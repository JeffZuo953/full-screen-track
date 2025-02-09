import threading
import win32api
import win32con
import win32gui
import win32ts

WM_WTSSESSION_CHANGE = 0x2B1
WTS_SESSION_LOCK = 0x7
WTS_SESSION_UNLOCK = 0x8


def monitor_lock_screen(callback):
    """
    Monitors the screen lock and unlock events using Windows API.

    This function sets up a window to listen for session change events,
    specifically for screen lock and unlock events. When these events occur,
    the provided callback function is called with a boolean indicating
    whether the screen is locked (True) or unlocked (False).
    """

    def WndProc(hwnd, msg, wparam, lparam):
        """
        Window procedure to handle Windows messages.

        This function is called by the Windows operating system to process
        messages sent to the window. It checks for session change messages
        and calls the callback function accordingly.
        """
        if msg == WM_WTSSESSION_CHANGE:
            if wparam == WTS_SESSION_LOCK:
                callback(True)
            elif wparam == WTS_SESSION_UNLOCK:
                callback(False)
        return win32gui.DefWindowProc(hwnd, msg, wparam, lparam)

    hinst = win32api.GetModuleHandle(None)
    wndclass = win32gui.WNDCLASS()
    wndclass.hInstance = hinst
    wndclass.lpszClassName = "LockScreenMonitor"  # Class name
    wndclass.lpfnWndProc = WndProc
    atom = win32gui.RegisterClass(wndclass)

    hwnd = win32gui.CreateWindowEx(
        0,
        atom,
        "LockScreenMonitorWnd",
        0,
        0,
        0,
        0,
        0,
        win32con.HWND_MESSAGE,
        0,
        0,
        None,
    )
    wtsobj = win32ts.WTSRegisterSessionNotification(
        hwnd, win32ts.NOTIFY_FOR_THIS_SESSION
    )

    try:
        win32gui.PumpMessages()  # Listen for message loop
    finally:
        win32ts.WTSUnRegisterSessionNotification(wtsobj)
        win32gui.DestroyWindow(hwnd)
        win32gui.UnregisterClass(atom, hinst)


def create_screen_lock_monitor_thread(callback):
    """
    Creates and starts a thread to monitor screen lock events.

    This function creates a daemon thread that runs the `monitor_lock_screen`
    function. The daemon thread will automatically exit when the main program
    exits.
    """
    thread = threading.Thread(target=monitor_lock_screen, args=(callback,))
    thread.daemon = True
    thread.start()
    return thread
