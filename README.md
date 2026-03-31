<p align="center">
  <a>
    <img width="400" height="200" alt="image" src="https://github.com/user-attachments/assets/a207c771-dd0d-4065-ba3e-6831dd3f634f" />

  </a>
</p>

<h1 align="center">PDFX Compressor - Compressor de PDF Offline | Desenvolvido em Python</h1>

<p align="center">
  <img alt="Python" src="https://img.shields.io/badge/-Python-3776AB?style=flat-square&logo=python&logoColor=white" />
  <img alt="Tkinter" src="https://img.shields.io/badge/-Tkinter-FF6F00?style=flat-square&logo=python&logoColor=white" />
  <img alt="Ghostscript" src="https://img.shields.io/badge/-Ghostscript-7C6FFF?style=flat-square&logo=adobeacrobatreader&logoColor=white" />
  <img alt="Windows" src="https://img.shields.io/badge/-Windows-0078D6?style=flat-square&logo=windows&logoColor=white" />
  <img alt="PyInstaller" src="https://img.shields.io/badge/-PyInstaller-2E2E45?style=flat-square&logo=python&logoColor=white" />
  <img alt="Inno Setup" src="https://img.shields.io/badge/-Inno%20Setup-264DE4?style=flat-square&logo=windowsterminal&logoColor=white" />
</p>

<br>

### v1.0.0:
Release inicial do **PDFX Compressor**

---

## 🧠 Sobre o PDFX Compressor

<p align="center">
O PDFX Compressor é uma aplicação desktop <strong>100% offline</strong> para compressão de arquivos PDF, desenvolvida em Python com interface gráfica Tkinter.
Foi criada para reduzir o tamanho de PDFs de forma rápida e sem depender de serviços externos, servidores ou conexão com a internet.

<br><br> Com uma interface moderna em tema escuro, o PDFX entrega uma experiência visual limpa e profissional, pensada para uso corporativo e distribuição em múltiplas máquinas via instalador Windows silencioso.
</p>

---
<p align="center">
<img width="600" alt="image" src="https://github.com/user-attachments/assets/ee90194c-392e-41b9-a530-b91e14561080" />
</p>

## ⚙️ Funcionalidades

### 🗂️ Seleção de Arquivo

O PDFX oferece duas formas de selecionar o PDF:

- **Drag & Drop** — arraste o arquivo diretamente para a área indicada
- **Clique para selecionar** — abre o explorador de arquivos nativo do Windows

Após a seleção, o app exibe imediatamente o nome e o tamanho original do arquivo.

---

### 📉 Compressão de PDF

O motor de compressão utiliza o **Ghostscript** com parâmetros otimizados para máxima redução de tamanho:

- Redução de resolução de imagens coloridas e em tons de cinza para **100 DPI**
- Remoção de imagens duplicadas dentro do PDF
- Compressão e subset de fontes embutidas
- Compatibilidade com **Acrobat 5+** (PDF 1.4)
- Processamento em **thread separada** para manter a interface responsiva
- Barra de progresso animada em tempo real

O arquivo comprimido é salvo automaticamente em `Downloads` do usuário com o nome `PDF_OTIMIZADO.pdf`.

---

### 📊 Comparativo de Tamanho

Após a compressão, o app exibe lado a lado:

- 📁 Tamanho original
- ✅ Tamanho após compressão

---

### 🔍 Verificação Automática do Ghostscript

Na inicialização, o PDFX detecta automaticamente o Ghostscript instalado no sistema via:

1. Leitura do **Registro do Windows** (`winreg`)
2. Varredura via `glob` em `Program Files`

Caso o GS não seja encontrado, o app exibe um alerta imediato e bloqueia a compressão com uma mensagem orientando a instalação.

O status do GS é exibido permanentemente na sidebar:

- 🟢 `◉ GS: gswin64c.exe` — encontrado e pronto
- 🔴 `◉ GS: não encontrado` — requer instalação

---

## 🖥️ Interface

A janela principal (820 × 596 px) é dividida em:

| Área | Conteúdo |
|---|---|
| **Sidebar** (230px) | Logo, menu, status do GS, badges do autor e versão |
| **Área principal** | Drop zone, informações do arquivo, barra de progresso e botão de ação |

Tema visual escuro com paleta personalizada — sem bordas do sistema operacional.

---

## 🚀 Distribuição — Instalador Windows

O PDFX foi desenvolvido para ser distribuído via **instalador Windows** gerado com Inno Setup.

O instalador:
- Instala o **Ghostscript silenciosamente** (sem janelas extras para o usuário)
- Copia o executável para `Program Files\PDFX Compressor`
- Cria atalhos no **Menu Iniciar** e na **Área de Trabalho**
- Registra o app em **Adicionar/Remover Programas**
- Após instalado, o app **não requer privilégios de administrador** para rodar

### Build local

```bash
# 1. Instalar dependências
pip install -r requirements.txt

# 2. Gerar o executável
pyinstaller --onefile --noconsole --manifest app.manifest --name PDFX_Compressor app.py

# 3. Gerar o instalador Windows
# Abra o installer.iss no Inno Setup e pressione F9
```

> O instalador final é gerado em `installer_output/PDFX_Compressor_Setup.exe`

---

## 🧰 Tecnologias Utilizadas

- **Backend / Lógica:** Python 3 + subprocess + threading
- **Interface:** Tkinter + tkinterdnd2 (drag & drop)
- **Motor de compressão:** Ghostscript (GPL)
- **Empacotamento:** PyInstaller
- **Instalador:** Inno Setup 6

---

## 📋 Requisitos do Sistema

| Requisito | Especificação |
|---|---|
| Sistema Operacional | Windows 10 / 11 (64 bits) |
| Ghostscript | 10.x x64 (instalado via installer) |
| Permissões | Usuário padrão (sem admin após instalação) |
| Conexão à Internet | ❌ Não necessária |

---

## 📁 Estrutura do Projeto

```
PDF_COMPRESS/
├── app.py                  # Código-fonte principal
├── app.manifest            # Manifest Windows (sem elevação)
├── installer.iss           # Script do instalador Inno Setup
├── requirements.txt        # Dependências Python
└── README.md
```

> ⚠️ As pastas `dist/`, `build/`, `venv/` e `gs_installer/` são ignoradas pelo `.gitignore`.
> O instalador final é disponibilizado via **GitHub Releases**.

---

## 🧑‍💻 Autor

Gabriel Nicolas — Analista de Software
<br>Desenvolvido com ❤️ e Python para otimizar o dia a dia corporativo.

[![GitHub](https://img.shields.io/badge/-Nik0lax-24292E?style=flat-square&logo=github&logoColor=white)](https://github.com/Nik0lax/)
[![LinkedIn](https://img.shields.io/badge/-gabrielnikolax-0A66C2?style=flat-square&logo=linkedin&logoColor=white)](https://www.linkedin.com/in/gabrielnikolax/)

# pdfx_compressor
Executável Windows para comprimir PDF Offline. Desenvolvido em Python

