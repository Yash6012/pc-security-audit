import sys
import os
import subprocess
import json
import ctypes
import platform
import time
from datetime import datetime

# --- CONFIGURATION ---
SCAN_TIME = datetime.now()
OUTPUT_FILENAME = f"Security_Audit_{SCAN_TIME.strftime('%Y%m%d_%H%M%S')}.json"


# --- UTILITIES ---

def log(message: str) -> None:
    """Prints a formatted status message to the console."""
    print(f"  {message}")


def is_admin() -> bool:
    """Returns True if the script is running with Administrator privileges."""
    try:
        return bool(ctypes.windll.shell32.IsUserAnAdmin())
    except Exception:
        return False


def run_powershell(cmd: str) -> str:
    """Runs a PowerShell command and returns its stdout output."""
    try:
        result = subprocess.run(
            ["powershell", "-NoProfile", "-Command", cmd],
            capture_output=True,
            text=True,
            encoding="utf-8",
            creationflags=subprocess.CREATE_NO_WINDOW,
        )
        return result.stdout.strip()
    except Exception as e:
        return f"Error: {e}"


# --- COLLECTION FUNCTIONS ---

def get_basic_info() -> dict:
    """Collects basic OS and hardware information."""
    log("Gathering system information...")
    return {
        "Hostname": platform.node(),
        "OS": platform.system(),
        "OS Release": platform.release(),
        "OS Version": platform.version(),
        "Architecture": platform.machine(),
        "Processor": platform.processor(),
        "Scan Time": SCAN_TIME.strftime("%Y-%m-%d %H:%M:%S"),
    }


def get_bios_version() -> str:
    """Returns the BIOS version string via WMI."""
    log("Fetching BIOS version...")
    if os.name != "nt":
        return "N/A (non-Windows)"
    output = run_powershell(
        "Get-CimInstance Win32_BIOS | Select-Object -ExpandProperty SMBIOSBIOSVersion"
    )
    return output or "Unknown"


def get_security_audit() -> dict:
    """Checks TPM, Secure Boot, and BitLocker status. Requires Admin privileges."""
    security_data = {}

    log("Checking TPM status...")
    tpm_output = run_powershell(
        "Get-Tpm | Select-Object TpmPresent, TpmReady, TpmEnabled | ConvertTo-Json"
    )
    try:
        security_data["TPM"] = json.loads(tpm_output)
    except Exception:
        security_data["TPM"] = "Unavailable"

    log("Checking Secure Boot...")
    sb_output = run_powershell("Confirm-SecureBootUEFI")
    security_data["Secure Boot"] = "Enabled" if "True" in sb_output else "Disabled / Legacy BIOS"

    log("Checking BitLocker status (C: drive)...")
    bl_output = run_powershell(
        "Get-BitLockerVolume -MountPoint C: "
        "| Select-Object MountPoint, ProtectionStatus, VolumeStatus "
        "| ConvertTo-Json"
    )
    try:
        security_data["BitLocker"] = json.loads(bl_output)
    except Exception:
        security_data["BitLocker"] = "Unavailable"

    return security_data


def get_installed_software() -> list:
    """Scans the Windows registry for installed applications."""
    log("Scanning installed software (this may take 10–20 seconds)...")

    if os.name != "nt":
        return []

    ps_script = """
    [Console]::OutputEncoding = [System.Text.Encoding]::UTF8
    $paths = @(
        'HKLM:\\Software\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\*',
        'HKLM:\\Software\\Wow6432Node\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\*',
        'HKCU:\\Software\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\*'
    )
    Get-ItemProperty -Path $paths -ErrorAction SilentlyContinue |
        Select-Object DisplayName, DisplayVersion, Publisher |
        Where-Object { $_.DisplayName -ne $null } |
        Sort-Object DisplayName -Unique |
        ConvertTo-Json -Compress
    """

    output = run_powershell(ps_script)
    if not output:
        return []

    try:
        data = json.loads(output)
        if isinstance(data, dict):
            data = [data]
        return [
            {
                "Name": item.get("DisplayName", "Unknown"),
                "Version": item.get("DisplayVersion", "Unknown"),
                "Publisher": item.get("Publisher", "Unknown"),
            }
            for item in data
        ]
    except json.JSONDecodeError:
        return [{"Error": "Could not decode PowerShell output"}]
    except Exception as e:
        return [{"Error": f"Scan failed: {e}"}]


# --- ENTRY POINT ---

def main() -> None:
    if not is_admin():
        print("[*] Administrator privileges are required. Requesting elevation...")
        try:
            script_path = os.path.abspath(__file__)
            ctypes.windll.shell32.ShellExecuteW(
                None, "runas", sys.executable, f'"{script_path}"', None, 1
            )
        except Exception as e:
            print(f"[!] Elevation failed: {e}")
            input("Press Enter to exit...")
        sys.exit()

    os.system("cls" if os.name == "nt" else "clear")
    print("=" * 44)
    print("   PC SYSTEM INFO & SECURITY AUDIT TOOL")
    print("=" * 44)

    try:
        report = {
            "System Information": {
                **get_basic_info(),
                "BIOS Version": get_bios_version(),
            },
            "Security Audit": get_security_audit(),
            "Installed Software": get_installed_software(),
        }

        script_dir = os.path.dirname(os.path.abspath(__file__))
        file_path = os.path.join(script_dir, OUTPUT_FILENAME)
        log(f"Saving report to: {file_path}")

        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(report, f, indent=4, ensure_ascii=False)

        print("\n" + "=" * 44)
        print("  [OK] Report saved successfully:")
        print(f"       {file_path}")
        print("=" * 44)
        print("\nExiting in 3 seconds...")
        time.sleep(3)

    except Exception as e:
        print(f"\n[!] Critical error: {e}")
        input("Press Enter to close...")


if __name__ == "__main__":
    main()