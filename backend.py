import pyautogui
import threading
import time
from pynput import keyboard, mouse
import sys
import json
import random
import os

# Force stdout to be line-buffered
sys.stdout.reconfigure(line_buffering=True)

def send_message(type, value):
    print(json.dumps({"type": type, "value": value}))

class ClickerBackend:
    def __init__(self, config):
        self.config = config
        self.is_running = False
        self.is_recording = False
        self.click_count = 0
        self.macro_events = config.get('macro_events', [])
        self.record_start_time = 0
        self.last_move_time = 0
        
        # Capture state
        self.is_picking = False
        self.pick_mode = 'single'
        self.pick_listener = None
        
        # New Params
        self.human_sim = False
        self.target_mode = 'cursor'
        self.target_x = 0
        self.target_y = 0
        self.multi_points = []
        self.hotkey_click = 'f6'
        self.hotkey_record = 'f10'
        
        # Mapping config values
        self.update_params(config)

    def update_params(self, config):
        self.config = config
        self.interval = config.get('interval', 100) / 1000.0
        self.random_ms = config.get('random', 0) / 1000.0
        self.limit = config.get('limit', 0)
        self.button = config.get('button', 'left')
        self.click_type = config.get('type', 'single')
        self.macro_events = config.get('macro_events', [])
        self.cps_limit = config.get('cps_limit', 0)
        self.capture_keyboard = config.get('capture_keyboard', True)
        
        # New Settings
        self.human_sim = config.get('human_sim', False)
        self.target_mode = config.get('target_mode', 'cursor')
        self.target_x = config.get('target_x', 0)
        self.target_y = config.get('target_y', 0)
        self.multi_points = config.get('multi_points', [])
        self.hotkey_click = config.get('hotkey_click', 'f6').lower()
        self.hotkey_record = config.get('hotkey_record', 'f10').lower()
        self.app_bounds = config.get('app_bounds', None)
        
        # Calculate dynamic interval if CPS limit is set
        if self.cps_limit > 0:
            self.interval = 1.0 / self.cps_limit

        self.py_button = 'left'
        if self.button == 'middle': self.py_button = 'middle'
        elif self.button == 'right': self.py_button = 'right'

    def start_clicking(self):
        if self.is_running: return
        self.is_running = True
        self.click_count = 0
        send_message("status", "running")
        
        if self.macro_events:
            threading.Thread(target=self.run_macro, daemon=True).start()
        else:
            threading.Thread(target=self.run_clicker, daemon=True).start()

    def stop_clicking(self):
        self.is_running = False
        send_message("status", "stopped")

    def run_clicker(self):
        try:
            # Pequeno delay inicial
            time.sleep(0.3)
            multi_index = 0
            
            while self.is_running:
                # Determinar posição do clique
                target_x, target_y = None, None
                
                if self.target_mode == 'fixed':
                    target_x, target_y = self.target_x, self.target_y
                elif self.target_mode == 'multi' and self.multi_points:
                    point = self.multi_points[multi_index]
                    target_x, target_y = point['x'], point['y']
                    multi_index = (multi_index + 1) % len(self.multi_points)
                
                # Simular humano: pequena variação na posição
                if self.human_sim and target_x is not None:
                    target_x += random.randint(-2, 2)
                    target_y += random.randint(-2, 2)
                
                # Executar clique
                if target_x is not None:
                    # Garantir que o mouse vá para a posição antes de clicar
                    if self.human_sim:
                        pyautogui.moveTo(target_x, target_y, duration=random.uniform(0.1, 0.25))
                    else:
                        pyautogui.moveTo(target_x, target_y, duration=0.05) # Pequeno delay para ser visível

                    if self.click_type == 'double':
                        pyautogui.doubleClick(button=self.py_button)
                        self.click_count += 2
                    elif self.click_type == 'triple':
                        pyautogui.click(button=self.py_button, clicks=3)
                        self.click_count += 3
                    else:
                        pyautogui.click(button=self.py_button)
                        self.click_count += 1
                else:
                    # Modo cursor padrão
                    if self.human_sim:
                        curr_x, curr_y = pyautogui.position()
                        pyautogui.moveTo(curr_x + random.randint(-1, 1), curr_y + random.randint(-1, 1), duration=0.05)

                    if self.click_type == 'double':
                        pyautogui.doubleClick(button=self.py_button)
                        self.click_count += 2
                    elif self.click_type == 'triple':
                        pyautogui.click(button=self.py_button, clicks=3)
                        self.click_count += 3
                    else:
                        pyautogui.click(button=self.py_button)
                        self.click_count += 1
                
                send_message("click_update", self.click_count)

                if self.limit > 0 and self.click_count >= self.limit:
                    break
                
                # Simular humano: variação no intervalo e duração do clique
                wait_time = self.interval
                if self.human_sim:
                    # Variação mais "orgânica"
                    wait_time *= random.uniform(0.9, 1.1)
                    # Ocasionalmente uma pausa maior
                    if random.random() < 0.05:
                        wait_time += random.uniform(0.1, 0.3)
                
                if self.random_ms > 0:
                    wait_time += random.uniform(0, self.random_ms)
                
                time.sleep(max(0.001, wait_time))
        except Exception as e:
            send_message("error", str(e))
        self.stop_clicking()

    def run_macro(self):
        try:
            while self.is_running:
                start_time = time.time()
                for event in self.macro_events:
                    if not self.is_running: break
                    
                    elapsed = time.time() - start_time
                    wait = event['time'] - elapsed
                    if wait > 0:
                        time.sleep(wait)
                    
                    if event['type'] == 'move':
                        pyautogui.moveTo(event['x'], event['y'])
                    elif event['type'] == 'click':
                        if event['pressed']:
                            pyautogui.mouseDown(x=event['x'], y=event['y'], button=event['button'])
                        else:
                            pyautogui.mouseUp(x=event['x'], y=event['y'], button=event['button'])
                    elif event['type'] == 'key':
                        if event['pressed']:
                            pyautogui.keyDown(event['key'])
                        else:
                            pyautogui.keyUp(event['key'])
                
                # Se houver limite de cliques/repetições
                if self.limit > 0:
                    self.click_count += 1
                    if self.click_count >= self.limit: 
                        break

        except Exception as e:
            send_message("error", str(e))
        self.stop_clicking()

    def start_recording(self):
        if self.is_recording: return
        self.is_recording = True
        self.macro_events = []
        self.record_start_time = time.time()
        send_message("status", "recording")
        
        self.mouse_listener = mouse.Listener(on_move=self.on_mouse_move, on_click=self.on_mouse_click)
        self.mouse_listener.start()
        
        if self.capture_keyboard:
            self.key_listener = keyboard.Listener(on_press=self.on_key_press, on_release=self.on_key_release)
            self.key_listener.start()

    def stop_recording(self):
        self.is_recording = False
        if hasattr(self, 'mouse_listener'): self.mouse_listener.stop()
        if hasattr(self, 'key_listener'): self.key_listener.stop()
        send_message("macro_recorded", self.macro_events)
        send_message("status", "stopped")

    def pick_position(self, mode='single'):
        if self.is_picking: self.stop_pick_position()
        
        self.is_picking = True
        self.pick_mode = mode
        
        def on_click(x, y, button, pressed):
            if pressed and self.is_picking:
                # Se o clique for dentro da área do app (onde está o botão Parar), ignoramos
                if self.app_bounds:
                    b = self.app_bounds
                    if b['x'] <= x <= b['x'] + b['width'] and b['y'] <= y <= b['y'] + b['height']:
                        return

                if self.pick_mode == 'multi':
                    send_message("multi-position-picked", {"x": int(x), "y": int(y)})
                    # Don't stop for multi, keep listening until stopped by user
                else:
                    send_message("position-picked", {"x": int(x), "y": int(y)})
                    self.stop_pick_position()
                    return False
        
        self.pick_listener = mouse.Listener(on_click=on_click)
        self.pick_listener.start()

    def stop_pick_position(self):
        self.is_picking = False
        if self.pick_listener:
            self.pick_listener.stop()
            self.pick_listener = None

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
            except: b_name = 'left'
            self.macro_events.append({'type': 'click', 'x': x, 'y': y, 'button': b_name, 'pressed': pressed, 'time': t})

    def on_key_press(self, key):
        if self.is_recording:
            # Skip control keys
            if self.is_control_key(key): return
            
            t = time.time() - self.record_start_time
            k_name = self.get_key_name(key)
            if k_name:
                self.macro_events.append({'type': 'key', 'key': k_name, 'pressed': True, 'time': t})

    def on_key_release(self, key):
        if self.is_recording:
            if self.is_control_key(key): return
            
            t = time.time() - self.record_start_time
            k_name = self.get_key_name(key)
            if k_name:
                self.macro_events.append({'type': 'key', 'key': k_name, 'pressed': False, 'time': t})

    def is_control_key(self, key):
        # Ignore hotkeys during recording
        k_name = self.get_key_name(key).lower()
        return k_name == self.hotkey_click or k_name == self.hotkey_record

    def get_key_name(self, key):
        try:
            return key.char
        except AttributeError:
            return str(key).replace('Key.', '')

def main():
    backend = ClickerBackend({})

    def on_press(key):
        k_name = backend.get_key_name(key).lower()
        
        if k_name == backend.hotkey_click:
            if backend.is_running: backend.stop_clicking()
            else: backend.start_clicking()
        elif k_name == backend.hotkey_record:
            if backend.is_recording: backend.stop_recording()
            else: backend.start_recording()

    listener = keyboard.Listener(on_press=on_press)
    listener.start()

    while True:
        try:
            line = sys.stdin.readline()
            if not line: break
            cmd = json.loads(line)
            
            if cmd['type'] == 'update_config':
                backend.update_params(cmd['value'])
            elif cmd['type'] == 'start':
                backend.start_clicking()
            elif cmd['type'] == 'stop':
                backend.stop_clicking()
            elif cmd['type'] == 'pick_position':
                backend.pick_position(cmd['value'])
            elif cmd['type'] == 'stop_pick_position':
                backend.stop_pick_position()
                
        except EOFError: break
        except Exception as e: send_message("error", str(e))

if __name__ == "__main__":
    main()
