# 🛡️ PC Security Audit Tool

A lightweight Windows command-line tool that generates a detailed JSON report of your system's security posture — including TPM, Secure Boot, BitLocker, BIOS version, and installed software.

---

## 📋 Features

- ✅ System information (OS, architecture, processor, hostname)
- ✅ BIOS version via WMI
- ✅ TPM status (present, ready, enabled)
- ✅ Secure Boot detection
- ✅ BitLocker encryption status (C: drive)
- ✅ Full installed software list (name, version, publisher)
- ✅ Timestamped JSON output — no overwrites on repeated runs
- ✅ Auto-requests Administrator elevation if not already elevated

---

## 🖥️ Requirements

| Requirement | Details |
|---|---|
| OS | Windows 10 / 11 |
| Python | 3.8 or higher |
| Privileges | Administrator (auto-requested) |
| Dependencies | None (standard library only) |

---

## 🚀 Getting Started

### 1. Clone the repository

```bash
git clone https://github.com/Yash6012/pc-security-audit.git
cd pc-security-audit
```

### 2. Run the script

```bash
python security_audit.py
```

> The script will automatically request Administrator privileges via a UAC prompt if not already elevated.

### 3. Find your report

A timestamped JSON file will be saved in the same directory as the script:

```
Security_Audit_20260401_143201.json
```

---

## 📁 Project Structure

```
pc-security-audit/
│
├── security_audit.py       # Main script
├── README.md               # Readme file
└── .gitignore              # Excludes generated report files
```

---

## 📄 Sample Output

```json
{
    "System Information": {
        "Hostname": "DESKTOP-ABC123",
        "OS": "Windows",
        "OS Release": "11",
        "OS Version": "10.0.22631",
        "Architecture": "AMD64",
        "Processor": "Intel64 Family 6 Model 154",
        "Scan Time": "2026-04-01 14:32:01",
        "BIOS Version": "F.70"
    },
    "Security Audit": {
        "TPM": {
            "TpmPresent": true,
            "TpmReady": true,
            "TpmEnabled": true
        },
        "Secure Boot": "Enabled",
        "BitLocker": {
            "MountPoint": "C:",
            "ProtectionStatus": "On",
            "VolumeStatus": "FullyEncrypted"
        }
    },
    "Installed Software": [
        {
            "Name": "Google Chrome",
            "Version": "123.0.6312.122",
            "Publisher": "Google LLC"
        }
    ]
}
```

---

## 🔧 Building the Executable (Optional)

To compile the script into a standalone .exe:

    pip install pyinstaller
    pyinstaller --onefile --noconsole security_audit.py

The output will be in the `dist/` folder.

---

## ⚠️ Disclaimer

This tool is intended for **personal use and educational purposes only**. It reads local system data and does not transmit any information externally. Run only on systems you own or have explicit permission to audit.

---

## 📜 License

This project is licensed under the [MIT License](LICENSE).

---

## 🙋 Author

Made by **Yash Singh** — feel free to connect on [LinkedIn](https://www.linkedin.com/in/yashsingh73/) or check out more projects on [GitHub](https://github.com/Yash6012).