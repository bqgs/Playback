# Overview

This project is a Python-based global macro recorder and playback utility. It captures system-wide keyboard and mouse events and reproduces them with precise timing. Built with `pynput` and a robust state-machine architecture, it allows users to automate repetitive tasks seamlessly.

# Key Features

* **Bilingual Interface:** Supports English and Portuguese terminal prompts natively.
* **Precise Event Logging:** Captures mouse movements, clicks, scrolls, and keystrokes alongside their exact time intervals.
* **Windows Native Integrations:** Automatically enforces High-DPI awareness for accurate mouse coordinates and verifies Administrator privileges.
* **Single-Hotkey Control:** A single global shortcut cleanly transitions the script through idle, recording, playback, and termination states while automatically stripping the trigger keys from the macro loop.

# Requirements & Setup

* **Operating System:** Windows (relies on `ctypes.windll` for Admin and DPI API calls).
* **Dependencies:** Requires Python 3 and the `pynput` library (install via `pip install pynput`).
* **Permissions:** You must run your terminal or IDE as an Administrator to allow global input hooking.

# Usage Instructions

1. Run the script and choose your language: enter `0` for English or `1` for Portuguese.
2. Press the global shortcut `Ctrl + Alt + Shift + P` to start a 3-second countdown, followed by the **RECORDING** phase.
3. Perform your workflow, then press the shortcut again to initiate the **REPEATING** countdown and loop.
4. Press the shortcut a final time to trigger a **PLAYBACK INTERRUPTED** state and safely exit the application.

# Best Practices & Precautions

To ensure your macros run smoothly, keep the following guidelines in mind during recording and playback:

* **Minimize the terminal window:** Do this before the countdown ends. This script records inputs system-wide, meaning any accidental clicks or keystrokes inside the terminal during recording will also be reproduced during playback.

* **Use a neutral mouse position:** Start and end your recording loop with the mouse in a consistent, neutral location. The script tracks absolute screen coordinates; returning to a baseline position prevents the end of one cycle from misaligning the start of the next.

* **Pad your loading times:** Add a few extra seconds when opening applications, loading web pages, or performing heavy processing tasks. Playback relies strictly on recorded time intervals. If your system or network is slightly slower during playback, adding buffer time prevents the macro from misfiring before the UI is ready.

## ⚠️ WARNING: Blind Playback

This utility does not possess computer vision or state awareness. It does not verify if an app has opened, a page has loaded, or a button is present. It strictly replays inputs based on timing and sequence. Unexpected interface changes will cause the macro to execute actions in the wrong context.

**In Short:** Playback is not a system that understands what is happening on the screen. The more predictable your environment is—matching mouse positions, open windows, and response times—the more reliable your automation will be.


<div align="center">
  <img width="617" height="446" alt="Screenshot 2026-08-27 115707" src="https://github.com/user-attachments/assets/e75ceb07-d9b0-4a23-88e2-d26f3fc7836b" />
</div>

<div align="center">
  <img width="608" height="445" alt="Screenshot 2026-08-27 115623" src="https://github.com/user-attachments/assets/5239602b-a4c4-4c81-9368-0df393bbb697" />
</div>
