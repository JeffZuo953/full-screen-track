# Standard library imports
from __future__ import annotations
import threading
import types
from typing import Callable

# Third-party library imports
import win32api
import win32con
import win32gui
import win32ts

# Constants for Windows messages and session states
WM_WTSSESSION_CHANGE: types.IntType = 0x2B1
WTS_SESSION_LOCK: types.IntType = 0x7
WTS_SESSION_UNLOCK: types.IntType = 0x8


def monitor_lock_screen(callback: Callable[[bool], None]) -> None:
    """
    Monitors the screen lock and unlock events using Windows API.

    This function sets up a window to listen for session change events,
    specifically for screen lock and unlock events. When these events occur,
    the provided callback function is called with a boolean indicating
    whether the screen is locked (True) or unlocked (False).

    Args:
        callback: A function to be called when the screen lock state changes.
                  It receives a boolean argument (True for locked, False for unlocked).
    """

    def WndProc(
        hwnd: int, msg: int, wparam: int, lparam: int
    ) -> int:  # Corrected type hints
        """
        Window procedure to handle Windows messages.

        This function is called by the Windows operating system to process
        messages sent to the window. It checks for session change messages
        and calls the callback function accordingly.

        Args:
            hwnd: The handle to the window receiving the message.
            msg: The message code.
            wparam: Additional message-specific information.
            lparam: Additional message-specific information.

        Returns:
            The result of the message processing, depends on the message.
        """
        if msg == WM_WTSSESSION_CHANGE:
            if wparam == WTS_SESSION_LOCK:
                callback(True)  # Screen locked
            elif wparam == WTS_SESSION_UNLOCK:
                callback(False)  # Screen unlocked
        return win32gui.DefWindowProc(hwnd, msg, wparam, lparam)

    hinst: int = win32api.GetModuleHandle(None)  # Handle to the current module instance
    wndclass: win32gui.WNDCLASS = (
        win32gui.WNDCLASS()
    )  # Define a new window class
    wndclass.hInstance = hinst
    wndclass.lpszClassName = "LockScreenMonitor"  # Class name
    wndclass.lpfnWndProc = WndProc  # Pointer to the window procedure
    atom: int = win32gui.RegisterClass(wndclass)  # Register the window class

    # Create a message-only window
    hwnd: int = win32gui.CreateWindowEx(
        0,  # Extended window style
        atom,  # Class name or atom
        "LockScreenMonitorWnd",  # Window name
        0,  # Window style
        0,  # X position
        0,  # Y position
        0,  # Width
        0,  # Height
        win32con.HWND_MESSAGE,  # Parent window: Message-only window
        0,  # Menu handle
        0,  # Instance handle
        None,  # Additional application data
    )
    # Register for session notifications
    wtsobj: types.IntType = win32ts.WTSRegisterSessionNotification(
        hwnd, win32ts.NOTIFY_FOR_THIS_SESSION
    )

    try:
        win32gui.PumpMessages()  # Listen for message loop
    finally:
        # Unregister for session notifications and clean up
        win32ts.WTSUnRegisterSessionNotification(wtsobj)
        win32gui.DestroyWindow(hwnd)
        win32gui.UnregisterClass(atom, hinst)


def create_screen_lock_monitor_thread(
    callback: Callable[[bool], None]
) -> threading.Thread:
    """
    Creates and starts a thread to monitor screen lock events.

    This function creates a daemon thread that runs the `monitor_lock_screen`
    function. The daemon thread will automatically exit when the main program
    exits.

    Args:
        callback: A function to be called when the screen lock state changes.
                  It receives a boolean argument (True for locked, False for unlocked).

    Returns:
        The created thread object.
    """
    thread = threading.Thread(
        target=monitor_lock_screen, args=(callback,)
    )  # Create the thread
    thread.daemon = True  # Set the thread as a daemon thread
    thread.start()  # Start the thread
    return thread
