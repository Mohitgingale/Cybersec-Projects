# Windows MAC Changer 🛡️

A Python-based command-line utility to easily view, change, and restore the Media Access Control (MAC) address of network interfaces on Windows systems. It features an interactive, color-coded terminal UI and automatically handles administrative privileges.

Created by **Mohit Ingale**.

## ✨ Features

* **Auto-Privilege Escalation:** Automatically detects and requests Administrator rights required for modifying network registry keys.
* **Interface Discovery:** Dynamically fetches and lists all available dedicated network interfaces using `netsh`.
* **Current MAC Display:** Quickly view the active MAC address of any selected adapter.
* **Random MAC Generation:** Generates and applies a completely random, valid locally administered MAC address with a single click.
* **Custom MAC Spoofing:** Allows you to input and apply a specific 12-character custom MAC address.
* **Restore Default:** Easily strip custom registry keys to restore the network adapter's original factory hardware MAC address.
* **Auto-Network Refresh:** Automatically disables the interface, flushes DNS, and reenables the connection to apply the new MAC address instantly without requiring a system reboot.

## ⚙️ Prerequisites & Requirements

Before running this script, ensure your system meets the following requirements:

* **Operating System:** Windows 10 or Windows 11 (This script relies on Windows-specific commands like `netsh`, `getmac`, and the Windows Registry).
* **Python:** Python 3.6 or higher installed on your system.

### Dependencies
This script primarily uses Python's built-in libraries (`subprocess`, `random`, `ctypes`, `sys`, `os`, `time`). However, it requires one external library for the colored terminal interface:

* `colorama`

## 🚀 Installation & Setup

1. **Clone the repository** (or download the files directly):
   git clone https://github.com/Mohitgingale/Cybersec-Projects.git
   cd Cybersec-Projects/MAC-CHANGER

2. **Install the required dependencies:**
   pip install colorama

## 💻 How to Run

1. Open your terminal or command prompt.
2. Navigate to the directory containing the script.
3. Run the script using Python:
   python macchanger.py

4. **Note:** A User Account Control (UAC) prompt will appear asking for Administrator permissions. Click **Yes**. The script will then relaunch itself with the necessary privileges.
5. Follow the on-screen interactive menu to select your interface and apply your desired MAC address.

## 🛠️ Technical Details: How it Works

Unlike Linux, where MAC spoofing is typically done via `ifconfig` or `ip link`, Windows requires modifying the system registry. This script automates that process by:

1. Locating the specific network adapter within `HKEY_LOCAL_MACHINE\SYSTEM\CurrentControlSet\Control\Class\{4d36e972-e325-11ce-bfc1-08002be10318}`.
2. Appending or modifying the `NetworkAddress` string value with the new MAC.
3. Disabling the adapter using `netsh interface set interface disable`.
4. Flushing the DNS and releasing/renewing the IP configuration.
5. Re-enabling the adapter to force Windows to read the new registry value.

## ⚠️ Disclaimer

This tool is created for **educational purposes and ethical hacking/security testing only**. Changing your MAC address can help bypass network filters, enhance privacy on public Wi-Fi, or test network security configurations. Do not use this tool on networks you do not own or do not have explicit permission to test. The author is not responsible for any misuse or damage caused by this program.