import sys
import time
import threading
import ctypes
from pynput import keyboard, mouse

LANG_DICT: dict[int, dict[str, str]] = {
    0: {
        "not_admin": "ATTENTION: You are NOT running this script as Administrator.",
        "shortcut": "Shortcut: Ctrl + Alt + Shift + P",
        "press_begin": "Press the shortcut to begin.",
        "recording": "RECORDING",
        "repeating": "REPEATING",
        "interrupted": "PLAYBACK INTERRUPTED",
        "exit_prompt": "\nPress Enter to exit..."
    },
    1: {
        "not_admin": "ATENÇÃO: Você NÃO está executando este script como Administrador.",
        "shortcut": "Atalho: Ctrl + Alt + Shift + P",
        "press_begin": "Pressione o atalho para começar.",
        "recording": "GRAVANDO",
        "repeating": "REPETINDO",
        "interrupted": "REPRODUÇÃO INTERROMPIDA",
        "exit_prompt": "\nPressione Enter para sair..."
    }
}
lang: int = 0

MOD_CTRL: set[str] = {"ctrl", "ctrl_l", "ctrl_r"}
MOD_ALT: set[str] = {"alt", "alt_l", "alt_r", "alt_gr"}
MOD_SHIFT: set[str] = {"shift", "shift_l", "shift_r"}

"""
Global `current_state` state-machine reference:

Operational States (Non-Negative):
 0 : IDLE
     Program is waiting for the user to press the shortcut trigger to begin.
 1 : RECORDING
     Mouse and keyboard listeners are actively logging events into `events`.
 2 : PLAYBACK
     The script is actively playing back the recorded event loop.

Transitional States (Negative):
-1 : PREPARING_RECORDING
     Intermediate state while running the countdown before starting recording.
-2 : PREPARING_PLAYBACK
     Intermediate state while stripping shortcut key events and running the 
     countdown before starting playback.
-3 : PREPARING_STOP
     Intermediate state while running the interruption countdown after stopping playback.
-4 : TERMINATED
     Playback has stopped and the script is shutting down.
"""

current_state: int = 0
events: list[tuple] = []
last_event_time: float = 0

pressed_keys: set[object] = set()
held_keys_for_recording: set[str] = set()
trigger_locked: bool = False 

playback_event = threading.Event()
exit_event = threading.Event()

def get_key_id(key) -> str:
    if isinstance(key, keyboard.Key):
        return key.name
    if hasattr(key, "vk") and key.vk is not None:
        return key.vk
    if hasattr(key, "char") and key.char is not None:
        return key.char.lower()
    return str(key)

def is_p_key_id(key_id) -> bool:
    return key_id in (80, "p", "\x10")

def is_trigger_active(pressed_set: set[object]) -> bool:
    has_ctrl: bool = any(k in MOD_CTRL for k in pressed_set)
    has_alt: bool = any(k in MOD_ALT for k in pressed_set)
    has_shift: bool = any(k in MOD_SHIFT for k in pressed_set)
    has_p: bool = any(is_p_key_id(k) for k in pressed_set)
    return has_ctrl and has_alt and has_shift and has_p

def print_countdown(final_text: str) -> None:
    for i in (3, 2, 1):
        print(i)
        time.sleep(1)
    print(final_text)

def record_event(event_type: str, *args: tuple) -> None:
    global last_event_time
    now: float = time.perf_counter()
    interval: float = now - last_event_time
    last_event_time = now
    events.append((interval, event_type, *args))

def strip_trigger_keys_from_events() -> None:
    keys_to_remove: set[object] = {k for k in pressed_keys if k in MOD_CTRL or k in MOD_ALT or k in MOD_SHIFT or is_p_key_id(k)}
    
    for i in range(len(events) - 1, -1, -1):
        ev: tuple = events[i]
        if ev[1] == "key_press":
            k_id: str = get_key_id(ev[2])
            if k_id in keys_to_remove:
                keys_to_remove.remove(k_id)
                events.pop(i)
                
        if not keys_to_remove:
            break

def handle_trigger() -> None:
    global current_state
    
    if current_state == 0:
        current_state = -1 
        threading.Thread(target=start_recording, daemon=True).start()
    elif current_state == 1:
        current_state = -2
        threading.Thread(target=start_playback, daemon=True).start()
    elif current_state == 2:
        current_state = -3
        threading.Thread(target=stop_everything, daemon=True).start()

def start_recording() -> None:
    global current_state, last_event_time
    print_countdown(LANG_DICT[lang]["recording"])
    events.clear()
    held_keys_for_recording.clear()
    last_event_time = time.perf_counter()
    current_state = 1

def start_playback() -> None:
    global current_state
    strip_trigger_keys_from_events()
    print_countdown(LANG_DICT[lang]["repeating"])
    current_state = 2
    playback_event.clear()
    threading.Thread(target=playback_loop, daemon=True).start()

def stop_everything() -> None:
    print_countdown(LANG_DICT[lang]["interrupted"])
    
    global current_state
    current_state = -4
    playback_event.set()
    exit_event.set()

def playback_loop() -> None:
    mouse_ctrl = mouse.Controller()
    key_ctrl = keyboard.Controller()
    
    playback_held_keys: set = set()
    
    while current_state in (2, -3):
        for ev in events:
            if current_state not in (2, -3):
                break
                
            interval: float = ev[0]
            if playback_event.wait(interval):
                break
                
            action: str = ev[1]
            if action == "mouse_move":
                mouse_ctrl.position = (ev[2], ev[3])
                
            elif action == "mouse_click":
                button, x, y, pressed = ev[2], ev[3], ev[4], ev[5]
                mouse_ctrl.position = (x, y)
                if pressed:
                    mouse_ctrl.press(button)
                else:
                    mouse_ctrl.release(button)
                    
            elif action == "mouse_scroll":
                x, y, dx, dy = ev[2], ev[3], ev[4], ev[5]
                mouse_ctrl.position = (x, y)
                mouse_ctrl.scroll(dx, dy)
                    
            elif action == "key_press":
                try:
                    key_ctrl.press(ev[2])
                    playback_held_keys.add(ev[2])
                except:
                    pass
                
            elif action == "key_release":
                try:
                    key_ctrl.release(ev[2])
                    if ev[2] in playback_held_keys:
                        playback_held_keys.remove(ev[2])
                except:
                    pass
                
    for k in playback_held_keys:
        try:
            key_ctrl.release(k)
        except:
            pass

def on_press(key) -> None:
    global trigger_locked
    key_id = get_key_id(key)
    pressed_keys.add(key_id)
    
    if is_trigger_active(pressed_keys):
        if not trigger_locked and current_state in (0, 1, 2):
            trigger_locked = True
            handle_trigger()
        return

    if current_state == 1:
        if key_id in held_keys_for_recording:
            return
        held_keys_for_recording.add(key_id)
        record_event("key_press", key)

def on_release(key) -> None:
    global trigger_locked
    key_id = get_key_id(key)
    
    if key_id in pressed_keys:
        pressed_keys.remove(key_id)
        
    if trigger_locked and not is_trigger_active(pressed_keys):
        trigger_locked = False
        
    if current_state == 1:
        if key_id in held_keys_for_recording:
            held_keys_for_recording.remove(key_id)
            record_event("key_release", key)

def on_move(x, y) -> None:
    if current_state == 1:
        record_event("mouse_move", x, y)

def on_click(x, y, button, pressed) -> None:
    if current_state == 1:
        record_event("mouse_click", button, x, y, pressed)

def on_scroll(x, y, dx, dy) -> None:
    if current_state == 1:
        record_event("mouse_scroll", x, y, dx, dy)

def is_admin() -> bool:
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False

def make_dpi_aware():
    try:
        ctypes.windll.shcore.SetProcessDpiAwareness(2)
    except Exception:
        try:
            ctypes.windll.user32.SetProcessDPIAware()
        except Exception:
            pass

if __name__ == "__main__":
    make_dpi_aware()
    
    try:
        lang_choice: str = input("[0] - English\n[1] - Português\n> ").strip()
        lang = 1 if lang_choice == '1' else 0
    except KeyboardInterrupt:
        sys.exit(0)
    
    print("-" * 60)
    
    if not is_admin():
        print(LANG_DICT[lang]["not_admin"])
        print("-" * 60)
        input(LANG_DICT[lang]["exit_prompt"])
        sys.exit(0)
        
    print(LANG_DICT[lang]["shortcut"])
    print(LANG_DICT[lang]["press_begin"])
    
    k_listener = keyboard.Listener(on_press=on_press, on_release=on_release)
    m_listener = mouse.Listener(on_move=on_move, on_click=on_click, on_scroll=on_scroll)
    
    k_listener.start()
    m_listener.start()
    
    try:
        exit_event.wait()
    except KeyboardInterrupt:
        pass
    
    k_listener.stop()
    m_listener.stop()
    
    input(LANG_DICT[lang]["exit_prompt"])