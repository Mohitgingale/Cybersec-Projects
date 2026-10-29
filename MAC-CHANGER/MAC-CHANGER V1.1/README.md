# 🛡️ Windows MAC Changer Pro

A modern, robust, graphical desktop application (GUI) for Windows 10/11 that easily views, changes, and restores the Media Access Control (MAC) address of network interfaces. Built with Python and `customtkinter`.

**Created by Mohit Ingale.**

![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)
![Windows](https://img.shields.io/badge/OS-Windows_10%20%7C%2011-0078D6.svg)
![License](https://img.shields.io/badge/License-MIT-green.svg)

---

## ✨ Key Features

- **Modern GUI with Theme Engine:** A sleek dark-mode-first interface built with CustomTkinter. Features 10 dynamic color themes (Cyber Red, Matrix Green, Hacker Dark, Ocean Blue, etc.).
- **Auto-Privilege Escalation:** Automatically detects if Administrator rights are present. If not, safely prompts for UAC and relaunches the app.
- **Robust Network Refresh:** Uses PowerShell (`Disable-NetAdapter` / `Enable-NetAdapter`) to restart adapters reliably without the system hangs commonly caused by standard `netsh` commands on Windows 11.
- **Random MAC Generation:** Automatically generates a valid, randomized *Locally Administered* MAC address with one click.
- **Custom MAC Spoofing:** Safely input your own 12-character MAC address with built-in regex validation.
- **Restore Default:** Safely strips custom registry keys to restore the network adapter's original factory hardware MAC address.

## ⚙️ Prerequisites

- **Operating System:** Windows 10 or Windows 11.
- **Python:** Python 3.8 or higher.
- **Libraries:** CustomTkinter.

## 🚀 Installation & Setup

1. **Clone the repository:**
   ```bash
   git clone https://github.com/Mohitgingale/Cybersec-Projects.git
   cd Cybersec-Projects/MAC-CHANGER
   ```

2. **Install the required dependencies:**
   ```bash
   pip install customtkinter
   ```

## 💻 Usage

Run the script from your terminal or command prompt:

```bash
python mac_changer_gui.py
```

*Note: A User Account Control (UAC) prompt will appear asking for Administrator permissions. Click Yes to allow the tool to modify the network registry keys.*

### Creating a Standalone Executable (.exe)

If you want to run the tool without needing Python installed, you can compile it into a single executable file using PyInstaller:

1. Install PyInstaller:
   ```bash
   pip install pyinstaller
   ```
2. Build the `.exe`:
   ```bash
   python -m PyInstaller --noconsole --onefile --uac-admin --collect-all customtkinter mac_changer_gui.py
   ```
3. Look inside the generated `dist` folder to find your compiled `mac_changer_gui.exe`.

## 🛠️ How it Works (Technical Details)

Unlike Linux (where MAC spoofing is handled via `ip link` or `ifconfig`), Windows requires modifying the system registry. This tool automates the process by:
1. Fetching accurate physical adapter mappings via PowerShell.
2. Locating the specific network adapter within `HKEY_LOCAL_MACHINE\SYSTEM\CurrentControlSet\Control\Class\{4d36e972-e325-11ce-bfc1-08002be10318}`.
3. Modifying or deleting the `NetworkAddress` string value.
4. Using PowerShell to disable the adapter, flush the DNS, and re-enable the connection to apply the new registry value instantly.

## ⚠️ Disclaimer

This tool is provided for educational and authorized network testing purposes only. The author is not responsible for any misuse or damage caused by this program. Always ensure you have permission before modifying network parameters on enterprise or public networks.