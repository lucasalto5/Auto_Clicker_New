import customtkinter as ctk
import pyautogui
import threading
import time
from pynput import keyboard, mouse
import sys
import json
import os
import random

# Configuração global do CustomTkinter
ctk.set_appearance_mode("light")

# Paleta Corporativa Minimalista
BG_COLOR = "#FFFFFF"          # Fundo Branco Puro
TEXT_MAIN = "#1A1A1A"         # Cinza Quase Preto (Elegante)
TEXT_MUTED = "#666666"        # Cinza Médio (Subtítulos)
RED_ACCENT = "#D32F2F"        # Vermelho Sólido Profissional
RED_HOVER = "#B71C1C"         # Vermelho Escuro Hover
INPUT_BG = "#F5F5F5"          # Fundo dos Inputs (Cinza Claro)
TAB_BG = "#EAEAEA"            # Fundo Abas Desativadas

PRESETS_FILE = "autoclicker_presets.json"

class AutoClickerApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("ROGERINHOXR")
        self.geometry("400x520")
        self.configure(fg_color=BG_COLOR)
        self.resizable(False, False)

        # Variáveis de Controle
        self.is_clicking = False
        self.is_recording = False
        self.click_thread = None
        self.hotkey_listener = None
        self.mouse_listener = None
        self.current_run_mode = None
        
        self.presets_data = {}
        self.macro_events = []
        self.record_start_time = 0
        self.last_move_time = 0
        
        # Variáveis de Interface
        self.interval_str = ctk.StringVar(value="100")
        self.random_str = ctk.StringVar(value="0")
        self.limit_str = ctk.StringVar(value="0")
        
        self.button_var = ctk.StringVar(value="Esquerdo")
        self.type_var = ctk.StringVar(value="Único")
        
        self.preset_name_var = ctk.StringVar(value="Meu Preset")
        self.selected_preset_var = ctk.StringVar(value="Selecione...")

        self.load_presets()
        self.setup_ui()
        self.start_hotkey_listener()

    def setup_ui(self):
        # Header Minimalista (Sem Emojis, Fonte Limpa)
        lbl_title = ctk.CTkLabel(self, text="ROGERINHOXR", font=("Helvetica", 22, "bold"), text_color=RED_ACCENT)
        lbl_title.pack(pady=(20, 0))
        lbl_sub = ctk.CTkLabel(self, text="AUTO CLICKER & MACRO", font=("Helvetica", 10, "bold"), text_color=TEXT_MUTED)
        lbl_sub.pack(pady=(0, 15))

        # Linha Divisória
        line = ctk.CTkFrame(self, fg_color="#E0E0E0", height=1, corner_radius=0)
        line.pack(fill="x", padx=20)

        # Abas Totalmente Quadradas (corner_radius=0)
        self.tabview = ctk.CTkTabview(
            self, fg_color=BG_COLOR, segmented_button_fg_color=TAB_BG,
            segmented_button_selected_color=RED_ACCENT, segmented_button_selected_hover_color=RED_HOVER,
            text_color=TEXT_MAIN, corner_radius=0, height=300
        )
        self.tabview.pack(fill="both", expand=True, padx=20, pady=10)
        
        # Nomes sem emojis para visual corporativo
        self.tab_clicker = self.tabview.add("CLICKER")
        self.tab_macro = self.tabview.add("MACRO")
        self.tab_presets = self.tabview.add("PRESETS")

        self.setup_clicker_tab()
        self.setup_macro_tab()
        self.setup_presets_tab()

        # Botão de Ação Centralizado (Quadrado, Fonte Clean)
        self.btn_toggle = ctk.CTkButton(
            self, text="INICIAR (F6)", font=("Helvetica", 14, "bold"),
            fg_color=RED_ACCENT, hover_color=RED_HOVER, text_color="#FFFFFF",
            corner_radius=0, height=45, command=self.toggle_clicker
        )
        self.btn_toggle.pack(fill="x", padx=20, pady=(15, 5))
        
        self.lbl_status = ctk.CTkLabel(self, text="STATUS: PARADO", font=("Helvetica", 10, "bold"), text_color=TEXT_MUTED)
        self.lbl_status.pack(side="bottom", pady=(0, 15))

    # Helpers de Layout (Tudo Quadrado: corner_radius=0)
    def create_input_row(self, parent, label_text, variable):
        frame = ctk.CTkFrame(parent, fg_color="transparent")
        frame.pack(fill="x", pady=5)
        lbl = ctk.CTkLabel(frame, text=label_text, font=("Helvetica", 12), text_color=TEXT_MAIN, width=110, anchor="w")
        lbl.pack(side="left")
        entry = ctk.CTkEntry(
            frame, textvariable=variable, font=("Helvetica", 12), height=30,
            fg_color=INPUT_BG, border_color="#CCCCCC", border_width=1,
            text_color=TEXT_MAIN, corner_radius=0
        )
        entry.pack(side="left", fill="x", expand=True)

    def create_segmented_row(self, parent, label_text, variable, values):
        frame = ctk.CTkFrame(parent, fg_color="transparent")
        frame.pack(fill="x", pady=5)
        lbl = ctk.CTkLabel(frame, text=label_text, font=("Helvetica", 12), text_color=TEXT_MAIN, width=110, anchor="w")
        lbl.pack(side="left")
        seg = ctk.CTkSegmentedButton(
            frame, values=values, variable=variable, height=30,
            selected_color=RED_ACCENT, selected_hover_color=RED_HOVER,
            unselected_color=INPUT_BG, unselected_hover_color="#E0E0E0",
            text_color=TEXT_MAIN, corner_radius=0
        )
        seg.pack(side="left", fill="x", expand=True)

    def setup_clicker_tab(self):
        ctk.CTkLabel(self.tab_clicker, text="TEMPO & LIMITES", font=("Helvetica", 10, "bold"), text_color=TEXT_MUTED).pack(anchor="w", pady=(5, 5))
        self.create_input_row(self.tab_clicker, "Intervalo (ms)", self.interval_str)
        self.create_input_row(self.tab_clicker, "Humanizer (+ms)", self.random_str)
        self.create_input_row(self.tab_clicker, "Limite (0 = ∞)", self.limit_str)
        
        ctk.CTkLabel(self.tab_clicker, text="CONFIGURAÇÃO MOUSE", font=("Helvetica", 10, "bold"), text_color=TEXT_MUTED).pack(anchor="w", pady=(15, 5))
        self.create_segmented_row(self.tab_clicker, "Botão", self.button_var, ["Esquerdo", "Direito", "Meio"])
        self.create_segmented_row(self.tab_clicker, "Tipo", self.type_var, ["Único", "Duplo"])

    def setup_macro_tab(self):
        f_center = ctk.CTkFrame(self.tab_macro, fg_color="transparent")
        f_center.pack(expand=True)
        
        lbl_inst = ctk.CTkLabel(
            f_center, 
            text="Pressione F10 para INICIAR a gravação.\nPressione F10 novamente para PARAR.", 
            font=("Helvetica", 12), text_color=TEXT_MAIN, justify="center"
        )
        lbl_inst.pack(pady=(0, 20))
        
        self.lbl_macro_status = ctk.CTkLabel(f_center, text="EVENTOS GRAVADOS: 0", font=("Helvetica", 14, "bold"), text_color=RED_ACCENT)
        self.lbl_macro_status.pack(pady=10)
        
        btn_clear = ctk.CTkButton(
            f_center, text="LIMPAR GRAVAÇÃO", width=140, height=32,
            fg_color="#E0E0E0", hover_color="#CCCCCC", text_color=TEXT_MAIN, 
            corner_radius=0, font=("Helvetica", 11, "bold"), command=self.clear_macro
        )
        btn_clear.pack(pady=10)

    def setup_presets_tab(self):
        # Salvar
        ctk.CTkLabel(self.tab_presets, text="SALVAR CONFIGURAÇÃO", font=("Helvetica", 10, "bold"), text_color=TEXT_MUTED).pack(anchor="w", pady=(5, 5))
        f_save = ctk.CTkFrame(self.tab_presets, fg_color="transparent")
        f_save.pack(fill="x", pady=2)
        ctk.CTkEntry(
            f_save, textvariable=self.preset_name_var, height=32, font=("Helvetica", 12),
            fg_color=INPUT_BG, border_color="#CCCCCC", border_width=1, corner_radius=0, text_color=TEXT_MAIN
        ).pack(side="left", fill="x", expand=True, padx=(0, 5))
        ctk.CTkButton(
            f_save, text="SALVAR", width=80, height=32, fg_color=RED_ACCENT, hover_color=RED_HOVER, 
            text_color="#FFFFFF", corner_radius=0, font=("Helvetica", 11, "bold"), command=self.save_preset
        ).pack(side="right")

        # Carregar
        ctk.CTkLabel(self.tab_presets, text="CARREGAR PRESET", font=("Helvetica", 10, "bold"), text_color=TEXT_MUTED).pack(anchor="w", pady=(20, 5))
        f_load = ctk.CTkFrame(self.tab_presets, fg_color="transparent")
        f_load.pack(fill="x", pady=2)
        self.opt_preset = ctk.CTkOptionMenu(
            f_load, variable=self.selected_preset_var, values=["Selecione..."], height=32, font=("Helvetica", 12),
            fg_color=INPUT_BG, button_color=RED_ACCENT, button_hover_color=RED_HOVER,
            text_color=TEXT_MAIN, dropdown_fg_color=BG_COLOR, dropdown_text_color=TEXT_MAIN, corner_radius=0
        )
        self.opt_preset.pack(side="left", fill="x", expand=True, padx=(0, 5))
        ctk.CTkButton(
            f_load, text="CARREGAR", width=80, height=32, fg_color="#333333", hover_color="#1A1A1A", 
            text_color="#FFFFFF", corner_radius=0, font=("Helvetica", 11, "bold"), command=self.apply_preset
        ).pack(side="right")
        
        # Deletar
        ctk.CTkButton(
            self.tab_presets, text="EXCLUIR SELECIONADO", height=32, fg_color="transparent", 
            border_color=RED_ACCENT, border_width=1, text_color=RED_ACCENT, hover_color="#FFF0F0", 
            corner_radius=0, font=("Helvetica", 11, "bold"), command=self.delete_preset
        ).pack(fill="x", pady=(30, 0))
        
        self.refresh_preset_menu()

    # --- FUNÇÕES DE PRESETS ---
    def load_presets(self):
        if os.path.exists(PRESETS_FILE):
            try:
                with open(PRESETS_FILE, "r") as f:
                    self.presets_data = json.load(f)
            except:
                self.presets_data = {}
        else:
            self.presets_data = {}

    def save_presets_file(self):
        with open(PRESETS_FILE, "w") as f:
            json.dump(self.presets_data, f, indent=4)

    def refresh_preset_menu(self):
        opts = list(self.presets_data.keys())
        if not opts:
            opts = ["Nenhum preset"]
            self.selected_preset_var.set("Nenhum preset")
        else:
            self.selected_preset_var.set(opts[0])
        self.opt_preset.configure(values=opts)

    def save_preset(self):
        name = self.preset_name_var.get().strip()
        if not name: return
        self.presets_data[name] = {
            "interval": self.interval_str.get(),
            "random": self.random_str.get(),
            "limit": self.limit_str.get(),
            "button": self.button_var.get(),
            "type": self.type_var.get(),
            "macro_events": self.macro_events
        }
        self.save_presets_file()
        self.refresh_preset_menu()
        self.lbl_status.configure(text=f"STATUS: PRESET '{name.upper()}' SALVO", text_color="#4CAF50")

    def apply_preset(self):
        name = self.selected_preset_var.get()
        if name in self.presets_data:
            p = self.presets_data[name]
            self.interval_str.set(p.get("interval", "100"))
            self.random_str.set(p.get("random", "0"))
            self.limit_str.set(p.get("limit", "0"))
            self.button_var.set(p.get("button", "Esquerdo"))
            self.type_var.set(p.get("type", "Único"))
            self.macro_events = p.get("macro_events", [])
            
            self.lbl_macro_status.configure(text=f"EVENTOS GRAVADOS: {len(self.macro_events)}")
            self.lbl_status.configure(text=f"STATUS: PRESET '{name.upper()}' CARREGADO", text_color="#4CAF50")

    def delete_preset(self):
        name = self.selected_preset_var.get()
        if name in self.presets_data:
            del self.presets_data[name]
            self.save_presets_file()
            self.refresh_preset_menu()
            self.lbl_status.configure(text=f"STATUS: PRESET '{name.upper()}' EXCLUÍDO", text_color=RED_ACCENT)

    # --- LÓGICA DE GRAVAÇÃO (MACRO) ---
    def clear_macro(self):
        if self.is_clicking or self.is_recording: return
        self.macro_events = []
        self.lbl_macro_status.configure(text="EVENTOS GRAVADOS: 0")
        self.lbl_status.configure(text="STATUS: MACRO LIMPO", text_color=TEXT_MUTED)

    def toggle_recording(self):
        if self.is_clicking: return 
        
        if not self.is_recording:
            self.is_recording = True
            self.macro_events = []
            self.record_start_time = time.time()
            self.lbl_status.configure(text="STATUS: GRAVANDO (F10 PARA PARAR)", text_color=RED_ACCENT)
            self.lbl_macro_status.configure(text="GRAVANDO... (0)")
            
            self.mouse_listener = mouse.Listener(on_move=self.on_mouse_move, on_click=self.on_mouse_click)
            self.mouse_listener.start()
        else:
            self.is_recording = False
            if self.mouse_listener:
                self.mouse_listener.stop()
            self.lbl_status.configure(text="STATUS: GRAVAÇÃO FINALIZADA", text_color=TEXT_MUTED)
            self.lbl_macro_status.configure(text=f"EVENTOS GRAVADOS: {len(self.macro_events)}")

    def on_mouse_move(self, x, y):
        if self.is_recording:
            t = time.time()
            if (t - self.last_move_time) > 0.02:
                self.last_move_time = t
                self.macro_events.append({'type': 'move', 'x': x, 'y': y, 'time': t - self.record_start_time})

    def on_mouse_click(self, x, y, button, pressed):
        if self.is_recording:
            t = time.time() - self.record_start_time
            try: b_name = button.name
            except AttributeError: b_name = 'left'
            self.macro_events.append({'type': 'click', 'x': x, 'y': y, 'button': b_name, 'pressed': pressed, 'time': t})

    # --- LÓGICA DE CLIQUE ---
    def start_hotkey_listener(self):
        def on_press(key):
            try:
                if key == keyboard.Key.f6:
                    self.after(0, self.toggle_clicker)
                elif key == keyboard.Key.f10:
                    if self.tabview.get() == "MACRO":
                        self.after(0, self.toggle_recording)
            except AttributeError:
                pass

        self.hotkey_listener = keyboard.Listener(on_press=on_press)
        self.hotkey_listener.daemon = True
        self.hotkey_listener.start()

    def toggle_clicker(self):
        if self.is_recording: return 
        
        if not self.is_clicking:
            try:
                float(self.interval_str.get())
                float(self.random_str.get())
                int(self.limit_str.get())
            except ValueError:
                self.lbl_status.configure(text="ERRO: VALORES INVÁLIDOS", text_color=RED_ACCENT)
                return

            self.is_clicking = True
            self.current_run_mode = self.tabview.get()
            
            if self.current_run_mode == "MACRO" and not self.macro_events:
                self.is_clicking = False
                self.lbl_status.configure(text="ERRO: NENHUM MACRO GRAVADO", text_color=RED_ACCENT)
                return

            # Atualizar UI
            self.btn_toggle.configure(text="PARAR (F6)", fg_color="#333333", hover_color="#1A1A1A")
            self.lbl_status.configure(text="STATUS: EXECUTANDO...", text_color=RED_ACCENT)
            self.tabview.configure(state="disabled")

            # Iniciar Thread
            self.click_thread = threading.Thread(target=self.click_loop, daemon=True)
            self.click_thread.start()
        else:
            self.stop_clicking()

    def stop_clicking(self):
        self.is_clicking = False
        self.btn_toggle.configure(text="INICIAR (F6)", fg_color=RED_ACCENT, hover_color=RED_HOVER)
        self.lbl_status.configure(text="STATUS: PARADO", text_color=TEXT_MUTED)
        self.tabview.configure(state="normal")

    def click_loop(self):
        limit = int(self.limit_str.get())
        clicks_done = 0
        
        if self.current_run_mode == "MACRO":
            while self.is_clicking:
                start_time = time.time()
                for ev in self.macro_events:
                    if not self.is_clicking: break
                    
                    target_time = start_time + ev['time']
                    while time.time() < target_time:
                        if not self.is_clicking: break
                        time.sleep(0.001)
                        
                    if not self.is_clicking: break
                    
                    if ev['type'] == 'move':
                        pyautogui.moveTo(ev['x'], ev['y'])
                    elif ev['type'] == 'click':
                        b = ev['button']
                        p_btn = 'left' if b == 'left' else ('right' if b == 'right' else 'middle')
                        if ev['pressed']: pyautogui.mouseDown(button=p_btn)
                        else: pyautogui.mouseUp(button=p_btn)
                            
                clicks_done += 1
                if limit > 0 and clicks_done >= limit:
                    self.after(0, self.stop_clicking)
                    break
                time.sleep(0.05)
                
        else:
            btn_map = {"Esquerdo": "left", "Direito": "right", "Meio": "middle"}
            btn = btn_map[self.button_var.get()]
            is_double = self.type_var.get() == "Duplo"
            
            try: base_ms = float(self.interval_str.get())
            except: base_ms = 100.0
            try: rand_ms = float(self.random_str.get())
            except: rand_ms = 0.0
                
            while self.is_clicking:
                actual_wait = (base_ms + random.uniform(0, rand_ms)) / 1000.0
                if is_double: pyautogui.doubleClick(button=btn)
                else: pyautogui.click(button=btn)
                    
                clicks_done += 1
                if limit > 0 and clicks_done >= limit:
                    self.after(0, self.stop_clicking)
                    break
                time.sleep(actual_wait)

if __name__ == "__main__":
    app = AutoClickerApp()
    app.mainloop()
