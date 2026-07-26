<div align="center">

# 🔐 LockIt

### Secure your files. Keep control of your data.

A modern, lightweight desktop application for **encrypting and decrypting files locally**, built with Python and PySide6.

[![Release](https://img.shields.io/github/v/release/Ariyan-Ebrahimi/Lockit?style=for-the-badge)](https://github.com/Ariyan-Ebrahimi/Lockit/releases/latest)
[![Windows](https://img.shields.io/badge/Windows-10%20%7C%2011-blue?style=for-the-badge\&logo=windows11)](https://github.com/Ariyan-Ebrahimi/Lockit/releases/latest)
[![Python](https://img.shields.io/badge/Python-3.12+-3776AB?style=for-the-badge\&logo=python\&logoColor=white)](https://www.python.org/)
[![License](https://img.shields.io/github/license/Ariyan-Ebrahimi/Lockit?style=for-the-badge)](LICENSE)

**[Download for Windows](https://github.com/Ariyan-Ebrahimi/Lockit/releases/latest)** · **[Report a Bug](https://github.com/Ariyan-Ebrahimi/Lockit/issues)** · **[Source Code](https://github.com/Ariyan-Ebrahimi/Lockit)**

</div>

---

## About LockIt

**LockIt** is a desktop file-encryption application designed to make protecting files simple and accessible.

Instead of dealing with command-line utilities or complicated configuration, LockIt provides a clean graphical interface for encrypting and decrypting files directly on your computer.

Encryption and decryption are performed **locally on the user's device**.

LockIt is packaged as a standalone Windows application, so end users do **not** need Python, PySide6, PyInstaller, or other development tools installed.

---

## ✨ Features

* 🔒 **File Encryption** — Protect files through a simple desktop interface
* 🔓 **File Decryption** — Restore encrypted files using LockIt
* 🛡️ **Local Processing** — Encryption and decryption happen on your device
* 🔑 **Password-Based Protection** — Protect encrypted data with a password
* 📊 **Password Strength Feedback** — Visual feedback while choosing passwords
* 🖥️ **Modern Interface** — Clean desktop UI powered by PySide6
* 🌙 **Theme Support** — Modern application theming
* 📁 **File Selection Interface** — Easily select files for processing
* ⚡ **Background Processing** — Cryptographic operations run without freezing the interface
* 📝 **Application Logging** — Logging support for diagnostics and troubleshooting
* 📦 **Windows Installer** — Standard installation experience for Windows
* 🔗 **Desktop Shortcut** — Optional desktop access after installation
* 🚀 **Standalone Distribution** — Python is not required for end users

---

## 📥 Download

### Windows

The easiest way to install LockIt is to download the latest Windows installer from:

### **[⬇️ Download Latest Release](https://github.com/Ariyan-Ebrahimi/Lockit/releases/latest)**

Open **Assets** and download:

```text
LockIt-Setup-0.1.0.exe
```

Then run the installer and follow the setup wizard.

The installer handles the application files and creates the required Windows shortcuts.

> **No Python installation is required.**

---

## 🖥️ System Requirements

| Requirement         | Recommended                                         |
| ------------------- | --------------------------------------------------- |
| Operating System    | Windows 10 / Windows 11                             |
| Architecture        | 64-bit                                              |
| Python for users    | Not required                                        |
| Internet connection | Not required for normal local encryption/decryption |

---

## 🚀 Installation

1. Download the latest installer from **Releases**.
2. Run `LockIt-Setup-0.1.0.exe`.
3. Follow the installation wizard.
4. Launch **LockIt** from the Desktop or Start Menu.
5. Select a file and start encrypting or decrypting.

That's it.

---

## 🔐 Security

LockIt is designed around local file processing.

Your files do not need to be uploaded to an external server in order to perform normal encryption or decryption operations.

However, encryption software should always be used carefully.

### Important

* Keep backups of important files.
* Use strong and unique passwords.
* Do not lose the password required to decrypt your files.
* Test encryption and decryption before using LockIt with critical data.
* Download installers only from the official repository.
* Do not interrupt the application while important file operations are in progress.

> **LockIt is provided without warranty. Always maintain backups of important data.**

---

## 🧰 Technology Stack

LockIt is built using:

| Technology                   | Purpose                          |
| ---------------------------- | -------------------------------- |
| **Python**                   | Core application                 |
| **PySide6 / Qt**             | Desktop user interface           |
| **Cryptographic components** | File encryption and key handling |
| **Loguru**                   | Application logging              |
| **PyInstaller**              | Standalone Windows packaging     |
| **Inno Setup**               | Windows installer                |

---

## 📂 Project Structure

```text
Lockit/
│
├── assets/
│   └── icons/
│
├── config/
│   ├── constants.py
│   ├── paths.py
│   └── settings.py
│
├── core/
│   ├── crypto/
│   ├── files/
│   ├── security/
│   └── validators/
│
├── services/
│   ├── encryption_service.py
│   ├── decryption_service.py
│   └── settings_service.py
│
├── ui/
│   ├── dialogs/
│   ├── layouts/
│   ├── styles/
│   ├── widgets/
│   └── windows/
│
├── utils/
├── workers/
├── tests/
├── docs/
├── installer/
│
├── main.py
├── requirements.txt
├── requirements-dev.txt
├── pyproject.toml
├── LockIt.spec
├── build_installer.bat
├── build_installer.ps1
├── LICENSE
└── README.md
```

---

## 💻 Development

Want to run LockIt from source?

### 1. Clone the repository

```bash
git clone https://github.com/Ariyan-Ebrahimi/Lockit.git
cd Lockit
```

### 2. Create a virtual environment

```bash
python -m venv .venv
```

### 3. Activate it

#### Windows PowerShell

```powershell
.venv\Scripts\Activate.ps1
```

#### Windows Command Prompt

```cmd
.venv\Scripts\activate.bat
```

### 4. Install dependencies

```bash
pip install -r requirements.txt
```

### 5. Run LockIt

```bash
python main.py
```

---

## 🔨 Building LockIt

The repository includes scripts for creating the standalone Windows application and installer.

On Windows, run:

```text
build_installer.bat
```

The build pipeline uses **PyInstaller** to package LockIt and **Inno Setup** to create the final Windows installer.

The generated Setup can then be distributed as a standalone application.

End users do not need the source code or Python environment.

---

## 🗺️ Roadmap

LockIt is under active development.

Planned improvements include:

* [ ] Drag-and-drop improvements
* [ ] Multi-file encryption
* [ ] Multi-file decryption
* [ ] Improved progress reporting
* [ ] Additional security options
* [ ] Better error recovery
* [ ] Automatic update support
* [ ] Installer improvements
* [ ] UI/UX refinements
* [ ] Expanded automated testing

---

## 🐛 Bug Reports & Feature Requests

Found a bug or have an idea?

Use **[GitHub Issues](https://github.com/Ariyan-Ebrahimi/Lockit/issues)** to report problems or suggest improvements.

When reporting a bug, please include:

* LockIt version
* Windows version
* What you were trying to do
* What happened
* Steps to reproduce the issue

Please avoid attaching sensitive or private files.

---

## 🤝 Contributing

Contributions are welcome.

To contribute:

1. Fork the repository.
2. Create a feature branch.
3. Make your changes.
4. Test the application.
5. Commit your changes.
6. Open a Pull Request.

Please keep changes focused and explain what the Pull Request improves or fixes.

---

## 📄 License

LockIt is distributed under the **MIT License**.

See [`LICENSE`](LICENSE) for more information.

---

## 👨‍💻 Author

**Ariyan Ebrahimi**

GitHub: [@Ariyan-Ebrahimi](https://github.com/Ariyan-Ebrahimi)

---

## ⭐ Support

If you find LockIt useful, consider giving the repository a **Star ⭐**.

It helps others discover the project and supports future development.

<div align="center">

### 🔐 LockIt

**Simple. Local. Secure.**

[Download](https://github.com/Ariyan-Ebrahimi/Lockit/releases/latest) · [Issues](https://github.com/Ariyan-Ebrahimi/Lockit/issues) · [License](LICENSE)

</div>
