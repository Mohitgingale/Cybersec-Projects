import os
import sys
import ctypes
import subprocess
import winreg
import random
import re
import threading
import time
import customtkinter as ctk

# =========================================
# 1. AUTO ADMIN (CRASH-PROOF VERSION)
# =========================================
def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False

def run_as_admin():
    """Relaunch with Admin rights safely (handles spaces in folder names)."""
    if not is_admin():
        script_path = os.path.abspath(sys.argv[0])
        params = f'"{script_path}"'
        ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, params, None, 1)
        sys.exit()

run_as_admin()

# =========================================
# 2. CORE BACKEND LOGIC
# =========================================
REGISTRY_NETWORK_CLASS = r"SYSTEM\CurrentControlSet\Control\Class\{4d36e972-e325-11ce-bfc1-08002be10318}"

def get_ethernet_interfaces():
    """Fetch physical network adapters using PowerShell (More reliable than netsh)."""
    adapters = {}
    try:
        ps_command = 'Get-NetAdapter | Where-Object {$_.Virtual -eq $False} | Select-Object Name, InterfaceDescription, MacAddress | ConvertTo-Csv -NoTypeInformation'
        output = subprocess.check_output(["powershell", "-Command", ps_command], creationflags=subprocess.CREATE_NO_WINDOW, text=True)
        
        lines = output.strip().split('\n')[1:]
        for line in lines:
            if not line: continue
            parts = [p.strip('"') for p in line.split('","')]
            if len(parts) >= 3:
                name, desc, mac = parts[0], parts[1], parts[2].replace('-', '')
                adapters[name] = {"desc": desc, "mac": mac}
    except Exception as e:
        pass
    return adapters

def get_registry_path(adapter_desc):
    try:
        key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, REGISTRY_NETWORK_CLASS)
        for i in range(100):
            try:
                subkey_name = f"{i:04d}"
                subkey = winreg.OpenKey(key, subkey_name)
                desc, _ = winreg.QueryValueEx(subkey, "DriverDesc")
                if adapter_desc in desc or desc in adapter_desc:
                    return f"{REGISTRY_NETWORK_CLASS}\\{subkey_name}"
            except WindowsError:
                continue
    except Exception:
        pass
    return None

def generate_random_mac():
    valid_second_chars = ['2', '6', 'A', 'E'] # Required by Windows
    mac = [random.choice('0123456789ABCDEF'), random.choice(valid_second_chars)]
    for _ in range(10):
        mac.append(random.choice('0123456789ABCDEF'))
    return "".join(mac)

def restart_adapter(adapter_name):
    """Restarts adapter & flushes DNS"""
    try:
        disable_cmd = f'Disable-NetAdapter -Name "{adapter_name}" -Confirm:$false'
        enable_cmd = f'Enable-NetAdapter -Name "{adapter_name}" -Confirm:$false'
        
        subprocess.run(["powershell", "-Command", disable_cmd], creationflags=subprocess.CREATE_NO_WINDOW, check=True)
        time.sleep(2)
        subprocess.run(["powershell", "-Command", enable_cmd], creationflags=subprocess.CREATE_NO_WINDOW, check=True)
        subprocess.run(["ipconfig", "/flushdns"], creationflags=subprocess.CREATE_NO_WINDOW)
        return True
    except:
        return False


# =========================================
# 3. GRAPHICAL USER INTERFACE (GUI)
# =========================================
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

class MacChangerGUI(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Windows MAC Changer 🛡️ - By Mohit Ingale")
        self.geometry("550x550")
        self.resizable(False, False)
        
        self.adapters = get_ethernet_interfaces()
        self.current_adapter = None

        self.build_ui()
        
        if not self.adapters:
            self.log("[-] No physical adapters found. Check Admin rights.", error=True)
        else:
            self.log("[+] System initialized. Ready to spoof.")

    def build_ui(self):
        # Header
        header = ctk.CTkLabel(self, text="WINDOWS MAC CHANGER", font=("Arial", 24, "bold"), text_color="#00ff41")
        header.pack(pady=(20, 5))
        
        sub_header = ctk.CTkLabel(self, text="Select Interface to spoof or restore:", font=("Arial", 14))
        sub_header.pack(pady=(0, 15))

        # Adapter Dropdown
        adapter_names = list(self.adapters.keys()) if self.adapters else ["None Found"]
        self.adapter_combo = ctk.CTkOptionMenu(self, values=adapter_names, width=350, command=self.on_adapter_select)
        self.adapter_combo.pack(pady=10)

        # MAC Display
        self.mac_label = ctk.CTkLabel(self, text="Current MAC: --:--:--:--:--:--", font=("Consolas", 16, "bold"), text_color="#f1c40f")
        self.mac_label.pack(pady=10)

        # Custom Input
        self.mac_input = ctk.CTkEntry(self, width=350, placeholder_text="Enter Custom 12-Hex MAC (Optional)", font=("Consolas", 14))
        self.mac_input.pack(pady=15)

        # Buttons
        btn_frame = ctk.CTkFrame(self, fg_color="transparent")
        btn_frame.pack(pady=10)

        self.btn_random = ctk.CTkButton(btn_frame, text="Generate Random MAC", fg_color="#0074d9", hover_color="#005bb5", command=self.do_random_mac)
        self.btn_random.grid(row=0, column=0, padx=10, pady=10)

        self.btn_custom = ctk.CTkButton(btn_frame, text="Apply Custom MAC", fg_color="#d32f2f", hover_color="#9a0007", command=self.do_custom_mac)
        self.btn_custom.grid(row=0, column=1, padx=10, pady=10)

        self.btn_restore = ctk.CTkButton(btn_frame, text="Restore Default Factory MAC", width=300, fg_color="#27ae60", hover_color="#1e8449", command=self.do_restore_mac)
        self.btn_restore.grid(row=1, column=0, columnspan=2, pady=10)

        # Console Log (Replaces Colorama terminal)
        self.console = ctk.CTkTextbox(self, height=130, width=450, font=("Consolas", 12), state="disabled", fg_color="#0a0a0a", text_color="#e0e0e0")
        self.console.pack(pady=15)

        if self.adapters:
            self.on_adapter_select(adapter_names[0])

    def log(self, message, error=False):
        self.console.configure(state="normal")
        color_tag = "Error" if error else "Info"
        self.console.insert("end", f"{message}\n")
        self.console.see("end")
        self.console.configure(state="disabled")

    def on_adapter_select(self, adapter_name):
        self.current_adapter = adapter_name
        mac = self.adapters.get(adapter_name, {}).get("mac", "Unknown")
        formatted_mac = ":".join(mac[i:i+2] for i in range(0, 12, 2)) if len(mac) == 12 else mac
        self.mac_label.configure(text=f"Current MAC: {formatted_mac}")

    def execute_change(self, new_mac=None):
        if not self.current_adapter: return
        desc = self.adapters[self.current_adapter]["desc"]
        reg_path = get_registry_path(desc)

        if not reg_path:
            self.log("[-] Registry Path Not Found.", error=True)
            return

        def task():
            try:
                self.log(f"[*] Accessing Registry...")
                key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, reg_path, 0, winreg.KEY_SET_VALUE)
                
                if new_mac:
                    winreg.SetValueEx(key, "NetworkAddress", 0, winreg.REG_SZ, new_mac)
                    self.log(f"[+] Written new MAC: {new_mac}")
                else:
                    try:
                        winreg.DeleteValue(key, "NetworkAddress")
                        self.log("[+] Deleted Custom MAC (Restoring default).")
                    except FileNotFoundError:
                        self.log("[*] Adapter is already using default MAC.")
                winreg.CloseKey(key)

                self.log("[*] Disabling and Enabling Interface (Please wait...)")
                if restart_adapter(self.current_adapter):
                    self.log("[+] Network Refreshed Successfully!")
                else:
                    self.log("[-] Failed to restart adapter automatically.", error=True)

                self.adapters = get_ethernet_interfaces()
                self.on_adapter_select(self.current_adapter)

            except Exception as e:
                self.log(f"[-] Error: {e}", error=True)
            finally:
                self.btn_random.configure(state="normal")
                self.btn_custom.configure(state="normal")
                self.btn_restore.configure(state="normal")

        # Disable buttons while working
        self.btn_random.configure(state="disabled")
        self.btn_custom.configure(state="disabled")
        self.btn_restore.configure(state="disabled")
        
        # Run in thread so GUI doesn't freeze during time.sleep()
        threading.Thread(target=task, daemon=True).start()

    def do_random_mac(self):
        new_mac = generate_random_mac()
        self.log(f"[*] Generated Random MAC: {new_mac}")
        self.execute_change(new_mac)

    def do_custom_mac(self):
        custom_mac = self.mac_input.get()
        clean_mac = re.sub(r'[^a-fA-F0-9]', '', custom_mac).upper()
        
        if len(clean_mac) != 12:
            self.log("[-] Custom MAC must be exactly 12 valid hex characters.", error=True)
            return
        if clean_mac[1] not in ['2', '6', 'A', 'E']:
            self.log("[-] Invalid Windows Local MAC. 2nd char must be 2, 6, A, or E.", error=True)
            return
            
        self.log(f"[*] Applying Custom MAC: {clean_mac}")
        self.execute_change(clean_mac)

    def do_restore_mac(self):
        self.log("[*] Restoring original hardware MAC...")
        self.execute_change(new_mac=None)

if __name__ == "__main__":
    app = MacChangerGUI()
    app.mainloop()