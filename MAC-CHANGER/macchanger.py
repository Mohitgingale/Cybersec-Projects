import subprocess
import random
import ctypes
import sys
import os
import time
from colorama import init, Fore, Style

# =========================================
# INIT COLORAMA
# =========================================

init(autoreset=True)

# =========================================
# AUTO ADMIN
# =========================================

def run_as_admin():

    try:
        admin = ctypes.windll.shell32.IsUserAnAdmin()

    except:
        admin = False

    if not admin:

        ctypes.windll.shell32.ShellExecuteW(
            None,
            "runas",
            sys.executable,
            " ".join(sys.argv),
            None,
            1
        )

        sys.exit()


run_as_admin()

# =========================================
# CLEAR SCREEN + BANNER
# =========================================

def clear():

    os.system("cls")

    print(
        Fore.GREEN + Style.BRIGHT + r"""
███╗   ███╗ █████╗  ██████╗
████╗ ████║██╔══██╗██╔════╝
██╔████╔██║███████║██║
██║╚██╔╝██║██╔══██║██║
██║ ╚═╝ ██║██║  ██║╚██████╗
╚═╝     ╚═╝╚═╝  ╚═╝ ╚═════╝
"""
    )

    print(
        Fore.CYAN + Style.BRIGHT +
        "         WINDOWS MAC CHANGER"
    )

    print(
        Fore.YELLOW +
        "         Created By Mohit Ingale\n"
    )

    print(
        Fore.BLUE +
        "=" * 55
    )


# =========================================
# LOADING ANIMATION
# =========================================

def loading(text):

    print()

    for i in range(3):

        print(
            Fore.YELLOW +
            f"[*] {text}{'.' * (i + 1)}"
        )

        time.sleep(0.4)


# =========================================
# RANDOM MAC GENERATOR
# =========================================

def generate_random_mac():

    mac = [
        0x02,
        random.randint(0x00, 0x7F),
        random.randint(0x00, 0xFF),
        random.randint(0x00, 0xFF),
        random.randint(0x00, 0xFF),
        random.randint(0x00, 0xFF)
    ]

    return ''.join(map(lambda x: "%02X" % x, mac))


# =========================================
# GET ETHERNET INTERFACES
# =========================================

def get_ethernet_interfaces():

    interfaces = []

    try:

        output = subprocess.check_output(
            "netsh interface show interface",
            shell=True
        ).decode(errors="ignore")

        lines = output.splitlines()

        for line in lines:

            line = line.strip()

            if (
                line
                and "Dedicated" in line
            ):

                parts = line.split()

                if len(parts) >= 4:

                    interface_name = " ".join(parts[3:])

                    interfaces.append(interface_name)

    except Exception as e:

        print(
            Fore.RED +
            f"[-] Error: {e}"
        )

    return interfaces


# =========================================
# SHOW CURRENT MAC
# =========================================

def show_current_mac(interface):

    clear()

    print(
        Fore.CYAN +
        Style.BRIGHT +
        "\n========== CURRENT MAC ==========\n"
    )

    try:

        output = subprocess.check_output(
            "getmac /v /fo list",
            shell=True
        ).decode(errors="ignore")

        adapters = output.split("\n\n")

        found = False

        for adapter in adapters:

            if interface.lower() in adapter.lower():

                print(
                    Fore.GREEN +
                    adapter
                )

                found = True

        if not found:

            print(
                Fore.RED +
                "[-] MAC Not Found"
            )

    except Exception as e:

        print(
            Fore.RED +
            f"[-] Error: {e}"
        )

    print(
        Fore.CYAN +
        "\n================================"
    )


# =========================================
# FIND REGISTRY PATH
# =========================================

def get_registry_path(interface_name):

    base = (
        r'HKEY_LOCAL_MACHINE\SYSTEM\CurrentControlSet'
        r'\Control\Class'
        r'\{4d36e972-e325-11ce-bfc1-08002be10318}'
    )

    for i in range(0, 40):

        key = f"{i:04}"

        try:

            cmd = f'reg query "{base}\\{key}"'

            output = subprocess.check_output(
                cmd,
                shell=True
            ).decode(errors="ignore")

            if interface_name.lower() in output.lower():

                return f"{base}\\{key}"

        except:
            pass

    return None


# =========================================
# REFRESH NETWORK
# =========================================

def refresh_network():

    loading("Refreshing Network")

    subprocess.call(
        "ipconfig /release",
        shell=True
    )

    subprocess.call(
        "ipconfig /flushdns",
        shell=True
    )

    subprocess.call(
        "ipconfig /renew",
        shell=True
    )

    print(
        Fore.GREEN +
        "\n[+] Network Refreshed"
    )


# =========================================
# CHANGE MAC
# =========================================

def change_mac(interface_name, new_mac):

    reg_path = get_registry_path(interface_name)

    if not reg_path:

        print(
            Fore.RED +
            "[-] Registry Path Not Found"
        )

        return

    try:

        loading("Disabling Interface")

        subprocess.call(
            f'netsh interface set interface "{interface_name}" disable',
            shell=True
        )

        time.sleep(3)

        loading("Writing MAC Address")

        cmd = (
            f'reg add "{reg_path}" '
            f'/v NetworkAddress '
            f'/d {new_mac} /f'
        )

        subprocess.call(cmd, shell=True)

        time.sleep(3)

        loading("Enabling Interface")

        subprocess.call(
            f'netsh interface set interface "{interface_name}" enable',
            shell=True
        )

        time.sleep(8)

        refresh_network()

        print(
            Fore.GREEN +
            Style.BRIGHT +
            "\n[+] MAC Changed Successfully"
        )

    except Exception as e:

        print(
            Fore.RED +
            f"[-] Error: {e}"
        )


# =========================================
# RESTORE DEFAULT MAC
# =========================================

def restore_default_mac(interface_name):

    reg_path = get_registry_path(interface_name)

    if not reg_path:

        print(
            Fore.RED +
            "[-] Registry Path Not Found"
        )

        return

    try:

        loading("Disabling Interface")

        subprocess.call(
            f'netsh interface set interface "{interface_name}" disable',
            shell=True
        )

        time.sleep(3)

        loading("Removing Custom MAC")

        cmd = (
            f'reg delete "{reg_path}" '
            f'/v NetworkAddress /f'
        )

        subprocess.call(cmd, shell=True)

        time.sleep(3)

        loading("Enabling Interface")

        subprocess.call(
            f'netsh interface set interface "{interface_name}" enable',
            shell=True
        )

        time.sleep(8)

        refresh_network()

        print(
            Fore.GREEN +
            Style.BRIGHT +
            "\n[+] Default MAC Restored"
        )

    except Exception as e:

        print(
            Fore.RED +
            f"[-] Error: {e}"
        )


# =========================================
# SELECT INTERFACE
# =========================================

def select_interface():

    interfaces = get_ethernet_interfaces()

    if not interfaces:

        print(
            Fore.RED +
            "[-] No Interfaces Found"
        )

        return None

    print(
        Fore.CYAN +
        Style.BRIGHT +
        "\n========== INTERFACES ==========\n"
    )

    for i, iface in enumerate(interfaces):

        print(
            Fore.YELLOW +
            f"{i + 1}. {iface}"
        )

    try:

        choice = int(
            input(
                Fore.GREEN +
                "\nSelect Interface > "
            )
        ) - 1

        if choice < 0 or choice >= len(interfaces):

            print(
                Fore.RED +
                "[-] Invalid Selection"
            )

            return None

        return interfaces[choice]

    except:

        print(
            Fore.RED +
            "[-] Invalid Input"
        )

        return None


# =========================================
# MAIN MENU
# =========================================

def main():

    while True:

        clear()

        print(
            Fore.MAGENTA + Style.BRIGHT + """
1. Show Interfaces
2. Show Current MAC
3. Generate Random MAC
4. Change To Random MAC
5. Change To Custom MAC
6. Restore Default MAC
7. Exit
"""
        )

        choice = input(
            Fore.GREEN +
            Style.BRIGHT +
            "Select Option > "
        )

        # =====================================
        # SHOW INTERFACES
        # =====================================

        if choice == "1":

            clear()

            interfaces = get_ethernet_interfaces()

            print(
                Fore.CYAN +
                Style.BRIGHT +
                "\n========== INTERFACES ==========\n"
            )

            if not interfaces:

                print(
                    Fore.RED +
                    "[-] No Interfaces Found"
                )

            else:

                for i, iface in enumerate(interfaces):

                    print(
                        Fore.YELLOW +
                        f"{i + 1}. {iface}"
                    )

            input(
                Fore.GREEN +
                "\nPress Enter To Continue..."
            )

        # =====================================
        # SHOW CURRENT MAC
        # =====================================

        elif choice == "2":

            interface = select_interface()

            if interface:

                show_current_mac(interface)

            input(
                Fore.GREEN +
                "\nPress Enter To Continue..."
            )

        # =====================================
        # GENERATE RANDOM MAC
        # =====================================

        elif choice == "3":

            clear()

            mac = generate_random_mac()

            print(
                Fore.GREEN +
                Style.BRIGHT +
                "\n[+] Generated MAC:\n"
            )

            print(
                Fore.YELLOW +
                mac
            )

            input(
                Fore.GREEN +
                "\nPress Enter To Continue..."
            )

        # =====================================
        # CHANGE RANDOM MAC
        # =====================================

        elif choice == "4":

            clear()

            interface = select_interface()

            if interface:

                new_mac = generate_random_mac()

                print(
                    Fore.GREEN +
                    f"\n[+] Generated MAC: {new_mac}"
                )

                confirm = input(
                    Fore.YELLOW +
                    "\nProceed? (y/n): "
                )

                if confirm.lower() == "y":

                    change_mac(interface, new_mac)

            input(
                Fore.GREEN +
                "\nPress Enter To Continue..."
            )

        # =====================================
        # CHANGE CUSTOM MAC
        # =====================================

        elif choice == "5":

            clear()

            interface = select_interface()

            if interface:

                print(
                    Fore.CYAN +
                    "\nExample: 001122334455"
                )

                new_mac = input(
                    Fore.GREEN +
                    "\nEnter New MAC Address > "
                )

                confirm = input(
                    Fore.YELLOW +
                    "\nProceed? (y/n): "
                )

                if confirm.lower() == "y":

                    change_mac(interface, new_mac)

            input(
                Fore.GREEN +
                "\nPress Enter To Continue..."
            )

        # =====================================
        # RESTORE DEFAULT MAC
        # =====================================

        elif choice == "6":

            clear()

            interface = select_interface()

            if interface:

                confirm = input(
                    Fore.YELLOW +
                    "\nRestore Original MAC? (y/n): "
                )

                if confirm.lower() == "y":

                    restore_default_mac(interface)

            input(
                Fore.GREEN +
                "\nPress Enter To Continue..."
            )

        # =====================================
        # EXIT
        # =====================================

        elif choice == "7":

            print(
                Fore.RED +
                Style.BRIGHT +
                "\nGoodbye..."
            )

            sys.exit()

        else:

            print(
                Fore.RED +
                "\n[-] Invalid Option"
            )

            time.sleep(1)


# =========================================
# START
# =========================================

if __name__ == "__main__":
    main()