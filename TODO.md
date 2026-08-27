# Implement the following features:
> Master shortcut: Ctrl + Alt + Shift + P (Cycles: Idle -> Record -> Playback -> Exit)
> Trigger action recording on first shortcut press:
    > Mouse actions: (interval, action_type [move/click], x, y, button, pressed_state)
    > Keyboard actions: (interval, action_type [press/release], key)
> Store all input events chronologically in a list
> Record continuously until the shortcut is triggered a second time
    > Strip the triggering shortcut keys from the end of the recorded event list
> Replay the recorded event list sequentially in an infinite loop
> Stop playback, unhook listeners, and exit the application when the shortcut is triggered a third time
--------------------------------------------------------------------------------------------------------------------------

# Fix the following bugs and issues:
> Mouse scroll wheel inputs are neither recorded nor reproduced during playback [FIXED]
--------------------------------------------------------------------------------------------------------------------------

# Optimize the efficiency of the following subroutines:
> N/A
--------------------------------------------------------------------------------------------------------------------------