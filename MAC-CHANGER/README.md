# 🛡️ Windows MAC Changer 

A powerful, Python-based utility to easily view, spoof, and restore the Media Access Control (MAC) address of network interfaces on Windows systems. This tool automates the process of editing Windows Registry keys and restarting network adapters to apply changes instantly.

Created by **Mohit Ingale** for network administration, cybersecurity testing, and privacy enhancement.

---

## 📂 Project Versions

This repository contains two distinct versions of the tool. Choose the one that fits your workflow:

### [🚀 V1.1 - GUI Edition (Latest & Recommended)](./MAC-CHANGER%20V1.1)
A modern, dark-mode desktop application built with `customtkinter`. 
* **Graphical Interface:** Sleek, user-friendly UI with no terminal required.
* **Theme Engine:** Includes 10 customizable color themes (Cyber Red, Matrix Green, Hacker Dark, etc.).
* **Robust Backend:** Uses PowerShell (`Disable-NetAdapter`) for highly reliable network refreshing on Windows 11.
* **Standalone Executable:** Can be packaged into a single `.exe` file for use on systems without Python installed.

### [💻 V1.0 - CLI Edition (Classic)](./MAC-CHANGER%20V1.0)
A lightweight, interactive command-line interface.
* **Terminal UI:** Color-coded menus built using `colorama`.
* **Fast & Minimal:** Perfect for environments where you just need to drop a script into a terminal and run it.
* **Legacy Support:** Uses standard `netsh` commands for adapter toggling.

---

## ✨ Core Features (Both Versions)
* **Auto-Privilege Escalation:** Automatically detects and requests the Administrator rights required to modify network registry keys.
* **Interface Discovery:** Dynamically fetches and lists all active physical network adapters.
* **Random MAC Generation:** Generates valid *Locally Administered* MAC addresses with a single click.
* **Custom MAC Spoofing:** Allows manual input of specific 12-character MAC addresses.
* **Restore Default:** Safely strips custom registry keys to restore the adapter's original factory hardware MAC.
* **Auto-Network Refresh:** Flushes DNS and restarts the adapter to apply the new MAC instantly—no system reboot required.

---

## ⚙️ Prerequisites
* **OS:** Windows 10 or Windows 11
* **Python:** Python 3.6+ (If running from source)
* **Dependencies:** 
  * V1.1 (GUI): `pip install customtkinter`
  * V1.0 (CLI): `pip install colorama`

---

## 🚀 How to Run

**1. Clone the repository:**
```bash
git clone [https://github.com/Mohitgingale/Cybersec-Projects.git](https://github.com/Mohitgingale/Cybersec-Projects.git)
cd Cybersec-Projects/MAC-CHANGER