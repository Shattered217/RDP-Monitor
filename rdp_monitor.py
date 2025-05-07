import win32api
import win32con
import win32gui
import win32ts
import time
import requests

# Telegram Bot配置
BOT_TOKEN = "xxxxxxxxxxxxx"
CHAT_ID = "111111111111"

# 消息与事件常量
WM_WTSSESSION_CHANGE   = 0x02B1
WTS_REMOTE_CONNECT     = 0x3
WTS_REMOTE_DISCONNECT  = 0x4

# Telegram 推送函数
def send_telegram_msg(text: str) -> bool:
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    data = {
        "chat_id": CHAT_ID,
        "text": text
    }
    try:
        r = requests.post(url, data=data, timeout=5)
        return r.status_code == 200 and r.json().get("ok", False)
    except Exception as e:
        print(f"[错误] Telegram 推送失败: {e}")
        return False

class RDPMonitor:
    CLASS_NAME = "RDPMonitorWindow"
    TITLE      = "HiddenRDPMonitor"

    def __init__(self):
        # 注册窗口类
        wc = win32gui.WNDCLASS()
        wc.hInstance     = hInstance = win32api.GetModuleHandle(None)
        wc.lpszClassName = self.CLASS_NAME
        wc.lpfnWndProc   = self._wnd_proc
        win32gui.RegisterClass(wc)

        # 创建隐藏窗口
        self.hWnd = win32gui.CreateWindow(
            self.CLASS_NAME, self.TITLE,
            0, 0, 0, 0, 0, 0, 0, hInstance, None
        )

        # 注册会话通知
        win32ts.WTSRegisterSessionNotification(
            self.hWnd, win32ts.NOTIFY_FOR_ALL_SESSIONS
        )

    def _wnd_proc(self, hWnd, msg, wParam, lParam):
        if msg == WM_WTSSESSION_CHANGE:
            session_id = lParam
            if wParam == WTS_REMOTE_CONNECT:
                self._notify(True)
            elif wParam == WTS_REMOTE_DISCONNECT:
                self._notify(False)
        return win32gui.DefWindowProc(hWnd, msg, wParam, lParam)

    def _notify(self, connected: bool):
        ts = time.strftime('%Y-%m-%d %H:%M:%S')
        if connected:
            message = f"📥 [远程登录] RDP 会话连接\n🕒 时间：{ts}"
        else:
            message = f"📤 [远程注销] RDP 会话断开\n🕒 时间：{ts}"
        ok = send_telegram_msg(message)
        print(f"[{'✔' if ok else '✘'}] 推送：{message}")

    def run(self):
        print("[*] RDP 会话监控器已启动，等待事件...")
        win32gui.PumpMessages()

if __name__ == "__main__":
    RDPMonitor().run()
