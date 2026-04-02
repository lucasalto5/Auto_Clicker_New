const { ipcRenderer } = require('electron');

// State
let isActive = false;
let isPinned = true;
let isSettingsOpen = false;
let isMacroOpen = false;
let isRecording = false;
let currentMacroEvents = [];
let multiPoints = [];
let startTime = 0;
let statsInterval = null;

// DOM Elements
const toggleBtn = document.getElementById('toggle-btn');
const totalClicksEl = document.getElementById('total-clicks');
const currentCpsEl = document.getElementById('current-cps');
const pinBtn = document.getElementById('pin-btn');
const settingsBtn = document.getElementById('settings-btn');
const settingsPanel = document.getElementById('settings-panel');
const macroBtn = document.getElementById('macro-btn');
const macroPanel = document.getElementById('macro-panel');
const alwaysOnTopCheck = document.getElementById('always-on-top');
const themeSelector = document.getElementById('theme-selector');
const eventsCountEl = document.getElementById('events-count');
const macroLog = document.getElementById('macro-log');
const clearMacroBtn = document.getElementById('clear-macro');

// New Elements
const humanSimCheck = document.getElementById('human-simulation');
const hotkeyClickInput = document.getElementById('hotkey-click');
const hotkeyRecordInput = document.getElementById('hotkey-record');
const targetModeSelect = document.getElementById('target-mode');
const fixedPosControls = document.getElementById('fixed-pos-controls');
const multiPosControls = document.getElementById('multi-pos-controls');
const targetXInput = document.getElementById('target-x');
const targetYInput = document.getElementById('target-y');
const pickPosBtn = document.getElementById('pick-pos-btn');
const addPointBtn = document.getElementById('add-point-btn');
const stopAddPointBtn = document.getElementById('stop-add-point-btn');
const clearPointsBtn = document.getElementById('clear-points-btn');
const pointsListEl = document.getElementById('points-list');
const presetSelector = document.getElementById('preset-selector');
const presetNameInput = document.getElementById('preset-name');
const savePresetBtn = document.getElementById('save-preset-btn');
const deletePresetBtn = document.getElementById('delete-preset-btn');

// Window Controls
document.getElementById('min-btn').addEventListener('click', () => ipcRenderer.send('window-min'));
document.getElementById('close-btn').addEventListener('click', () => ipcRenderer.send('window-close'));

// Theme Management
themeSelector.addEventListener('change', (e) => {
    const theme = e.target.value;
    document.body.className = `theme-${theme}`;
    localStorage.setItem('selected-theme', theme);
});

// Target System Management
targetModeSelect.addEventListener('change', (e) => {
    const mode = e.target.value;
    fixedPosControls.classList.toggle('hidden', mode !== 'fixed');
    multiPosControls.classList.toggle('hidden', mode !== 'multi');
    updateConfig();
});

pickPosBtn.addEventListener('click', () => {
    // Auto-switch to Posição Fixa mode if not already
    if (targetModeSelect.value !== 'fixed') {
        targetModeSelect.value = 'fixed';
        fixedPosControls.classList.remove('hidden');
        multiPosControls.classList.add('hidden');
    }
    ipcRenderer.send('request-position-pick');
});

addPointBtn.addEventListener('click', () => {
    addPointBtn.classList.add('hidden');
    stopAddPointBtn.classList.remove('hidden');
    
    // Auto-switch to Multi-Ponto mode if not already
    if (targetModeSelect.value !== 'multi') {
        targetModeSelect.value = 'multi';
        fixedPosControls.classList.add('hidden');
        multiPosControls.classList.remove('hidden');
    }
    
    ipcRenderer.send('request-position-pick', 'multi');
});

stopAddPointBtn.addEventListener('click', () => {
    stopAddPointBtn.classList.add('hidden');
    addPointBtn.classList.remove('hidden');
    ipcRenderer.send('stop-position-pick');
});

clearPointsBtn.addEventListener('click', () => {
    multiPoints = [];
    renderPointsList();
    updateConfig();
});

function renderPointsList() {
    pointsListEl.innerHTML = multiPoints.map((p, i) => `
        <div style="display:flex; justify-content:space-between; margin-bottom:2px; background:rgba(255,255,255,0.1); padding:2px 5px; border-radius:3px;">
            <span>#${i+1}: ${p.x}, ${p.y}</span>
            <i class="fa-solid fa-xmark" style="cursor:pointer; color:#ff4444;" onclick="removePoint(${i})"></i>
        </div>
    `).join('');
    
    // Sync with overlay - Ensure this is ALWAYS called when points change
    console.log("Syncing points with overlay:", multiPoints);
    ipcRenderer.send('update-overlay-points', multiPoints);
}

window.removePoint = (index) => {
    multiPoints.splice(index, 1);
    renderPointsList();
    updateConfig();
};

ipcRenderer.on('point-removed-from-overlay', (event, index) => {
    removePoint(index);
});

// Preset Management
function loadPresets() {
    const presets = JSON.parse(localStorage.getItem('clicker-presets') || '{}');
    presetSelector.innerHTML = '<option value="">Selecione...</option>' + 
        Object.keys(presets).map(name => `<option value="${name}">${name}</option>`).join('');
}

savePresetBtn.addEventListener('click', () => {
    const name = presetNameInput.value.trim();
    if (!name) return alert('Digite um nome para o preset');
    
    const presets = JSON.parse(localStorage.getItem('clicker-presets') || '{}');
    presets[name] = {
        interval: document.getElementById('interval').value,
        random: document.getElementById('random').value,
        limit: document.getElementById('limit').value,
        cps_limit: document.getElementById('cps-limit').value,
        button: document.querySelector('#mouse-button .active').dataset.value,
        human_sim: humanSimCheck.checked,
        target_mode: targetModeSelect.value,
        target_x: targetXInput.value,
        target_y: targetYInput.value,
        multi_points: multiPoints,
        hotkey_click: hotkeyClickInput.value,
        hotkey_record: hotkeyRecordInput.value
    };
    
    localStorage.setItem('clicker-presets', JSON.stringify(presets));
    presetNameInput.value = '';
    loadPresets();
    presetSelector.value = name;
});

deletePresetBtn.addEventListener('click', () => {
    const name = presetSelector.value;
    if (!name) return;
    
    const presets = JSON.parse(localStorage.getItem('clicker-presets') || '{}');
    delete presets[name];
    localStorage.setItem('clicker-presets', JSON.stringify(presets));
    loadPresets();
});

presetSelector.addEventListener('change', (e) => {
    const name = e.target.value;
    if (!name) return;
    
    const presets = JSON.parse(localStorage.getItem('clicker-presets') || '{}');
    const p = presets[name];
    if (!p) return;
    
    document.getElementById('interval').value = p.interval;
    document.getElementById('random').value = p.random;
    document.getElementById('limit').value = p.limit;
    document.getElementById('cps-limit').value = p.cps_limit;
    
    document.querySelectorAll('#mouse-button .icon-btn').forEach(btn => {
        btn.classList.toggle('active', btn.dataset.value === p.button);
    });
    
    humanSimCheck.checked = p.human_sim;
    targetModeSelect.value = p.target_mode;
    targetXInput.value = p.target_x || 0;
    targetYInput.value = p.target_y || 0;
    multiPoints = p.multi_points || [];
    hotkeyClickInput.value = p.hotkey_click || 'F6';
    hotkeyRecordInput.value = p.hotkey_record || 'F10';
    
    document.getElementById('hotkey-click-label').innerText = hotkeyClickInput.value;
    document.getElementById('hotkey-record-label').innerText = hotkeyRecordInput.value;
    
    fixedPosControls.classList.toggle('hidden', p.target_mode !== 'fixed');
    multiPosControls.classList.toggle('hidden', p.target_mode !== 'multi');
    renderPointsList();
    updateConfig();
});

// Hotkey Display Updates
hotkeyClickInput.addEventListener('input', (e) => {
    document.getElementById('hotkey-click-label').innerText = e.target.value.toUpperCase();
    updateConfig();
});

hotkeyRecordInput.addEventListener('input', (e) => {
    document.getElementById('hotkey-record-label').innerText = e.target.value.toUpperCase();
    updateConfig();
});

// Load saved theme
const savedTheme = localStorage.getItem('selected-theme') || 'elite';
themeSelector.value = savedTheme;
document.body.className = `theme-${savedTheme}`;

// Pin Button
pinBtn.addEventListener('click', () => {
    isPinned = !isPinned;
    pinBtn.classList.toggle('active', isPinned);
    alwaysOnTopCheck.checked = isPinned;
    ipcRenderer.send('set-always-on-top', isPinned);
});

alwaysOnTopCheck.addEventListener('change', (e) => {
    isPinned = e.target.checked;
    pinBtn.classList.toggle('active', isPinned);
    ipcRenderer.send('set-always-on-top', isPinned);
});

// Settings Panel Toggle
settingsBtn.addEventListener('click', () => {
    isSettingsOpen = !isSettingsOpen;
    isMacroOpen = false; // Close macro if open
    macroPanel.classList.add('hidden');
    macroBtn.classList.remove('active');

    settingsBtn.classList.toggle('active', isSettingsOpen);
    settingsPanel.classList.toggle('hidden', !isSettingsOpen);
    
    updateWindowSize();
});

// Macro Panel Toggle
macroBtn.addEventListener('click', () => {
    isMacroOpen = !isMacroOpen;
    isSettingsOpen = false; // Close settings if open
    settingsPanel.classList.add('hidden');
    settingsBtn.classList.remove('active');

    macroBtn.classList.toggle('active', isMacroOpen);
    macroPanel.classList.toggle('hidden', !isMacroOpen);
    
    updateWindowSize();
});

function updateWindowSize() {
    if (isSettingsOpen || isMacroOpen) {
        ipcRenderer.send('resize-window', { width: 1000, height: 700 });
    } else {
        ipcRenderer.send('resize-window', { width: 1000, height: 120 });
    }
}

// Mouse Button Toggles
document.querySelectorAll('#mouse-button .icon-btn').forEach(btn => {
    btn.addEventListener('click', () => {
        document.querySelectorAll('#mouse-button .icon-btn').forEach(b => b.classList.remove('active'));
        btn.classList.add('active');
        updateConfig();
    });
});

// Settings & Inputs
document.querySelectorAll('input, select').forEach(input => {
    if (input.id === 'preset-name' || input.id === 'preset-selector') return;
    input.addEventListener('change', updateConfig);
    input.addEventListener('input', updateConfig);
});

function updateConfig() {
    const config = {
        interval: parseInt(document.getElementById('interval').value) || 100,
        random: parseInt(document.getElementById('random').value) || 0,
        limit: parseInt(document.getElementById('limit').value) || 0,
        cps_limit: parseInt(document.getElementById('cps-limit').value) || 0,
        button: document.querySelector('#mouse-button .active').dataset.value,
        type: 'single',
        capture_keyboard: true,
        macro_events: currentMacroEvents,
        human_sim: humanSimCheck.checked,
        target_mode: targetModeSelect.value,
        target_x: parseInt(targetXInput.value) || 0,
        target_y: parseInt(targetYInput.value) || 0,
        multi_points: multiPoints,
        hotkey_click: hotkeyClickInput.value || 'F6',
        hotkey_record: hotkeyRecordInput.value || 'F10',
        app_bounds: {
            x: window.screenX,
            y: window.screenY,
            width: window.innerWidth,
            height: window.innerHeight
        }
    };
    ipcRenderer.send('update-config', config);
}

// Action Button
toggleBtn.addEventListener('click', () => {
    // Evita que o primeiro clique automático (que acontece na posição do mouse)
    // acione o botão de parar imediatamente se o mouse ainda estiver em cima.
    toggleBtn.style.pointerEvents = 'none';
    setTimeout(() => {
        toggleBtn.style.pointerEvents = 'auto';
    }, 500);

    if (!isActive) {
        ipcRenderer.send('start-clicking');
    } else {
        ipcRenderer.send('stop-clicking');
    }
});

// Macro Log Helper
function addLog(msg) {
    macroLog.innerText = msg;
}

clearMacroBtn.addEventListener('click', () => {
    currentMacroEvents = [];
    eventsCountEl.innerText = '0';
    addLog('Memória limpa.');
    updateConfig();
});

// Stats Management
function startStats() {
    startTime = Date.now();
    totalClicksEl.innerText = '0';
    statsInterval = setInterval(() => {
        const elapsed = (Date.now() - startTime) / 1000;
        if (elapsed <= 0) return;
        
        const total = parseInt(totalClicksEl.innerText);
        currentCpsEl.innerText = (total / elapsed).toFixed(1);
    }, 500);
}

function stopStats() {
    clearInterval(statsInterval);
}

// IPC Messages
ipcRenderer.on('python-message', (event, message) => {
    if (message.type === 'status') {
        if (message.value === 'running') {
            isActive = true;
            toggleBtn.classList.add('active');
            toggleBtn.innerHTML = '<i class="fa-solid fa-stop"></i>';
            startStats();
        } else if (message.value === 'stopped') {
            isActive = false;
            isRecording = false;
            toggleBtn.classList.remove('active');
            toggleBtn.innerHTML = '<i class="fa-solid fa-play"></i>';
            macroPanel.classList.remove('recording');
            stopStats();
        } else if (message.value === 'recording') {
            isRecording = true;
            macroPanel.classList.add('recording');
            addLog('Gravando...');
        }
    } else if (message.type === 'click_update') {
        totalClicksEl.innerText = message.value;
    } else if (message.type === 'macro_recorded') {
        currentMacroEvents = message.value;
        eventsCountEl.innerText = currentMacroEvents.length;
        addLog(`Gravado: ${currentMacroEvents.length} ações`);
        updateConfig();
    } else if (message.type === 'position-picked') {
        targetXInput.value = message.value.x;
        targetYInput.value = message.value.y;
        updateConfig();
    } else if (message.type === 'multi-position-picked') {
        multiPoints.push(message.value);
        renderPointsList();
        updateConfig();
    }
});

// Initial Config
loadPresets();
updateConfig();

// Garante que o estado inicial de Always on Top seja aplicado ao iniciar
ipcRenderer.send('set-always-on-top', isPinned);
