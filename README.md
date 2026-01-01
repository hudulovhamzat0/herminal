# 🚀 Herminal

A beautiful, feature-rich terminal emulator for Linux with 20+ stunning themes, full ANSI color support, and extensive customization options.

![Herminal](https://img.shields.io/badge/version-1.0.0-purple)
![Python](https://img.shields.io/badge/python-3.8+-blue)
![License](https://img.shields.io/badge/license-MIT-green)
![Platform](https://img.shields.io/badge/platform-Linux-lightgrey)

## ✨ Features

### 🎨 Beautiful Themes
- **20+ Preset Themes** including:
  - 🌙 Purple Night (default)
  - 🌊 Ocean
  - 🌳 Forest
  - 🔥 Fire
  - 🌅 Sunset
  - 🧛 Dracula
  - 🎨 Monokai
  - ☀️ Solarized Dark
  - ❄️ Nord
  - 🍂 Gruvbox
  - 🗼 Tokyo Night
  - 🤖 Cyberpunk
  - 💚 Matrix
  - 🟠 Amber
  - 🌆 Synthwave
  - 🌸 Cherry Blossom
  - 💜 Lavender
  - 🍃 Mint
  - ☕ Coffee
  - 🌃 Midnight

### 🛠️ Customization
- **Full Color Customization**
  - Background color
  - Text color
  - Selection color
- **Font Settings**
  - Monospace font selection
  - Font size adjustment (8-24pt)
- **Transparency Control**
  - Adjustable window opacity (10-100%)
- **Cursor Styles**
  - Block
  - Underline
  - Beam

### ⌨️ Advanced Features
- Full ANSI color support (256 colors)
- Command history navigation (↑/↓ arrows)
- Tab completion support
- Copy/Paste functionality
- Right-click context menu
- Persistent settings across sessions
- Custom commands (`hsettings`, `hinfo`)

## 📦 Installation

### Option 1: Install from .deb Package (Recommended)

Download the latest `.deb` package from the [Releases](https://github.com/hudulovhamzat0/herminal/releases) page.

```bash
# Install the package
sudo dpkg -i herminal.deb

# Install dependencies if needed
sudo apt-get install -f
```

### Option 2: Install from Source

#### Prerequisites

- Python 3.8 or higher
- pip3

#### Install Dependencies

```bash
# Install system dependencies
sudo apt-get update
sudo apt-get install python3 python3-pip

# Install Python packages
pip3 install PyQt6 pyte ptyprocess
```

#### Clone and Run

```bash
# Clone the repository
git clone https://github.com/hudulovhamzat0/herminal.git
cd herminal

# Run directly
python3 herminal.py
```

#### Optional: Create System-wide Installation

```bash
# Copy script to system location
sudo cp herminal.py /usr/share/herminal/herminal.py

# Create launcher script
sudo tee /usr/bin/herminal << 'EOF'
#!/bin/bash
python3 /usr/share/herminal/herminal.py "$@"
EOF

sudo chmod +x /usr/bin/herminal

# Create desktop entry
sudo tee /usr/share/applications/herminal.desktop << 'EOF'
[Desktop Entry]
Version=1.0
Type=Application
Name=Herminal
Comment=Beautiful terminal emulator with 20+ themes
Exec=herminal
Icon=utilities-terminal
Terminal=false
Categories=System;TerminalEmulator;
Keywords=terminal;shell;console;command;
StartupNotify=true
EOF

# Update desktop database
sudo update-desktop-database
```

## 🚀 Usage

### Launch Herminal

```bash
# From command line
herminal

# Or search for "Herminal" in your application menu
```

### Custom Commands

Herminal includes special built-in commands:

- **`hsettings`** - Open the settings dialog to customize your terminal
- **`hinfo`** - Display keyboard shortcuts and help information

### Keyboard Shortcuts

#### Navigation Keys
- **↑ (Up Arrow)** - Previous command in history
- **↓ (Down Arrow)** - Next command in history
- **← (Left Arrow)** - Move cursor left
- **→ (Right Arrow)** - Move cursor right
- **Home** - Jump to beginning of line
- **End** - Jump to end of line

#### Enhanced Ctrl Key Support
- **Ctrl+C** - Interrupt/cancel current command
- **Ctrl+D** - EOF/logout (exit shell)
- **Ctrl+Z** - Suspend current process
- **Ctrl+R** - Reverse history search
- **Ctrl+L** - Clear screen
- **Ctrl+A** - Go to beginning of line
- **Ctrl+E** - Go to end of line
- **Ctrl+K** - Delete from cursor to end of line
- **Ctrl+U** - Delete entire line
- **Ctrl+W** - Delete word before cursor

### Context Menu

Right-click anywhere in the terminal to access:
- 📋 Copy
- 📄 Paste
- ⚙️ Settings
- ℹ️ Help & Info
- 🗑 Clear

## 🎨 Customization

Type `hsettings` in the terminal or right-click and select "Settings" to access:

1. **Colors**: Customize background, text, and selection colors
2. **Fonts**: Choose from monospace fonts and adjust size
3. **Transparency**: Make the terminal semi-transparent
4. **Cursor Style**: Select your preferred cursor appearance
5. **Preset Themes**: Quick-apply beautiful color schemes

All settings are automatically saved to `~/.hudul_terminal_settings.json` and persist across sessions.

## 📸 Screenshots

### Purple Night Theme (Default)
![Purple Night](https://via.placeholder.com/800x450/1a0a2e/e0d0ff?text=Purple+Night+Theme)

### Matrix Theme
![Matrix](https://via.placeholder.com/800x450/000000/00ff00?text=Matrix+Theme)

### Tokyo Night Theme
![Tokyo Night](https://via.placeholder.com/800x450/1a1b26/c0caf5?text=Tokyo+Night+Theme)

## 🔧 Building from Source

### Create Debian Package

```bash
# Create package structure
mkdir -p herminal_1.0.0/DEBIAN
mkdir -p herminal_1.0.0/usr/bin
mkdir -p herminal_1.0.0/usr/share/applications
mkdir -p herminal_1.0.0/usr/share/herminal

# Copy files (adjust paths as needed)
cp herminal.py herminal_1.0.0/usr/share/herminal/
cp DEBIAN/control herminal_1.0.0/DEBIAN/
cp DEBIAN/postinst herminal_1.0.0/DEBIAN/
cp usr/bin/herminal herminal_1.0.0/usr/bin/
cp usr/share/applications/herminal.desktop herminal_1.0.0/usr/share/applications/

# Make scripts executable
chmod +x herminal_1.0.0/usr/bin/herminal
chmod +x herminal_1.0.0/DEBIAN/postinst

# Build package
dpkg-deb --build --root-owner-group herminal_1.0.0

# Install
sudo dpkg -i herminal_1.0.0.deb
```

## 🐛 Troubleshooting

### Missing Dependencies

If you get import errors:

```bash
pip3 install --user PyQt6 pyte ptyprocess
```

### Permission Errors

If the terminal won't start:

```bash
# Check if the script is executable
ls -la /usr/share/herminal/herminal.py

# Make it executable if needed
sudo chmod +x /usr/share/herminal/herminal.py
```

### Settings Not Saving

Check that you have write permissions in your home directory:

```bash
touch ~/.hudul_terminal_settings.json
```

### Arrow Keys Not Working

Make sure your shell is properly configured. Add to your `~/.bashrc` or `~/.zshrc`:

```bash
export TERM=xterm-256color
```

## 🤝 Contributing

Contributions are welcome! Here's how you can help:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

### Ideas for Contributions

- Add more preset themes
- Implement tabs support
- Add split pane functionality
- Create more keyboard shortcuts
- Improve performance
- Add plugin system
- Create configuration import/export

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 👨‍💻 Author

**Hamzat Hudulov**
- GitHub: [@hudulovhamzat0](https://github.com/hudulovhamzat0)
- Email: hudulov8@gmail.com

## 🙏 Acknowledgments

- Built with [PyQt6](https://www.riverbankcomputing.com/software/pyqt/)
- Terminal emulation powered by [pyte](https://github.com/selectel/pyte)
- PTY handling via [ptyprocess](https://github.com/pexpect/ptyprocess)

## 📊 Project Stats

![GitHub stars](https://img.shields.io/github/stars/hudulovhamzat0/herminal?style=social)
![GitHub forks](https://img.shields.io/github/forks/hudulovhamzat0/herminal?style=social)
![GitHub issues](https://img.shields.io/github/issues/hudulovhamzat0/herminal)


## 💬 Support

If you encounter any issues or have questions:

1. Check the [Issues](https://github.com/hudulovhamzat0/herminal/issues) page
2. Create a new issue if your problem isn't already listed
3. Email: hudulov8@gmail.com

## ⭐ Star History

If you find Herminal useful, please consider giving it a star! It helps the project grow and motivates continued development.

---

Made with ❤️ by Hamzat Hudulov
