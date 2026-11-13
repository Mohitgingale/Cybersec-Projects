# Cyber Security Projects Portfolio 🛡️

Welcome to my central repository for custom-built cybersecurity tools, scripts, and applications. This repository serves as a portfolio of my work in ethical hacking, network security, and system administration.

Created and maintained by **Mohit Ingale**.

## 📂 Repository Structure

Below is a list of the tools currently available in this repository. Navigate to each specific folder for detailed information, prerequisites, and usage instructions for that tool.

### 1. [MAC-CHANGER](./MAC-CHANGER)
A Python-based Windows command-line utility to easily view, spoof, and restore the Media Access Control (MAC) address of network interfaces. Features an interactive terminal UI, automatic privilege escalation, and instant network refreshing without requiring a system reboot.

### 2. [KEYLOGGER](./KEYLOGGER)
A lightweight, cross-platform keystroke and active-window logger written in Python. Captures input with readable tags for control and function keys, stamps every foreground window change for context, and rolls logs over per day. Supports optional silent SMTP exfiltration so logs leave the host without opening a port. Runs headless via `pythonw` with no admin rights, and ships with autostart recipes for Windows, Linux, and macOS.

*(More tools will be added here as they are developed...)*

## 🚀 Getting Started

To download all the tools in this repository to your local machine, you can clone the entire repository using Git:

```bash
git clone https://github.com/Mohitgingale/Cybersec-Projects.git
cd Cybersec-Projects
```

From there, navigate into the specific tool's directory (e.g., `cd MAC-CHANGER`) and follow the instructions in that tool's individual `README.md` file.

## 📋 Tool Overview

| Tool | Platform | Language | Requires Admin/Root |
| --- | --- | --- | --- |
| [MAC-CHANGER](./MAC-CHANGER) | Windows | Python | Yes (auto-elevates) |
| [KEYLOGGER](./KEYLOGGER) | Windows / Linux (X11) / macOS | Python | No |

## 🧰 Common Prerequisites

Both tools are written in Python 3 and are installed the same way:

```bash
pip install -r requirements.txt
```

Each tool has its own `requirements.txt` and its own setup notes — read the individual README before running anything.

## ⚠️ Legal Disclaimer

All scripts, tools, and information provided in this repository are created strictly for educational purposes, ethical hacking, and security research.

- Do not use these tools on any system, network, or application that you do not own or do not have explicit, written permission to test.
- The author is not responsible for any misuse, damage, or illegal activity caused by the use of these tools.
- All code is provided as-is, without warranty of any kind.
- By using any code in this repository, you agree to take full responsibility for your actions.

---

## © Copyright

© 2026 **Mohit Ingale**. All rights reserved.

The tools, scripts, and documentation in this repository are the original work of Mohit Ingale unless otherwise credited. Code is released under the MIT License — see [`LICENSE`](./LICENSE) — which permits reuse with attribution intact.

- **Author:** Mohit Ingale
- **GitHub:** [@Mohitgingale](https://github.com/Mohitgingale)
- **Repository:** [Cybersec-Projects](https://github.com/Mohitgingale/Cybersec-Projects)