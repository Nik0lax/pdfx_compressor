import tkinter as tk
from tkinter import filedialog
import webbrowser
try:
    from tkinterdnd2 import DND_FILES, TkinterDnD
    BASE_CLASS = TkinterDnD.Tk
    HAS_DND = True
except ImportError:
    BASE_CLASS = tk.Tk
    HAS_DND = False

import subprocess
import os
import threading
import time
import sys

# ─── Paleta ────────────────────────────────────────
BG_MAIN   = "#16161E"
BG_SIDE   = "#1C1C28"
BG_CARD   = "#1C1C28"
BG_ACTIVE = "#252538"
BORDER    = "#2E2E45"
TEXT_PRI  = "#E8E8F0"
TEXT_SEC  = "#8A8AA8"
TEXT_DIM  = "#555570"
ACCENT    = "#7C6FFF"
ACCENT_HV = "#9B90FF"
SUCCESS   = "#2DD4A0"
ERROR     = "#FF5577"
TITLE_H   = 36

DESKTOP = os.path.join(os.path.expanduser("~"), "Downloads")


# ─────────────────────────────────────────────────────
# DIALOG CUSTOMIZADO
# ─────────────────────────────────────────────────────
class ThemedDialog(tk.Toplevel):
    def __init__(self, master, kind="info", title="", message=""):
        super().__init__(master)
        self.overrideredirect(True)
        self.configure(bg=BORDER)
        self.resizable(False, False)
        self.grab_set()
        self.focus_force()

        icon_map  = {"info": ("◈", ACCENT), "error": ("✕", ERROR), "warn": ("⚠", "#FFB347")}
        icon, clr = icon_map.get(kind, ("◈", ACCENT))

        inner = tk.Frame(self, bg=BG_CARD)
        inner.pack(fill="both", expand=True, padx=1, pady=1)

        tbar = tk.Frame(inner, bg="#111118", height=32)
        tbar.pack(fill="x")
        tbar.pack_propagate(False)
        tk.Label(tbar, text=f"{icon}  {title}", font=("Courier New", 8, "bold"),
                 bg="#111118", fg=TEXT_SEC).pack(side="left", padx=12)
        tbar.bind("<ButtonPress-1>", self._drag_start)
        tbar.bind("<B1-Motion>",     self._drag_move)

        tk.Frame(inner, bg=BORDER, height=1).pack(fill="x")

        body = tk.Frame(inner, bg=BG_CARD, padx=30, pady=20)
        body.pack(fill="both", expand=True)

        tk.Label(body, text=icon, font=("Courier New", 28, "bold"),
                 bg=BG_CARD, fg=clr).pack()
        tk.Label(body, text=message, font=("Courier New", 9),
                 bg=BG_CARD, fg=TEXT_PRI, wraplength=320, justify="center").pack(pady=(10, 20))

        ok_c = tk.Canvas(body, bg=BG_CARD, width=120, height=36, highlightthickness=0, cursor="hand2")
        ok_c.pack()
        self._draw_ok(ok_c, ACCENT)
        ok_c.bind("<Button-1>", lambda e: self.destroy())
        ok_c.bind("<Enter>",    lambda e: self._draw_ok(ok_c, ACCENT_HV))
        ok_c.bind("<Leave>",    lambda e: self._draw_ok(ok_c, ACCENT))

        self._center(master)

    def _draw_ok(self, c, color):
        c.delete("all")
        c.create_rectangle(0, 0, 120, 36, fill=color, outline="")
        c.create_text(60, 18, text="OK", font=("Courier New", 9, "bold"), fill="white")

    def _center(self, master):
        self.update_idletasks()
        x = master.winfo_x() + (master.winfo_width()  - self.winfo_width())  // 2
        y = master.winfo_y() + (master.winfo_height() - self.winfo_height()) // 2
        self.geometry(f"+{x}+{y}")

    def _drag_start(self, e):
        self._dx = e.x_root - self.winfo_x()
        self._dy = e.y_root - self.winfo_y()

    def _drag_move(self, e):
        self.geometry(f"+{e.x_root - self._dx}+{e.y_root - self._dy}")


# ─────────────────────────────────────────────────────
# APP PRINCIPAL
# ─────────────────────────────────────────────────────
class CompressorApp(BASE_CLASS):
    def __init__(self):
        super().__init__()

        self.overrideredirect(True)
        self.geometry("820x596")
        self.configure(bg=BG_MAIN)

        self._drag_x = 0
        self._drag_y = 0
        self.file_path = None
        self._anim_running = False
        self._last_progress = 0

        # ── Resolve o caminho do GS uma única vez na inicialização ──
        self._gs_path = None
        try:
            self._gs_path = self.get_gs_path()
        except FileNotFoundError as e:
            # Exibe o aviso após a janela estar visível
            self.after(300, lambda msg=str(e): ThemedDialog(
                self, kind="error",
                title="Ghostscript não encontrado",
                message=msg
            ))

        self._build()
        self.after(50, lambda: self._draw_drop_zone(hover=False))

    # ─────────────────────────────────────────
    # TITLEBAR CUSTOMIZADA
    # ─────────────────────────────────────────
    def _build_titlebar(self, parent):
        bar = tk.Frame(parent, bg="#111118", height=TITLE_H)
        bar.pack(fill="x", side="top")
        bar.pack_propagate(False)

        tk.Label(bar, text="◈  PDFX Compressor",
                 font=("Courier New", 9, "bold"),
                 bg="#111118", fg=TEXT_SEC).pack(side="left", padx=14)

        btn_frame = tk.Frame(bar, bg="#111118")
        btn_frame.pack(side="right", padx=6)

        self._mk_wm_btn(btn_frame, "–", "#444466", TEXT_PRI, lambda: self.iconify())
        self._mk_wm_btn(btn_frame, "✕", "#FF5577", "#FFFFFF", lambda: self.destroy())

        bar.bind("<ButtonPress-1>", self._drag_start)
        bar.bind("<B1-Motion>",     self._drag_move)

        tk.Frame(parent, bg=BORDER, height=1).pack(fill="x")

    def _mk_wm_btn(self, parent, text, bg_hover, fg, cmd):
        btn = tk.Label(parent, text=text, font=("Courier New", 10, "bold"),
                       bg="#111118", fg=TEXT_DIM, width=3, cursor="hand2")
        btn.pack(side="left", padx=2, pady=6)
        btn.bind("<Enter>",    lambda e, b=btn, c=bg_hover: b.config(bg=c, fg=fg))
        btn.bind("<Leave>",    lambda e, b=btn: b.config(bg="#111118", fg=TEXT_DIM))
        btn.bind("<Button-1>", lambda e: cmd())

    def _drag_start(self, e):
        self._drag_x = e.x_root - self.winfo_x()
        self._drag_y = e.y_root - self.winfo_y()

    def _drag_move(self, e):
        self.geometry(f"+{e.x_root - self._drag_x}+{e.y_root - self._drag_y}")

    # ─────────────────────────────────────────
    # BADGES (GitHub / LinkedIn)
    # ─────────────────────────────────────────
    def _make_badge(self, parent, icon, label, bg_icon, bg_label, url):
        frame = tk.Frame(parent, bg=BG_SIDE, cursor="hand2")
        frame.pack(side="left", padx=(0, 6))

        if icon == "gh":
            ic = tk.Label(frame,
                        text=" Git ",
                        font=("Courier New", 7, "bold"),
                        bg=bg_icon,
                        fg="#FFFFFF",
                        cursor="hand2")
            ic.pack(side="left", ipady=3)
        else:
            ic = tk.Label(frame, text=" in ",
                          font=("Courier New", 7, "bold"),
                          bg=bg_icon, fg="#FFFFFF", cursor="hand2", height=1)
            ic.pack(side="left", ipady=3)

        lb = tk.Label(frame, text=f" {label} ",
                      font=("Courier New", 7),
                      bg=bg_label, fg="#DDDDEE", cursor="hand2", height=1)
        lb.pack(side="left", ipady=3)

        def on_enter(e):
            ic_b = self._brighten(bg_icon)
            ic.config(bg=ic_b)
            lb.config(bg=self._brighten(bg_label))

        def on_leave(e):
            ic.config(bg=bg_icon)
            lb.config(bg=bg_label)

        def on_click(e):
            webbrowser.open(url)

        for w in (frame, ic, lb):
            w.bind("<Enter>",    on_enter)
            w.bind("<Leave>",    on_leave)
            w.bind("<Button-1>", on_click)

    @staticmethod
    def _brighten(hex_color):
        h = hex_color.lstrip("#")
        r, g, b = int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)
        return f"#{min(255,r+30):02X}{min(255,g+30):02X}{min(255,b+30):02X}"

    # ─────────────────────────────────────────
    # BUILD PRINCIPAL
    # ─────────────────────────────────────────
    def _build(self):
        outer = tk.Frame(self, bg=BORDER, padx=1, pady=1)
        outer.pack(fill="both", expand=True)

        inner = tk.Frame(outer, bg=BG_MAIN)
        inner.pack(fill="both", expand=True)

        self._build_titlebar(inner)

        body = tk.Frame(inner, bg=BG_MAIN)
        body.pack(fill="both", expand=True)

        # ── Sidebar ──────────────────────────
        left = tk.Frame(body, bg=BG_SIDE, width=230)
        left.pack(side="left", fill="y")
        left.pack_propagate(False)

        logo_frame = tk.Frame(left, bg=BG_SIDE)
        logo_frame.pack(fill="x", padx=18, pady=(26, 0))
        tk.Label(logo_frame, text="◈", font=("Courier New", 20, "bold"),
                 bg=BG_SIDE, fg=ACCENT).pack(side="left")
        tk.Label(logo_frame, text="  PDFX", font=("Courier New", 15, "bold"),
                 bg=BG_SIDE, fg=TEXT_PRI).pack(side="left")

        tk.Label(left, text="C O M P R E S S O R", font=("Courier New", 7, "bold"),
                 bg=BG_SIDE, fg=TEXT_DIM).pack(anchor="w", padx=18, pady=(2, 0))

        tk.Frame(left, bg=BORDER, height=1).pack(fill="x", padx=18, pady=18)

        row = tk.Frame(left, bg=BG_ACTIVE, cursor="hand2")
        row.pack(fill="x", padx=8, pady=2)
        tk.Frame(row, bg=ACCENT, width=3).pack(side="left", fill="y")
        tk.Label(row, text="▣  Comprimir PDF", font=("Courier New", 9),
                 bg=BG_ACTIVE, fg=TEXT_PRI, pady=11, padx=12).pack(side="left")

        # ── Indicador de status do GS na sidebar ──
        self.lbl_gs_status = tk.Label(
            left,
            text="",  # preenchido abaixo
            font=("Courier New", 7),
            bg=BG_SIDE,
            anchor="w",
            padx=18
        )
        self.lbl_gs_status.pack(fill="x", pady=(8, 0))
        self._update_gs_status_label()

        # ── Rodapé da sidebar ─────────────────
        tk.Frame(left, bg=BORDER, height=1).pack(fill="x", padx=18, pady=(18, 8), side="bottom")

        badges_frame = tk.Frame(left, bg=BG_SIDE)
        badges_frame.pack(side="bottom", fill="x", padx=14, pady=(0, 6))

        self._make_badge(badges_frame,
                         icon="gh", label="Nik0lax",
                         bg_icon="#24292E", bg_label="#2D333B",
                         url="https://github.com/Nik0lax/")

        self._make_badge(badges_frame,
                         icon="in", label="gabrielnikolax",
                         bg_icon="#0A66C2", bg_label="#0D5FA8",
                         url="https://www.linkedin.com/in/gabrielnikolax/")

        tk.Label(left, text="v1.0.0  •  by Gabriel Nicolas", font=("Courier New", 7),
                 bg=BG_SIDE, fg=TEXT_DIM).pack(side="bottom", pady=(0, 4))

        # ── Conteúdo principal ────────────────
        right = tk.Frame(body, bg=BG_MAIN)
        right.pack(side="right", fill="both", expand=True)

        topbar = tk.Frame(right, bg=BG_MAIN)
        topbar.pack(fill="x", padx=28, pady=(22, 0))
        tk.Label(topbar, text="Comprimir PDF", font=("Courier New", 13, "bold"),
                 bg=BG_MAIN, fg=TEXT_PRI).pack(side="left")
        tk.Label(topbar, text="Compressor Offline",
                 font=("Courier New", 8), bg=BG_MAIN, fg=TEXT_DIM).pack(side="right")

        # Drop zone
        self.drop_canvas = tk.Canvas(right, bg=BG_CARD, highlightthickness=0,
                                     height=148, cursor="hand2")
        self.drop_canvas.pack(fill="x", padx=28, pady=18)
        self.drop_canvas.bind("<Button-1>",  lambda e: self.select_file())
        self.drop_canvas.bind("<Enter>",     self._drop_hover_on)
        self.drop_canvas.bind("<Leave>",     self._drop_hover_off)
        self.drop_canvas.bind("<Configure>", lambda e: self._draw_drop_zone(hover=False))

        if HAS_DND:
            self.drop_canvas.drop_target_register(DND_FILES)
            self.drop_canvas.dnd_bind("<<Drop>>", self._on_drop)

        # Card info
        self.info_frame = tk.Frame(right, bg=BG_CARD)
        self.info_frame.pack(fill="x", padx=28)

        self.lbl_filename = tk.Label(
            self.info_frame, text="Nenhum arquivo selecionado",
            font=("Courier New", 9, "bold"),
            bg=BG_CARD, fg=TEXT_SEC, pady=10, padx=14, anchor="w")
        self.lbl_filename.pack(fill="x")

        sizes_row = tk.Frame(self.info_frame, bg=BG_CARD)
        sizes_row.pack(fill="x", padx=14, pady=(0, 10))

        self.lbl_before = tk.Label(sizes_row, text="", font=("Courier New", 8),
                                   bg=BG_CARD, fg=TEXT_SEC)
        self.lbl_before.pack(side="left")
        self.lbl_arrow = tk.Label(sizes_row, text="", font=("Courier New", 8),
                                  bg=BG_CARD, fg=ACCENT)
        self.lbl_arrow.pack(side="left", padx=6)
        self.lbl_after = tk.Label(sizes_row, text="", font=("Courier New", 8),
                                  bg=BG_CARD, fg=SUCCESS)
        self.lbl_after.pack(side="left")

        # Barra de progresso
        prog_outer = tk.Frame(right, bg=BG_MAIN)
        prog_outer.pack(fill="x", padx=28, pady=(14, 0))
        self.prog_canvas = tk.Canvas(prog_outer, bg=BG_MAIN, height=6, highlightthickness=0)
        self.prog_canvas.pack(fill="x")
        self.prog_canvas.bind("<Configure>", lambda e: self._draw_progress(0))

        status_row = tk.Frame(right, bg=BG_MAIN)
        status_row.pack(fill="x", padx=28, pady=(5, 0))
        self.lbl_status = tk.Label(status_row, text="Aguardando arquivo...",
                                   font=("Courier New", 8), bg=BG_MAIN, fg=TEXT_DIM)
        self.lbl_status.pack(side="left")
        self.lbl_pct = tk.Label(status_row, text="",
                                font=("Courier New", 8, "bold"), bg=BG_MAIN, fg=ACCENT)
        self.lbl_pct.pack(side="right")

        # Botão
        self.btn = tk.Canvas(right, bg=BG_MAIN, width=210, height=44,
                             highlightthickness=0, cursor="hand2")
        self.btn.pack(pady=18)
        self._draw_btn("COMPRIMIR AGORA", ACCENT)
        self.btn.bind("<Button-1>", lambda e: self.start())
        self.btn.bind("<Enter>",    lambda e: self._draw_btn("COMPRIMIR AGORA", ACCENT_HV))
        self.btn.bind("<Leave>",    lambda e: self._draw_btn("COMPRIMIR AGORA", ACCENT))

    # ─────────────────────────────────────────
    # STATUS DO GS NA SIDEBAR
    # ─────────────────────────────────────────
    def _update_gs_status_label(self):
        if self._gs_path:
            nome = os.path.basename(self._gs_path)
            self.lbl_gs_status.config(
                text=f"◉  GS: {nome}",
                fg=SUCCESS
            )
        else:
            self.lbl_gs_status.config(
                text="◉  GS: não encontrado",
                fg=ERROR
            )

    # ─────────────────────────────────────────
    # DRAW HELPERS
    # ─────────────────────────────────────────
    def _draw_drop_zone(self, hover=False):
        c = self.drop_canvas
        c.delete("all")
        w = c.winfo_width()
        if w < 10:
            return
        h = 148
        c.create_rectangle(2, 2, w - 2, h - 2,
                            outline=ACCENT if hover else BORDER,
                            dash=(6, 4),
                            fill="#20203A" if hover else BG_CARD,
                            width=2)
        c.create_text(w // 2, 48, text="⬆", font=("Courier New", 20),
                      fill=ACCENT if hover else "#3A3A58")
        c.create_text(w // 2, 84,
                      text="Arraste o PDF aqui   ou   clique para selecionar",
                      font=("Courier New", 9),
                      fill=TEXT_SEC if hover else "#5A5A7A")
        c.create_text(w // 2, 112, text="Suporta arquivos .pdf",
                      font=("Courier New", 7), fill=TEXT_DIM)

    def _draw_btn(self, text, color):
        c = self.btn
        c.delete("all")
        c.create_rectangle(0, 0, 210, 44, fill=color, outline="")
        c.create_text(105, 22, text=text, font=("Courier New", 9, "bold"), fill="white")

    def _draw_progress(self, pct):
        c = self.prog_canvas
        c.delete("all")
        w = c.winfo_width()
        if w < 10:
            return
        c.create_rectangle(0, 0, w, 6, fill=BORDER, outline="")
        if pct > 0:
            bar_w = int(w * pct / 100)
            c.create_rectangle(0, 0, bar_w, 6, fill=ACCENT, outline="")
            c.create_rectangle(max(0, bar_w - 24), 0, bar_w, 6, fill=ACCENT_HV, outline="")

    # ─────────────────────────────────────────
    # EVENTOS
    # ─────────────────────────────────────────
    def _drop_hover_on(self, e=None):
        self._draw_drop_zone(hover=True)

    def _drop_hover_off(self, e=None):
        self._draw_drop_zone(hover=False)

    def _on_drop(self, event):
        files = self.tk.splitlist(event.data)
        if files:
            self.load_file(files[0])

    # ─────────────────────────────────────────
    # ARQUIVO
    # ─────────────────────────────────────────
    def select_file(self):
        path = filedialog.askopenfilename(filetypes=[("PDF Files", "*.pdf")])
        if path:
            self.load_file(path)

    def load_file(self, path):
        self.file_path = path
        size  = os.path.getsize(path) / (1024 * 1024)
        name  = os.path.basename(path)
        short = name[:38] + "…" if len(name) > 40 else name

        self.lbl_filename.config(text=f"  ◈  {short}", fg=TEXT_PRI)
        self.lbl_before.config(text=f"Original: {size:.2f} MB")
        self.lbl_arrow.config(text="")
        self.lbl_after.config(text="")
        self.lbl_status.config(text="Arquivo carregado. Pronto para comprimir.", fg=TEXT_SEC)
        self._draw_drop_zone(hover=False)
        self._draw_progress(0)
        self.lbl_pct.config(text="")

    # ─────────────────────────────────────────
    # PROCESSO
    # ─────────────────────────────────────────
    def start(self):
        # ── Bloqueia se o GS não foi encontrado ──
        if not self._gs_path:
            ThemedDialog(self, kind="error",
                         title="Ghostscript não encontrado",
                         message="Instale o Ghostscript e reinicie o aplicativo.\n\nghostscript.com/download")
            return

        if not self.file_path:
            ThemedDialog(self, kind="warn", title="Atenção",
                         message="Selecione um arquivo PDF primeiro.")
            return

        output = os.path.join(DESKTOP, "PDF_OTIMIZADO.pdf")
        self._anim_running = True
        self._last_progress = 0
        self.lbl_status.config(text="Processando…", fg=ACCENT)
        self.lbl_pct.config(text="0%")
        self._draw_btn("PROCESSANDO…", "#2E2E45")
        self.btn.unbind("<Button-1>")
        self.btn.unbind("<Enter>")
        self.btn.unbind("<Leave>")

        threading.Thread(target=self._run_gs,  args=(output,), daemon=True).start()
        threading.Thread(target=self._animate, daemon=True).start()

    def _animate(self):
        p = 0
        while self._anim_running and p < 90:
            time.sleep(0.08)
            p += (90 - p) / 20
            self.after(0, lambda v=p: self._set_progress(v))

    def _set_progress(self, val):
        self._last_progress = val
        self._draw_progress(val)
        self.lbl_pct.config(text=f"{int(val)}%")

    def _animate_to_100(self, p=None):
        if p is None:
            p = self._last_progress
        if p < 100:
            p = min(p + 2, 100)
            self._draw_progress(p)
            self.lbl_pct.config(text=f"{int(p)}%")
            self._last_progress = p
            self.after(20, lambda: self._animate_to_100(p))

    # ─────────────────────────────────────────
    # LOCALIZAÇÃO DO GHOSTSCRIPT
    # ─────────────────────────────────────────
    def get_gs_path(self):
        import winreg, glob

        # 1. Registro do Windows (instalação oficial)
        for root in (winreg.HKEY_LOCAL_MACHINE, winreg.HKEY_CURRENT_USER):
            for subkey in (
                r"SOFTWARE\Artifex\GPL Ghostscript",
                r"SOFTWARE\WOW6432Node\Artifex\GPL Ghostscript",
            ):
                try:
                    with winreg.OpenKey(root, subkey) as k:
                        i = 0
                        while True:
                            version = winreg.EnumKey(k, i)
                            with winreg.OpenKey(k, version) as vk:
                                dll_path = winreg.QueryValueEx(vk, "GS_DLL")[0]
                                gs_dir   = os.path.dirname(dll_path)
                                for f in os.listdir(gs_dir):
                                    if f.startswith("gswin64c") and f.endswith(".exe"):
                                        return os.path.join(gs_dir, f)
                            i += 1
                except (FileNotFoundError, OSError, WindowsError):
                    continue

        # 2. Glob em Program Files (qualquer versão)
        for pattern in [
            r"C:\Program Files\gs\gs*\bin\gswin64c.exe",
            r"C:\Program Files (x86)\gs\gs*\bin\gswin64c.exe",
        ]:
            results = sorted(glob.glob(pattern))
            if results:
                return results[-1]  # versão mais recente

        raise FileNotFoundError(
            "Ghostscript não encontrado.\n"
            "Instale em: ghostscript.com/download"
        )

    def _run_gs(self, output):
        # Usa o caminho já resolvido no __init__ — sem chamar get_gs_path() novamente
        cmd = [
            self._gs_path,
            "-sDEVICE=pdfwrite",
            "-dPDFSETTINGS=/screen",
            "-dNOPAUSE", "-dQUIET", "-dBATCH",
            "-dCompatibilityLevel=1.4",
            "-dColorImageDownsampleType=/Bicubic",
            "-dColorImageResolution=100",
            "-dDownsampleColorImages=true",
            "-dGrayImageDownsampleType=/Bicubic",
            "-dGrayImageResolution=100",
            "-dDownsampleGrayImages=true",
            "-dMonoImageDownsampleType=/Subsample",
            "-dMonoImageResolution=150",
            "-dDownsampleMonoImages=true",
            "-dDetectDuplicateImages=true",
            "-dCompressFonts=true",
            "-dSubsetFonts=true",
            "-dEmbedAllFonts=true",
            f"-sOutputFile={output}",
            self.file_path
        ]
        try:
            subprocess.run(cmd, check=True, creationflags=0x08000000)
            self._anim_running = False
            self.after(0, lambda: self._finish(output))
        except Exception as e:
            self._anim_running = False
            self.after(0, lambda err=str(e): self._error(err))

    def _finish(self, path):
        size = os.path.getsize(path) / (1024 * 1024)
        self._animate_to_100()
        self.after(500, lambda: self.lbl_pct.config(text="100%"))
        self.lbl_status.config(text="Concluído com sucesso!", fg=SUCCESS)
        self.lbl_arrow.config(text="→")
        self.lbl_after.config(text=f"Comprimido: {size:.2f} MB")

        self._draw_btn("COMPRIMIR NOVAMENTE", "#1A7A5A")
        self.btn.bind("<Button-1>", lambda e: self._reset())
        self.btn.bind("<Enter>",    lambda e: self._draw_btn("COMPRIMIR NOVAMENTE", "#22A876"))
        self.btn.bind("<Leave>",    lambda e: self._draw_btn("COMPRIMIR NOVAMENTE", "#1A7A5A"))

        ThemedDialog(self, kind="info", title="Concluído",
                     message=f"Arquivo salvo em Downloads:\n\nPDF_OTIMIZADO.pdf\n({size:.2f} MB)")

    def _error(self, msg):
        self.lbl_status.config(text="Erro ao processar.", fg=ERROR)
        self._draw_btn("TENTAR NOVAMENTE", ERROR)
        self.btn.bind("<Button-1>", lambda e: self.start())
        self.btn.bind("<Enter>",    lambda e: self._draw_btn("TENTAR NOVAMENTE", "#FF7799"))
        self.btn.bind("<Leave>",    lambda e: self._draw_btn("TENTAR NOVAMENTE", ERROR))
        ThemedDialog(self, kind="error", title="Erro", message=msg)

    def _reset(self):
        self.file_path = None
        self.lbl_filename.config(text="Nenhum arquivo selecionado", fg=TEXT_SEC)
        self.lbl_before.config(text="")
        self.lbl_arrow.config(text="")
        self.lbl_after.config(text="")
        self.lbl_status.config(text="Aguardando arquivo...", fg=TEXT_DIM)
        self.lbl_pct.config(text="")
        self._last_progress = 0
        self._draw_progress(0)
        self._draw_drop_zone(hover=False)
        self._draw_btn("COMPRIMIR AGORA", ACCENT)
        self.btn.bind("<Button-1>", lambda e: self.start())
        self.btn.bind("<Enter>",    lambda e: self._draw_btn("COMPRIMIR AGORA", ACCENT_HV))
        self.btn.bind("<Leave>",    lambda e: self._draw_btn("COMPRIMIR AGORA", ACCENT))


if __name__ == "__main__":
    app = CompressorApp()
    app.mainloop()