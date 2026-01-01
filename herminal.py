import sys
import os
import threading
import re
import json
from PyQt6.QtWidgets import (QApplication, QPlainTextEdit, QVBoxLayout, 
                              QWidget, QLabel, QMenu, QMessageBox, QDialog,
                              QFormLayout, QPushButton, QColorDialog, 
                              QSpinBox, QFontComboBox, QHBoxLayout, QComboBox)
from PyQt6.QtCore import pyqtSignal, QObject, Qt
from PyQt6.QtGui import (QTextCharFormat, QColor, QTextCursor, QFont, 
                         QAction)
import pyte
import ptyprocess


class Communicate(QObject):
    output_signal = pyqtSignal(str, dict)
    status_signal = pyqtSignal(str)
    settings_signal = pyqtSignal()
    info_signal = pyqtSignal()


class ANSIParser:
    """Parse ANSI escape sequences for colors and styles"""
    
    ANSI_COLORS = {
        '30': QColor(40, 40, 40),      # Black
        '31': QColor(255, 100, 100),    # Red
        '32': QColor(150, 255, 150),    # Green
        '33': QColor(255, 220, 100),    # Yellow
        '34': QColor(150, 150, 255),    # Blue
        '35': QColor(255, 150, 255),    # Magenta
        '36': QColor(150, 255, 255),    # Cyan
        '37': QColor(240, 240, 240),    # White
        # Bright colors
        '90': QColor(128, 128, 128),    # Bright Black
        '91': QColor(255, 150, 150),    # Bright Red
        '92': QColor(200, 255, 200),    # Bright Green
        '93': QColor(255, 255, 150),    # Bright Yellow
        '94': QColor(180, 180, 255),    # Bright Blue
        '95': QColor(255, 180, 255),    # Bright Magenta
        '96': QColor(180, 255, 255),    # Bright Cyan
        '97': QColor(255, 255, 255),    # Bright White
    }
    
    @staticmethod
    def parse_color(code):
        """Convert ANSI color code to QColor"""
        return ANSIParser.ANSI_COLORS.get(code, QColor(220, 200, 255))


class SettingsDialog(QDialog):
    """Settings dialog for customizing terminal appearance"""
    
    def __init__(self, parent=None, current_settings=None):
        super().__init__(parent)
        self.setWindowTitle("⚙️ Terminal Settings")
        self.setModal(True)
        self.resize(500, 450)
        
        self.settings = current_settings or {}
        self.setup_ui()
    
    def apply_theme_to_dialog(self, settings):
        """Apply current theme colors to the settings dialog"""
        bg_color = settings['bg_color']
        text_color = settings['text_color']
        sel_color = settings['selection_color']
        
        # Darken background for dialog
        bg_q = QColor(bg_color)
        dialog_bg = QColor(
            max(0, bg_q.red() - 20),
            max(0, bg_q.green() - 20),
            max(0, bg_q.blue() - 20)
        ).name()
        
        # Lighten selection color for buttons
        sel_q = QColor(sel_color)
        btn_hover = sel_q.lighter(120).name()
        
        # Style the dialog with current theme
        self.setStyleSheet(f"""
            QDialog {{
                background-color: {dialog_bg};
                color: {text_color};
            }}
            QLabel {{
                color: {text_color};
            }}
            QPushButton {{
                background-color: {sel_color};
                color: white;
                border: none;
                border-radius: 4px;
                padding: 6px 12px;
            }}
            QPushButton:hover {{
                background-color: {btn_hover};
            }}
            QSpinBox, QFontComboBox, QComboBox {{
                background-color: {bg_color};
                color: {text_color};
                border: 1px solid {sel_color};
                border-radius: 3px;
                padding: 4px;
            }}
            QSpinBox::up-button, QSpinBox::down-button {{
                background-color: {sel_color};
                border: none;
            }}
            QSpinBox::up-button:hover, QSpinBox::down-button:hover {{
                background-color: {btn_hover};
            }}
            QComboBox::drop-down {{
                background-color: {sel_color};
                border: none;
            }}
            QComboBox QAbstractItemView {{
                background-color: {dialog_bg};
                color: {text_color};
                selection-background-color: {sel_color};
            }}
        """)
        
    def setup_ui(self):
        layout = QVBoxLayout()
        
        # Form layout for settings
        form = QFormLayout()
        
        # Background color
        bg_layout = QHBoxLayout()
        self.bg_color = self.settings.get('bg_color', '#1a0a2e')
        self.bg_preview = QLabel()
        self.bg_preview.setFixedSize(50, 30)
        self.bg_preview.setStyleSheet(f"background-color: {self.bg_color}; border: 1px solid #888;")
        bg_btn = QPushButton("Choose Color")
        bg_btn.clicked.connect(lambda: self.choose_color('bg'))
        bg_layout.addWidget(self.bg_preview)
        bg_layout.addWidget(bg_btn)
        bg_layout.addStretch()
        form.addRow("Background Color:", bg_layout)
        
        # Text color
        text_layout = QHBoxLayout()
        self.text_color = self.settings.get('text_color', '#e0d0ff')
        self.text_preview = QLabel()
        self.text_preview.setFixedSize(50, 30)
        self.text_preview.setStyleSheet(f"background-color: {self.text_color}; border: 1px solid #888;")
        text_btn = QPushButton("Choose Color")
        text_btn.clicked.connect(lambda: self.choose_color('text'))
        text_layout.addWidget(self.text_preview)
        text_layout.addWidget(text_btn)
        text_layout.addStretch()
        form.addRow("Text Color:", text_layout)
        
        # Selection color
        sel_layout = QHBoxLayout()
        self.sel_color = self.settings.get('selection_color', '#6a4c93')
        self.sel_preview = QLabel()
        self.sel_preview.setFixedSize(50, 30)
        self.sel_preview.setStyleSheet(f"background-color: {self.sel_color}; border: 1px solid #888;")
        sel_btn = QPushButton("Choose Color")
        sel_btn.clicked.connect(lambda: self.choose_color('sel'))
        sel_layout.addWidget(self.sel_preview)
        sel_layout.addWidget(sel_btn)
        sel_layout.addStretch()
        form.addRow("Selection Color:", sel_layout)
        
        # Font family
        self.font_combo = QFontComboBox()
        self.font_combo.setFontFilters(QFontComboBox.FontFilter.MonospacedFonts)
        current_font = self.settings.get('font_family', 'Consolas')
        self.font_combo.setCurrentFont(QFont(current_font))
        form.addRow("Font Family:", self.font_combo)
        
        # Font size
        self.font_size = QSpinBox()
        self.font_size.setRange(8, 24)
        self.font_size.setValue(self.settings.get('font_size', 11))
        form.addRow("Font Size:", self.font_size)
        
        # Cursor style
        self.cursor_style = QComboBox()
        self.cursor_style.addItems(["Block", "Underline", "Beam"])
        self.cursor_style.setCurrentText(self.settings.get('cursor_style', 'Block'))
        form.addRow("Cursor Style:", self.cursor_style)
        
        # Opacity/Transparency
        self.opacity = QSpinBox()
        self.opacity.setRange(10, 100)
        self.opacity.setValue(self.settings.get('opacity', 100))
        self.opacity.setSuffix("%")
        self.opacity.setToolTip("Lower values make the window more transparent")
        form.addRow("Transparency:", self.opacity)
        
        layout.addLayout(form)
        
        # Preset themes
        layout.addWidget(QLabel("\n📦 Preset Themes:"))
        
        # Create scrollable theme grid
        themes_widget = QWidget()
        themes_layout = QVBoxLayout()
        
        # Row 1
        row1 = QHBoxLayout()
        themes = [
            ('purple', '🌙 Purple Night'),
            ('ocean', '🌊 Ocean'),
            ('forest', '🌳 Forest'),
            ('fire', '🔥 Fire'),
            ('sunset', '🌅 Sunset')
        ]
        for theme_id, theme_name in themes:
            btn = QPushButton(theme_name)
            btn.clicked.connect(lambda checked, t=theme_id: self.apply_preset(t))
            row1.addWidget(btn)
        themes_layout.addLayout(row1)
        
        # Row 2
        row2 = QHBoxLayout()
        themes = [
            ('dracula', '🧛 Dracula'),
            ('monokai', '🎨 Monokai'),
            ('solarized_dark', '☀️ Solarized Dark'),
            ('nord', '❄️ Nord'),
            ('gruvbox', '🍂 Gruvbox')
        ]
        for theme_id, theme_name in themes:
            btn = QPushButton(theme_name)
            btn.clicked.connect(lambda checked, t=theme_id: self.apply_preset(t))
            row2.addWidget(btn)
        themes_layout.addLayout(row2)
        
        # Row 3
        row3 = QHBoxLayout()
        themes = [
            ('tokyo_night', '🗼 Tokyo Night'),
            ('cyberpunk', '🤖 Cyberpunk'),
            ('matrix', '💚 Matrix'),
            ('amber', '🟠 Amber'),
            ('synthwave', '🌆 Synthwave')
        ]
        for theme_id, theme_name in themes:
            btn = QPushButton(theme_name)
            btn.clicked.connect(lambda checked, t=theme_id: self.apply_preset(t))
            row3.addWidget(btn)
        themes_layout.addLayout(row3)
        
        # Row 4
        row4 = QHBoxLayout()
        themes = [
            ('cherry_blossom', '🌸 Cherry Blossom'),
            ('lavender', '💜 Lavender'),
            ('mint', '🍃 Mint'),
            ('coffee', '☕ Coffee'),
            ('midnight', '🌃 Midnight')
        ]
        for theme_id, theme_name in themes:
            btn = QPushButton(theme_name)
            btn.clicked.connect(lambda checked, t=theme_id: self.apply_preset(t))
            row4.addWidget(btn)
        themes_layout.addLayout(row4)
        
        themes_widget.setLayout(themes_layout)
        layout.addWidget(themes_widget)
        
        # Buttons
        button_layout = QHBoxLayout()
        
        save_btn = QPushButton("💾 Save")
        save_btn.clicked.connect(self.accept)
        save_btn.setStyleSheet("""
            QPushButton {
                background-color: #6a4c93;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 8px 20px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #8b5fbf;
            }
        """)
        
        cancel_btn = QPushButton("❌ Cancel")
        cancel_btn.clicked.connect(self.reject)
        cancel_btn.setStyleSheet("""
            QPushButton {
                background-color: #555;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 8px 20px;
            }
            QPushButton:hover {
                background-color: #777;
            }
        """)
        
        reset_btn = QPushButton("🔄 Reset")
        reset_btn.clicked.connect(self.reset_defaults)
        reset_btn.setStyleSheet("""
            QPushButton {
                background-color: #d9534f;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 8px 20px;
            }
            QPushButton:hover {
                background-color: #c9302c;
            }
        """)
        
        button_layout.addWidget(reset_btn)
        button_layout.addStretch()
        button_layout.addWidget(cancel_btn)
        button_layout.addWidget(save_btn)
        
        layout.addLayout(button_layout)
        
        self.setLayout(layout)
        
        # Style the dialog
        self.setStyleSheet("""
            QDialog {
                background-color: #2d1b4e;
                color: #e0d0ff;
            }
            QLabel {
                color: #e0d0ff;
            }
            QPushButton {
                background-color: #6a4c93;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 6px 12px;
            }
            QPushButton:hover {
                background-color: #8b5fbf;
            }
            QSpinBox, QFontComboBox, QComboBox {
                background-color: #1a0a2e;
                color: #e0d0ff;
                border: 1px solid #6a4c93;
                border-radius: 3px;
                padding: 4px;
            }
        """)
        
    def choose_color(self, color_type):
        """Open color picker dialog"""
        if color_type == 'bg':
            current = QColor(self.bg_color)
        elif color_type == 'text':
            current = QColor(self.text_color)
        else:
            current = QColor(self.sel_color)
            
        color = QColorDialog.getColor(current, self, "Choose Color")
        
        if color.isValid():
            hex_color = color.name()
            if color_type == 'bg':
                self.bg_color = hex_color
                self.bg_preview.setStyleSheet(f"background-color: {hex_color}; border: 1px solid #888;")
            elif color_type == 'text':
                self.text_color = hex_color
                self.text_preview.setStyleSheet(f"background-color: {hex_color}; border: 1px solid #888;")
            else:
                self.sel_color = hex_color
                self.sel_preview.setStyleSheet(f"background-color: {hex_color}; border: 1px solid #888;")
    
    def apply_preset(self, theme):
        """Apply a preset theme"""
        presets = {
            'purple': {
                'bg_color': '#1a0a2e',
                'text_color': '#e0d0ff',
                'selection_color': '#6a4c93'
            },
            'ocean': {
                'bg_color': '#001f3f',
                'text_color': '#7fdbff',
                'selection_color': '#0074d9'
            },
            'forest': {
                'bg_color': '#0d1f0d',
                'text_color': '#90ee90',
                'selection_color': '#2d5a2d'
            },
            'fire': {
                'bg_color': '#1a0a00',
                'text_color': '#ffcc99',
                'selection_color': '#cc3300'
            },
            'sunset': {
                'bg_color': '#2d1b2e',
                'text_color': '#ffb347',
                'selection_color': '#ff6b9d'
            },
            'dracula': {
                'bg_color': '#282a36',
                'text_color': '#f8f8f2',
                'selection_color': '#44475a'
            },
            'monokai': {
                'bg_color': '#272822',
                'text_color': '#f8f8f2',
                'selection_color': '#49483e'
            },
            'solarized_dark': {
                'bg_color': '#002b36',
                'text_color': '#839496',
                'selection_color': '#073642'
            },
            'nord': {
                'bg_color': '#2e3440',
                'text_color': '#d8dee9',
                'selection_color': '#434c5e'
            },
            'gruvbox': {
                'bg_color': '#282828',
                'text_color': '#ebdbb2',
                'selection_color': '#504945'
            },
            'tokyo_night': {
                'bg_color': '#1a1b26',
                'text_color': '#c0caf5',
                'selection_color': '#414868'
            },
            'cyberpunk': {
                'bg_color': '#0a0e27',
                'text_color': '#00ff9f',
                'selection_color': '#ff00ff'
            },
            'matrix': {
                'bg_color': '#000000',
                'text_color': '#00ff00',
                'selection_color': '#003300'
            },
            'amber': {
                'bg_color': '#1a1200',
                'text_color': '#ffb000',
                'selection_color': '#664400'
            },
            'synthwave': {
                'bg_color': '#2b213a',
                'text_color': '#ff7edb',
                'selection_color': '#6d77b3'
            },
            'cherry_blossom': {
                'bg_color': '#2d1a2e',
                'text_color': '#ffb3d9',
                'selection_color': '#944d6b'
            },
            'lavender': {
                'bg_color': '#1e1433',
                'text_color': '#e6d9ff',
                'selection_color': '#7b68a6'
            },
            'mint': {
                'bg_color': '#0f2922',
                'text_color': '#98ff98',
                'selection_color': '#2d5a4a'
            },
            'coffee': {
                'bg_color': '#1a0f0a',
                'text_color': '#d4a574',
                'selection_color': '#6b4423'
            },
            'midnight': {
                'bg_color': '#0c0f1a',
                'text_color': '#a8b5d1',
                'selection_color': '#1e2742'
            }
        }
        
        if theme in presets:
            preset = presets[theme]
            self.bg_color = preset['bg_color']
            self.text_color = preset['text_color']
            self.sel_color = preset['selection_color']
            
            self.bg_preview.setStyleSheet(f"background-color: {self.bg_color}; border: 1px solid #888;")
            self.text_preview.setStyleSheet(f"background-color: {self.text_color}; border: 1px solid #888;")
            self.sel_preview.setStyleSheet(f"background-color: {self.sel_color}; border: 1px solid #888;")
    
    def reset_defaults(self):
        """Reset to default settings"""
        self.bg_color = '#1a0a2e'
        self.text_color = '#e0d0ff'
        self.sel_color = '#6a4c93'
        
        self.bg_preview.setStyleSheet(f"background-color: {self.bg_color}; border: 1px solid #888;")
        self.text_preview.setStyleSheet(f"background-color: {self.text_color}; border: 1px solid #888;")
        self.sel_preview.setStyleSheet(f"background-color: {self.sel_color}; border: 1px solid #888;")
        
        self.font_combo.setCurrentFont(QFont('Consolas'))
        self.font_size.setValue(11)
        self.cursor_style.setCurrentText('Block')
        self.opacity.setValue(100)
    
    def get_settings(self):
        """Return current settings"""
        return {
            'bg_color': self.bg_color,
            'text_color': self.text_color,
            'selection_color': self.sel_color,
            'font_family': self.font_combo.currentFont().family(),
            'font_size': self.font_size.value(),
            'cursor_style': self.cursor_style.currentText(),
            'opacity': self.opacity.value()
        }


class EnhancedTerminal(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Herminal")
        self.resize(1000, 700)
        
        # Load settings
        self.settings = self.load_settings()
        
        self.setup_ui()
        self.setup_terminal()
        self.apply_settings()
        
        self.command_history = []
        self.history_index = -1
        self.current_line = ""
        self.command_buffer = ""
        
    def load_settings(self):
        """Load settings from file"""
        settings_file = os.path.expanduser('~/.hudul_terminal_settings.json')
        if os.path.exists(settings_file):
            try:
                with open(settings_file, 'r') as f:
                    return json.load(f)
            except:
                pass
        
        return {
            'bg_color': '#1a0a2e',
            'text_color': '#e0d0ff',
            'selection_color': '#6a4c93',
            'font_family': 'Consolas',
            'font_size': 11,
            'cursor_style': 'Block',
            'opacity': 100
        }
    
    def save_settings(self):
        """Save settings to file"""
        settings_file = os.path.expanduser('~/.hudul_terminal_settings.json')
        try:
            with open(settings_file, 'w') as f:
                json.dump(self.settings, f, indent=2)
        except Exception as e:
            print(f"Error saving settings: {e}")
        
    def setup_ui(self):
        """Setup the user interface"""
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # Terminal output area
        self.output = QPlainTextEdit()
        self.output.setReadOnly(True)
        
        main_layout.addWidget(self.output)
        
        # Status bar
        self.status_bar = QLabel("Ready | Type 'hsettings' for settings or 'hinfo' for help")
        main_layout.addWidget(self.status_bar)
        
        self.setLayout(main_layout)
        self.output.setFocus()
        
        # Context menu
        self.setup_context_menu()
        
    def apply_settings(self):
        """Apply current settings to terminal"""
        # Set font
        font = QFont(self.settings['font_family'], self.settings['font_size'])
        font.setStyleHint(QFont.StyleHint.Monospace)
        self.output.setFont(font)
        
        # Set colors
        bg_color = self.settings['bg_color']
        text_color = self.settings['text_color']
        sel_color = self.settings['selection_color']
        
        self.output.setStyleSheet(f"""
            QPlainTextEdit {{
                background-color: {bg_color};
                color: {text_color};
                border: none;
                padding: 10px;
                selection-background-color: {sel_color};
            }}
        """)
        
        # Calculate contrasting colors for status bar
        # Darken the background color for status bar
        bg_q = QColor(bg_color)
        status_bg = QColor(
            max(0, bg_q.red() - 30),
            max(0, bg_q.green() - 30),
            max(0, bg_q.blue() - 30)
        ).name()
        
        # Use text color for status bar text
        text_q = QColor(text_color)
        status_text = text_q.name()
        
        self.status_bar.setStyleSheet(f"""
            QLabel {{
                background-color: {status_bg};
                color: {status_text};
                padding: 5px 10px;
                font-size: 10px;
                border-top: 1px solid {sel_color};
            }}
        """)
        
        # Set window opacity
        self.setWindowOpacity(self.settings['opacity'] / 100.0)
        
    def setup_context_menu(self):
        """Setup right-click context menu"""
        self.output.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.output.customContextMenuRequested.connect(self.show_context_menu)
        
    def show_context_menu(self, position):
        """Show context menu"""
        menu = QMenu(self)
        
        # Get current theme colors
        bg_color = self.settings['bg_color']
        text_color = self.settings['text_color']
        sel_color = self.settings['selection_color']
        
        # Darken background for menu
        bg_q = QColor(bg_color)
        menu_bg = QColor(
            max(0, bg_q.red() - 20),
            max(0, bg_q.green() - 20),
            max(0, bg_q.blue() - 20)
        ).name()
        
        menu.setStyleSheet(f"""
            QMenu {{
                background-color: {menu_bg};
                color: {text_color};
                border: 1px solid {sel_color};
            }}
            QMenu::item:selected {{
                background-color: {sel_color};
            }}
        """)
        
        copy_action = QAction("📋 Copy", self)
        copy_action.triggered.connect(self.copy_selection)
        menu.addAction(copy_action)
        
        paste_action = QAction("📄 Paste", self)
        paste_action.triggered.connect(self.paste_clipboard)
        menu.addAction(paste_action)
        
        menu.addSeparator()
        
        settings_action = QAction("⚙️ Settings", self)
        settings_action.triggered.connect(self.open_settings)
        menu.addAction(settings_action)
        
        info_action = QAction("ℹ️ Help & Info", self)
        info_action.triggered.connect(self.show_info)
        menu.addAction(info_action)
        
        clear_action = QAction("🗑 Clear", self)
        clear_action.triggered.connect(self.clear_terminal)
        menu.addAction(clear_action)
        
        menu.exec(self.output.mapToGlobal(position))
    
    def setup_terminal(self):
        """Setup terminal backend"""
        self.screen = pyte.Screen(100, 30)
        self.stream = pyte.Stream(self.screen)
        
        shell = os.environ.get("SHELL", "/bin/zsh")
        try:
            # Set TERM environment variable for proper terminal emulation
            env = os.environ.copy()
            env['TERM'] = 'xterm-256color'
            self.ptyproc = ptyprocess.PtyProcessUnicode.spawn([shell], env=env)
            self.update_status(f"Shell: {shell} | 'hsettings' = settings, 'hinfo' = help")
        except Exception as e:
            self.update_status(f"Error: {str(e)}")
            return
        
        self.comm = Communicate()
        self.comm.output_signal.connect(self.update_output)
        self.comm.status_signal.connect(self.update_status)
        self.comm.settings_signal.connect(self.open_settings)
        self.comm.info_signal.connect(self.show_info)
        
        self.thread = threading.Thread(target=self.read_pty, daemon=True)
        self.thread.start()
        
    def read_pty(self):
        """Read from PTY in background thread"""
        while self.ptyproc.isalive():
            try:
                output = self.ptyproc.read(1024)
                if output:
                    # Check for hsettings command
                    if 'hsettings' in output.lower():
                        self.comm.settings_signal.emit()
                        # Clear the command from display
                        self.ptyproc.write('\x15')  # Ctrl+U to clear line
                        continue
                    
                    # Check for hinfo command
                    if 'hinfo' in output.lower():
                        self.comm.info_signal.emit()
                        # Clear the command from display
                        self.ptyproc.write('\x15')  # Ctrl+U to clear line
                        continue
                    
                    self.stream.feed(output)
                    display_text = "\n".join(self.screen.display)
                    
                    cursor_attr = {
                        'x': self.screen.cursor.x,
                        'y': self.screen.cursor.y,
                        'attrs': {}
                    }
                    
                    self.comm.output_signal.emit(display_text, cursor_attr)
            except EOFError:
                self.comm.status_signal.emit("Terminal closed")
                break
            except Exception as e:
                self.comm.status_signal.emit(f"Error: {str(e)}")
                break
    
    def update_output(self, text, cursor_attr):
        """Update terminal output with ANSI color support"""
        self.output.clear()
        
        text_cursor = self.output.textCursor()
        text_cursor.movePosition(QTextCursor.MoveOperation.Start)
        
        # Default text color from settings
        default_color = QColor(self.settings['text_color'])
        
        # Parse and apply ANSI colors
        lines = text.split('\n')
        for i, line in enumerate(lines):
            if i > 0:
                text_cursor.insertText('\n')
            
            # Check for ANSI escape sequences
            ansi_pattern = re.compile(r'\x1b\[([0-9;]+)m')
            last_end = 0
            current_format = QTextCharFormat()
            current_format.setForeground(default_color)
            
            for match in ansi_pattern.finditer(line):
                # Insert text before escape sequence
                if match.start() > last_end:
                    text_cursor.setCharFormat(current_format)
                    text_cursor.insertText(line[last_end:match.start()])
                
                # Parse color codes
                codes = match.group(1).split(';')
                for code in codes:
                    if code == '0':  # Reset
                        current_format = QTextCharFormat()
                        current_format.setForeground(default_color)
                    elif code == '1':  # Bold
                        current_format.setFontWeight(QFont.Weight.Bold)
                    elif code in ['30', '31', '32', '33', '34', '35', '36', '37',
                                  '90', '91', '92', '93', '94', '95', '96', '97']:
                        current_format.setForeground(ANSIParser.parse_color(code))
                
                last_end = match.end()
            
            # Insert remaining text
            if last_end < len(line):
                text_cursor.setCharFormat(current_format)
                text_cursor.insertText(line[last_end:])
        
        # Auto-scroll to bottom
        self.output.verticalScrollBar().setValue(
            self.output.verticalScrollBar().maximum()
        )
    
    def update_status(self, message):
        """Update status bar"""
        self.status_bar.setText(f"📟 {message}")
    
    def open_settings(self):
        """Open settings dialog"""
        dialog = SettingsDialog(self, self.settings)
        dialog.apply_theme_to_dialog(self.settings)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            self.settings = dialog.get_settings()
            self.apply_settings()
            self.save_settings()
            self.update_status("Settings saved successfully!")
    
    def show_info(self):
        """Show keyboard shortcuts and info"""
        info_text = """
<h2>🚀 Hudul Terminal - Keyboard Shortcuts</h2>

<h3>📋 Navigation Keys:</h3>
<ul>
<li><b>↑ (Up Arrow)</b> - Previous command in history</li>
<li><b>↓ (Down Arrow)</b> - Next command in history</li>
<li><b>← (Left Arrow)</b> - Move cursor left</li>
<li><b>→ (Right Arrow)</b> - Move cursor right</li>
<li><b>Home</b> - Jump to beginning of line</li>
<li><b>End</b> - Jump to end of line</li>
</ul>

<h3>⌨️ Enhanced Ctrl Key Support:</h3>
<ul>
<li><b>Ctrl+C</b> - Interrupt/cancel current command</li>
<li><b>Ctrl+D</b> - EOF/logout (exit shell)</li>
<li><b>Ctrl+Z</b> - Suspend current process</li>
<li><b>Ctrl+R</b> - Reverse history search</li>
<li><b>Ctrl+L</b> - Clear screen</li>
<li><b>Ctrl+A</b> - Go to beginning of line</li>
<li><b>Ctrl+E</b> - Go to end of line</li>
<li><b>Ctrl+K</b> - Delete from cursor to end of line</li>
<li><b>Ctrl+U</b> - Delete entire line</li>
<li><b>Ctrl+W</b> - Delete word before cursor</li>
</ul>

<h3>🛠️ Custom Commands:</h3>
<ul>
<li><b>hsettings</b> - Open terminal settings and themes</li>
<li><b>hinfo</b> - Show this help information</li>
</ul>

<h3>🎨 Features:</h3>
<ul>
<li>20+ beautiful preset themes</li>
<li>Full ANSI color support</li>
<li>Customizable fonts and colors</li>
<li>Adjustable transparency</li>
<li>Command history navigation</li>
<li>Right-click context menu</li>
</ul>
        """
        
        # Get current theme colors
        bg_color = self.settings['bg_color']
        text_color = self.settings['text_color']
        sel_color = self.settings['selection_color']
        
        # Darken background for dialog
        bg_q = QColor(bg_color)
        dialog_bg = QColor(
            max(0, bg_q.red() - 20),
            max(0, bg_q.green() - 20),
            max(0, bg_q.blue() - 20)
        ).name()
        
        msg = QMessageBox(self)
        msg.setWindowTitle("ℹ️ Terminal Information")
        msg.setTextFormat(Qt.TextFormat.RichText)
        msg.setText(info_text)
        msg.setStyleSheet(f"""
            QMessageBox {{
                background-color: {dialog_bg};
                color: {text_color};
            }}
            QLabel {{
                color: {text_color};
                min-width: 500px;
            }}
            QPushButton {{
                background-color: {sel_color};
                color: white;
                border: none;
                border-radius: 4px;
                padding: 6px 20px;
                min-width: 80px;
            }}
            QPushButton:hover {{
                background-color: {QColor(sel_color).lighter(120).name()};
            }}
        """)
        msg.exec()
        self.update_status("Type 'hsettings' for settings or 'hinfo' for help")
    
    def clear_terminal(self):
        """Clear terminal output"""
        self.ptyproc.write('clear\n')
    
    def copy_selection(self):
        """Copy selected text to clipboard"""
        cursor = self.output.textCursor()
        if cursor.hasSelection():
            QApplication.clipboard().setText(cursor.selectedText())
            self.update_status("Copied to clipboard")
    
    def paste_clipboard(self):
        """Paste from clipboard"""
        text = QApplication.clipboard().text()
        if text:
            self.ptyproc.write(text)
    
    def keyPressEvent(self, event):
        """Handle key press events"""
        key = event.key()
        mod = event.modifiers()
        text = event.text()
        
        # Check for hsettings command typing
        if text and (text.isalnum() or text in ['_', '-']):
            self.command_buffer += text
            if 'hsettings' in self.command_buffer:
                self.open_settings()
                # Clear the typed command
                for _ in range(9):  # length of 'hsettings'
                    self.ptyproc.write('\x7f')
                self.command_buffer = ""
                event.accept()
                return
            elif 'hinfo' in self.command_buffer:
                self.show_info()
                # Clear the typed command
                for _ in range(5):  # length of 'hinfo'
                    self.ptyproc.write('\x7f')
                self.command_buffer = ""
                event.accept()
                return
            # Keep only last 20 chars to avoid memory issues
            if len(self.command_buffer) > 20:
                self.command_buffer = self.command_buffer[-20:]
        
        # Handle special keys - send proper ANSI escape sequences
        if key == Qt.Key.Key_Backspace:
            if self.command_buffer:
                self.command_buffer = self.command_buffer[:-1]
            self.ptyproc.write('\x7f')
            event.accept()
            
        elif key == Qt.Key.Key_Return or key == Qt.Key.Key_Enter:
            self.command_buffer = ""
            self.ptyproc.write('\r')
            event.accept()
            
        elif key == Qt.Key.Key_Tab:
            self.ptyproc.write('\t')
            event.accept()
            
        elif key == Qt.Key.Key_Up:
            # Up arrow - for history
            self.ptyproc.write('\x1b[A')
            event.accept()
            
        elif key == Qt.Key.Key_Down:
            # Down arrow - for history
            self.ptyproc.write('\x1b[B')
            event.accept()
            
        elif key == Qt.Key.Key_Right:
            # Right arrow - for cursor movement
            self.ptyproc.write('\x1b[C')
            event.accept()
            
        elif key == Qt.Key.Key_Left:
            # Left arrow - for cursor movement
            self.ptyproc.write('\x1b[D')
            event.accept()
            
        elif key == Qt.Key.Key_Home:
            # Home key - go to beginning of line
            self.ptyproc.write('\x1b[H')
            event.accept()
            
        elif key == Qt.Key.Key_End:
            # End key - go to end of line
            self.ptyproc.write('\x1b[F')
            event.accept()
            
        elif key == Qt.Key.Key_Delete:
            # Delete key
            self.ptyproc.write('\x1b[3~')
            event.accept()
            
        elif key == Qt.Key.Key_PageUp:
            # Page Up
            self.ptyproc.write('\x1b[5~')
            event.accept()
            
        elif key == Qt.Key.Key_PageDown:
            # Page Down
            self.ptyproc.write('\x1b[6~')
            event.accept()
            
        elif mod & Qt.KeyboardModifier.ControlModifier:
            # Handle Ctrl key combinations
            if key == Qt.Key.Key_C:
                # Ctrl+C - interrupt
                self.ptyproc.write('\x03')
                event.accept()
            elif key == Qt.Key.Key_D:
                # Ctrl+D - EOF
                self.ptyproc.write('\x04')
                event.accept()
            elif key == Qt.Key.Key_Z:
                # Ctrl+Z - suspend
                self.ptyproc.write('\x1a')
                event.accept()
            elif key == Qt.Key.Key_R:
                # Ctrl+R - reverse search
                self.ptyproc.write('\x12')
                event.accept()
            elif key == Qt.Key.Key_L:
                # Ctrl+L - clear screen
                self.ptyproc.write('\x0c')
                event.accept()
            elif key == Qt.Key.Key_A:
                # Ctrl+A - beginning of line
                self.ptyproc.write('\x01')
                event.accept()
            elif key == Qt.Key.Key_E:
                # Ctrl+E - end of line
                self.ptyproc.write('\x05')
                event.accept()
            elif key == Qt.Key.Key_K:
                # Ctrl+K - kill to end of line
                self.ptyproc.write('\x0b')
                event.accept()
            elif key == Qt.Key.Key_U:
                # Ctrl+U - kill whole line
                self.ptyproc.write('\x15')
                event.accept()
            elif key == Qt.Key.Key_W:
                # Ctrl+W - kill word
                self.ptyproc.write('\x17')
                event.accept()
            elif Qt.Key.Key_A <= key <= Qt.Key.Key_Z:
                # Other Ctrl+letter combinations
                char = chr(key - Qt.Key.Key_A + 1)
                self.ptyproc.write(char)
                self.command_buffer = ""
                event.accept()
            else:
                event.ignore()
        else:
            # Regular text input
            if text:
                self.ptyproc.write(text)
                event.accept()
            else:
                event.ignore()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle('Fusion')
    window = EnhancedTerminal()
    window.show()
    sys.exit(app.exec())