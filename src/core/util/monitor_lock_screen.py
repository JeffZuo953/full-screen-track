import threading
import win32api
import win32con
import win32gui
import win32ts

WM_WTSSESSION_CHANGE = 0x2B1
WTS_SESSION_LOCK = 0x7
WTS_SESSION_UNLOCK = 0x8


def monitor_lock_screen(callback):

    def WndProc(hwnd, msg, wparam, lparam):
        if msg == WM_WTSSESSION_CHANGE:
            if wparam == WTS_SESSION_LOCK:
                callback(True)
            elif wparam == WTS_SESSION_UNLOCK:
                callback(False)
        return win32gui.DefWindowProc(hwnd, msg, wparam, lparam)

    hinst = win32api.GetModuleHandle(None)
    wndclass = win32gui.WNDCLASS()
    wndclass.hInstance = hinst
    wndclass.lpszClassName = "LockScreenMonitor"  # 类名
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
        win32gui.PumpMessages()  # 监听消息循环
    finally:
        win32ts.WTSUnRegisterSessionNotification(wtsobj)
        win32gui.DestroyWindow(hwnd)
        win32gui.UnregisterClass(atom, hinst)


def create_screen_lock_monitor_thread(callback):
    thread = threading.Thread(target=monitor_lock_screen, args=(callback,))
    thread.daemon = True
    thread.start()
    return thread
