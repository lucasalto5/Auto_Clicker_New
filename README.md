<h1 align="center">
  <br>
  <img src="icon.ico" alt="Auto Clicker Logo" width="120">
  <br>
  Elite Auto Clicker & Macro
  <br>
</h1>

<h4 align="center">Um Auto Clicker moderno, invisível e extremamente poderoso, com sistema de macro avançado e simulação humana.</h4>

<p align="center">
  <a href="#-recursos">Recursos</a> •
  <a href="#-instalação">Instalação</a> •
  <a href="#-como-usar">Como Usar</a> •
  <a href="#-sistema-multi-ponto">Multi-Ponto</a> •
  <a href="#-tecnologias">Tecnologias</a>
</p>

<p align="center">
  <img src="https://cdn.discordapp.com/attachments/1472212787622052055/1489144029265399838/Screenshot_2026-04-02_030637.png?ex=69cf58f3&is=69ce0773&hm=950c5aad943f3abc2a5a400ad9ef1e3206d5f728b402900d770ebba3905a1778&" alt="Interface Hotbar">
</p>

## ✨ Recursos

O **Elite Auto Clicker** não é apenas um clicador rápido. Ele foi projetado para ser flexível, com uma interface *overlay* (hotbar) que não atrapalha o seu uso no computador.

*   **⚡ Auto Clicker Extremamente Rápido**: Defina o CPS (Cliques por Segundo) limite ou deixe em 0 para velocidade máxima.
*   **🎯 Sistema de Alvo Triplo**:
    *   **Cursor**: Clica onde o mouse estiver.
    *   **Posição Fixa**: Captura uma coordenada (X, Y) na tela e clica sempre lá, não importa onde o seu mouse esteja.
    *   **Multi-Ponto**: Cria uma sequência de pontos na tela. O clicker viaja entre eles criando ciclos perfeitos de automação.
*   **🤖 Simulação Humana (Human Sim)**: 
    *   Adiciona tremores orgânicos (*jitter*) na posição do mouse.
    *   Varia milissegundos aleatoriamente entre os cliques para evitar detecção por sistemas anti-cheat/anti-macro.
*   **📼 Gravador de Macro Real**: Grave cliques do mouse e teclas do teclado para reproduzir sequências complexas perfeitamente.
*   **💾 Sistema de Presets**: Salve todas as suas configurações (velocidade, botões, posições, teclas de atalho) em perfis para carregar com um clique.
*   **🎨 Mais de 10 Temas Visuais**: De "Elite Glass" a "Cyber Neon", "Matrix" e "Kawaii". Personalize a aparência da hotbar.
*   **⌨️ Teclas de Atalho Customizáveis**: Altere as teclas de iniciar/parar e de gravação (padrão F6 e F10) direto pela interface.
*   **📌 Overlay "Sempre no Topo"**: Interface minimalista estilo *hotbar* que fica sobreposta aos seus jogos ou programas.

---

## 🚀 Instalação

A maneira mais fácil de usar o Elite Auto Clicker é baixando o executável pronto (Não requer instalação!).

1. Vá até a página de **[Releases](../../releases)** do projeto.
2. Baixe o arquivo `.zip` ou `.exe` da versão mais recente.
3. Extraia os arquivos em qualquer pasta do seu computador.
4. Execute o arquivo `autoclicker.exe`.
5. Pronto! A hotbar aparecerá no topo da sua tela.

> **Nota:** Se o Windows Defender exibir um alerta (SmartScreen), clique em "Mais informações" e depois em "Executar assim mesmo". Isso ocorre porque o executável é novo e ainda não possui um certificado de desenvolvedor pago.

---

## 🎮 Como Usar

### Auto Clicker Básico
1. Abra as configurações clicando no ícone de engrenagem <kbd>⚙️</kbd>.
2. Ajuste o **Intervalo** (em milissegundos) ou defina um **CPS Limit**.
3. Escolha qual botão do mouse (Esquerdo, Direito, Meio) e o tipo de clique (Simples, Duplo).
4. Pressione <kbd>F6</kbd> (ou a tecla que você configurou) para Iniciar/Parar.

### 📍 Sistema Multi-Ponto (Ciclos de Clique)
O modo Multi-Ponto permite que você crie uma "rota" de cliques na tela.
1. Nas configurações, em **Sistema de Alvo**, selecione `Multi-Ponto`.
2. Clique em `+ Add Ponto`.
3. Clique nos lugares da tela onde você quer que o programa clique (em ordem). 
4. Aparecerão bolinhas com efeito de vidro numeradas (1, 2, 3...) mostrando a ordem exata.
5. Clique em `Parar` no menu quando terminar de marcar.
6. Pressione <kbd>F6</kbd>. O mouse irá viajar entre os pontos e clicar em cada um sequencialmente.

### 🎥 Gravando uma Macro
1. Clique no ícone de gravação <kbd>⏺️</kbd> para abrir o painel de Macro.
2. Pressione <kbd>F10</kbd> para começar a gravar.
3. Faça as ações desejadas no seu computador (cliques e teclado).
4. Pressione <kbd>F10</kbd> novamente para parar a gravação.
5. Pressione <kbd>F6</kbd> para reproduzir tudo o que você gravou.

---

## 💻 Para Desenvolvedores (Build from Source)

Se você quiser modificar o código fonte e gerar seu próprio executável:

### Pré-requisitos
*   [Node.js](https://nodejs.org/) (versão 18+)
*   [Python](https://www.python.org/) (versão 3.9+)

### Passos para rodar em modo Desenvolvimento

1. Clone o repositório:
```bash
git clone https://github.com/SEU-USUARIO/elite-auto-clicker.git
cd elite-auto-clicker
```

2. Instale as dependências do Node.js:
```bash
npm install
```

3. Instale as dependências do Python:
```bash
pip install -r requirements.txt
```

4. Execute o aplicativo:
```bash
npm start
```

### Como gerar o Executável (.exe) Final

O projeto usa uma arquitetura dupla: Uma interface moderna em Electron (HTML/CSS/JS) e um "motor" robusto em Python (`pynput` / `pyautogui`) compilado via `pyinstaller`.

Para buildar, rode os comandos na ordem:

1. Compile o backend Python:
```bash
pyinstaller --noconsole --onefile backend.py
```

2. Gere o build do Electron:
```bash
npm run build
```

O aplicativo final estará disponível na pasta `release-builds/`.

---

## 🛠️ Tecnologias Utilizadas

*   **[Electron](https://www.electronjs.org/)**: Interface de usuário (UI) e controle de janelas (Overlay).
*   **[Node.js](https://nodejs.org/)**: Gerenciamento de processos e comunicação (IPC) via `child_process`.
*   **[Python](https://www.python.org/)**: Motor de automação rodando em background.
    *   `pyautogui`: Para controle e movimentação visual do mouse.
    *   `pynput`: Para escuta global de teclas (Hotkeys) e eventos de clique sem bloquear o sistema.

---

<p align="center">Feito com ☕ e 💻. Sinta-se à vontade para fazer um Fork e enviar Pull Requests!</p>
