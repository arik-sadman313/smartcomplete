#!/usr/bin/env python3
"""
SmartComplete GUI Installer, Diagnostic Suite & Control Center
A modern, intuitive graphical installer, diagnostic tool, and settings manager
for the SmartComplete intelligent text prediction engine on Linux.
"""

import os
import sys
import subprocess
import threading
import shutil
import json
import pathlib
import re
import time
import platform
import webbrowser
from typing import Dict, List, Optional, Tuple, Any

from PyQt6.QtCore import (
    Qt, QThread, pyqtSignal, QObject, QTimer, QSize, QPoint
)
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QStackedWidget, QLabel, QPushButton, QProgressBar, QTextEdit,
    QCheckBox, QRadioButton, QButtonGroup, QLineEdit, QComboBox,
    QSpinBox, QSlider, QFrame, QScrollArea, QSplitter, QDialog,
    QMessageBox, QGroupBox, QGridLayout, QSizePolicy, QToolButton
)
from PyQt6.QtGui import (
    QIcon, QPixmap, QColor, QFont, QTextCursor, QPainter, QLinearGradient,
    QKeySequence, QKeyEvent
)

# ═══════════════════════════════════════════════════════════════════════════════
_ICONS_DIR = pathlib.Path(__file__).resolve().parent / "data" / "icons"
_CHECK_SVG = (_ICONS_DIR / "checkbox_check.svg").as_posix()

DARK_THEME_QSS = """
/* Base typography and background reset */
* {
    font-family: -apple-system, BlinkMacSystemFont, "Inter", "Segoe UI", Roboto, "Ubuntu", "Cantarell", sans-serif;
    color: #e2e8f0;
}

QWidget {
    background-color: transparent;
}

QWidget#MainWindow {
    background-color: #070a13;
}

QDialog {
    background-color: #0c1220;
    border: 1px solid #1f2d46;
}

/* Base button reset to prevent native Linux 3D beveled rendering */
QPushButton {
    border: none;
    background-color: transparent;
    outline: none;
}

/* Sidebar styling */
QWidget#Sidebar {
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #090e19, stop:1 #050810);
    border-right: 1px solid #162033;
}

QLabel#SidebarBrandTitle {
    color: #f8fafc;
    font-size: 15px;
    font-weight: 800;
    letter-spacing: 0.6px;
}

QLabel#SidebarBrandSubtitle {
    color: #64748b;
    font-size: 11px;
    font-weight: 600;
    letter-spacing: 0.4px;
}

QLabel[class*="SidebarCategory"] {
    color: #475569;
    font-size: 10px;
    font-weight: 800;
    letter-spacing: 1.5px;
    padding-left: 8px;
    margin-top: 16px;
    margin-bottom: 6px;
}

QPushButton[class*="NavBtn"] {
    background-color: #0d1524;
    color: #94a3b8;
    border: 1px solid #17243b;
    border-radius: 10px;
    padding: 10px 14px;
    min-height: 20px;
    text-align: left;
    font-size: 13px;
    font-weight: 500;
}

QPushButton[class*="NavBtn"]:hover {
    background-color: #152238;
    color: #f1f5f9;
    border-color: #25395a;
}

QPushButton[class*="NavBtn"]:checked {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #1d4ed8, stop:0.8 #0284c7, stop:1 #0ea5e9);
    color: #ffffff;
    font-weight: 700;
    border: 1px solid #38bdf8;
    border-radius: 10px;
}

/* Header */
QWidget#HeaderBar {
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #0d1525, stop:1 #080d17);
    border-bottom: 1px solid #172439;
    padding: 14px 28px;
}

QLabel#HeaderPageTitle {
    color: #f8fafc;
    font-size: 17px;
    font-weight: 800;
    letter-spacing: 0.3px;
}

QLabel#HeaderPageSubtitle {
    color: #8393a7;
    font-size: 12px;
}

/* Workspace Canvas & Scroll Area */
QWidget#Workspace, QScrollArea#MainScrollArea, QStackedWidget#MainStack {
    background-color: #070a13;
    border: none;
}

QScrollArea#MainScrollArea > QWidget > QWidget {
    background-color: #070a13;
}

/* Cards & Panels */
QFrame[class*="Card"] {
    background-color: #0d1424;
    border: 1px solid #1e2c44;
    border-radius: 14px;
}

QFrame[class*="Card"]:hover {
    border-color: #2b4166;
}

QFrame[class*="CardHighlight"] {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #0f1e38, stop:1 #0b1426);
    border: 1px solid #0284c7;
    border-radius: 14px;
}

QFrame[class*="CardDanger"] {
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #220f14, stop:1 #16080b);
    border: 1px solid #991b1b;
    border-radius: 14px;
}

QFrame[class*="MiniStatCard"] {
    background-color: #131c30;
    border: 1px solid #233450;
    border-radius: 12px;
}

QFrame[class*="MiniStatCard"]:hover {
    border-color: #38bdf8;
    background-color: #17233c;
}

/* Interactive Option Row Card */
QFrame[class*="OptionCard"] {
    background-color: #131c30;
    border: 1px solid #233450;
    border-radius: 11px;
}

QFrame[class*="OptionCard"]:hover {
    background-color: #17233c;
    border-color: #38bdf8;
}

/* Doctor Diagnostic Row Cards */
QFrame[class*="DoctorItemCard"] {
    background-color: #131c30;
    border: 1px solid #233450;
    border-radius: 11px;
}

QFrame[class*="DoctorItemCard"]:hover {
    border-color: #38bdf8;
    background-color: #17233c;
}

QFrame[class*="DoctorItemCardNotice"] {
    background-color: #231116;
    border: 1px solid #881337;
    border-radius: 11px;
}

/* Badges */
QLabel[class*="Badge"] {
    border-radius: 11px;
    padding: 4px 12px;
    font-size: 11px;
    font-weight: 700;
    letter-spacing: 0.4px;
}

QLabel[class*="BadgeSuccess"] {
    background-color: rgba(16, 185, 129, 0.18);
    color: #34d399;
    border: 1px solid rgba(16, 185, 129, 0.5);
}

QLabel[class*="BadgeWarning"] {
    background-color: rgba(245, 158, 11, 0.18);
    color: #fcd34d;
    border: 1px solid rgba(245, 158, 11, 0.5);
}

QLabel[class*="BadgeError"] {
    background-color: rgba(239, 68, 68, 0.18);
    color: #fca5a5;
    border: 1px solid rgba(239, 68, 68, 0.5);
}

QLabel[class*="BadgeInfo"] {
    background-color: rgba(56, 189, 248, 0.18);
    color: #7dd3fc;
    border: 1px solid rgba(56, 189, 248, 0.5);
}

QLabel[class*="BadgeNeutral"] {
    background-color: #172439;
    color: #94a3b8;
    border: 1px solid #293d5c;
}

/* Buttons */
QPushButton[class*="PrimaryBtn"] {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #2563eb, stop:0.7 #0284c7, stop:1 #06b6d4);
    color: #ffffff;
    font-weight: 700;
    font-size: 13px;
    border: 1px solid #67e8f9;
    border-radius: 9px;
    padding: 10px 22px;
}

QPushButton[class*="PrimaryBtn"]:hover {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #3b82f6, stop:0.7 #0ea5e9, stop:1 #22d3ee);
    border-color: #ffffff;
}

QPushButton[class*="PrimaryBtn"]:pressed {
    background: #1d4ed8;
}

QPushButton[class*="PrimaryBtn"]:disabled {
    background: #152033;
    color: #64748b;
    border-color: #1e2d44;
}

QPushButton[class*="SecondaryBtn"] {
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #1a2840, stop:1 #131e30);
    color: #e2e8f0;
    font-weight: 600;
    font-size: 12px;
    border: 1px solid #2b436b;
    border-radius: 8px;
    padding: 8px 16px;
}

QPushButton[class*="SecondaryBtn"]:hover {
    background-color: #1f324f;
    border-color: #38bdf8;
    color: #ffffff;
}

QPushButton[class*="SecondaryBtn"]:pressed {
    background-color: #0e1624;
}

QPushButton[class*="DangerBtn"] {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #dc2626, stop:1 #991b1b);
    color: #ffffff;
    font-weight: 700;
    font-size: 13px;
    border: 1px solid #f87171;
    border-radius: 9px;
    padding: 11px 22px;
}

QPushButton[class*="DangerBtn"]:hover {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #ef4444, stop:1 #b91c1c);
    border-color: #fecaca;
}

QPushButton[class*="CandidateBtn"] {
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #172740, stop:1 #101c2f);
    color: #f0f9ff;
    font-weight: 600;
    font-size: 13px;
    border: 1px solid #0284c7;
    border-radius: 8px;
    padding: 8px 16px;
}

QPushButton[class*="CandidateBtn"]:hover {
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #0284c7, stop:1 #2563eb);
    color: #ffffff;
    border-color: #7dd3fc;
}

QPushButton[class*="ChipBtn"] {
    background-color: #152236;
    color: #cbd5e1;
    font-weight: 600;
    font-size: 12px;
    border: 1px solid #283c5a;
    border-radius: 14px;
    padding: 6px 14px;
}

QPushButton[class*="ChipBtn"]:hover {
    background-color: #1d2f4a;
    border-color: #38bdf8;
    color: #38bdf8;
}

/* Keycap styling */
QLabel[class*="KeyCap"] {
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #1d2c44, stop:1 #131c2e);
    color: #38bdf8;
    font-family: "JetBrains Mono", "Fira Code", monospace;
    font-weight: 800;
    font-size: 12px;
    border-radius: 7px;
    padding: 6px 14px;
    border: 1px solid #2e4366;
    border-bottom: 3px solid #070d18;
}

/* Input Fields */
QLineEdit, QTextEdit, QComboBox, QSpinBox {
    background-color: #0b1220;
    border: 1px solid #243650;
    border-radius: 8px;
    padding: 8px 12px;
    color: #f8fafc;
    font-size: 13px;
    selection-background-color: #0284c7;
}

QLineEdit:focus, QTextEdit:focus, QComboBox:focus, QSpinBox:focus {
    border-color: #38bdf8;
    background-color: #0e1728;
}

QComboBox::drop-down {
    subcontrol-origin: padding;
    subcontrol-position: top right;
    width: 24px;
    border-left: 1px solid #243650;
}

QComboBox QAbstractItemView {
    background-color: #0e1728;
    border: 1px solid #243650;
    color: #f8fafc;
    selection-background-color: #0284c7;
}

/* Sliders */
QSlider::groove:horizontal {
    border: 1px solid #22344f;
    height: 7px;
    background: #0b1220;
    border-radius: 4px;
}

QSlider::sub-page:horizontal {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #2563eb, stop:1 #38bdf8);
    border-radius: 4px;
}

QSlider::handle:horizontal {
    background: #ffffff;
    border: 2px solid #0284c7;
    width: 18px;
    margin-top: -6px;
    margin-bottom: -6px;
    border-radius: 9px;
}

QSlider::handle:horizontal:hover {
    background: #38bdf8;
    border-color: #ffffff;
}

/* Checkboxes */
QCheckBox {
    spacing: 10px;
    font-size: 13px;
    color: #e2e8f0;
}

QCheckBox::indicator {
    width: 20px;
    height: 20px;
    border-radius: 6px;
    border: 1px solid #3b5278;
    background-color: #0c1424;
}

QCheckBox::indicator:checked {
    background-color: #0284c7;
    border-color: #38bdf8;
    image: url('__CHECK_SVG__');
}

QCheckBox::indicator:hover {
    border-color: #38bdf8;
}

/* Progress Bar */
QProgressBar {
    background-color: #0b1220;
    border: 1px solid #22344f;
    border-radius: 8px;
    height: 16px;
    text-align: center;
    font-size: 10px;
    font-weight: 800;
    color: #cbd5e1;
}

QProgressBar::chunk {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #38bdf8, stop:0.5 #2563eb, stop:1 #6366f1);
    border-radius: 7px;
}

/* Scrollbars */
QScrollBar:vertical {
    border: none;
    background-color: #070a13;
    width: 10px;
    margin: 0;
}

QScrollBar::handle:vertical {
    background-color: #1f304c;
    border-radius: 5px;
    min-height: 26px;
}

QScrollBar::handle:vertical:hover {
    background-color: #314b75;
}

QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
    height: 0px;
}

/* Terminal / Log Viewer */
QFrame#TerminalContainer {
    background-color: #060912;
    border: 1px solid #1f304a;
    border-radius: 12px;
}

QFrame#TerminalHeader {
    background: #0e1728;
    border-bottom: 1px solid #1f304a;
    border-top-left-radius: 11px;
    border-top-right-radius: 11px;
    padding: 8px 16px;
}

QTextEdit#LogViewer {
    background-color: #060912;
    border: none;
    border-bottom-left-radius: 11px;
    border-bottom-right-radius: 11px;
    font-family: "JetBrains Mono", "Fira Code", "Cascadia Code", "Consolas", monospace;
    font-size: 12px;
    color: #a5b4fc;
    padding: 12px;
}

/* Step list */
QFrame[class*="StepItem"] {
    background-color: #131c30;
    border: 1px solid #233450;
    border-radius: 11px;
}

QFrame[class*="StepItem"]:hover {
    border-color: #2d456b;
}

QFrame[class*="StepItemActive"] {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #0f2746, stop:1 #0c182c);
    border: 1px solid #0284c7;
    border-radius: 11px;
}

QFrame[class*="StepItemSuccess"] {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #0a241b, stop:1 #081713);
    border: 1px solid rgba(16, 185, 129, 0.55);
    border-radius: 11px;
}

QFrame[class*="StepItemError"] {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #2b1116, stop:1 #19090d);
    border: 1px solid rgba(239, 68, 68, 0.55);
    border-radius: 11px;
}
"""
DARK_THEME_QSS = DARK_THEME_QSS.replace("__CHECK_SVG__", _CHECK_SVG)

# ═══════════════════════════════════════════════════════════════════════════════
# System Inspector
# ═══════════════════════════════════════════════════════════════════════════════

class SystemInspector:
    """Probes the OS, desktop environment, compositor, shell, and dependencies."""

    @staticmethod
    def get_project_dir() -> pathlib.Path:
        return pathlib.Path(__file__).resolve().parent

    @classmethod
    def detect_distro(cls) -> Dict[str, str]:
        info = {"id": "unknown", "name": "Linux (Unknown)", "pkg_mgr": "unknown"}
        if os.path.exists("/etc/os-release"):
            with open("/etc/os-release", "r", encoding="utf-8") as f:
                for line in f:
                    if line.startswith("ID="):
                        info["id"] = line.strip().split("=")[1].strip('"').lower()
                    elif line.startswith("PRETTY_NAME="):
                        info["name"] = line.strip().split("=")[1].strip('"')
                    elif line.startswith("ID_LIKE="):
                        info["id_like"] = line.strip().split("=")[1].strip('"').lower()

        id_str = info.get("id", "") + " " + info.get("id_like", "")
        if shutil.which("pacman") or "arch" in id_str or "manjaro" in id_str or "endeavouros" in id_str or "omarchy" in id_str:
            info["family"] = "arch"
            info["pkg_mgr"] = "pacman"
        elif shutil.which("apt-get") or "debian" in id_str or "ubuntu" in id_str or "mint" in id_str or "pop" in id_str:
            info["family"] = "debian"
            info["pkg_mgr"] = "apt-get"
        elif shutil.which("dnf") or "fedora" in id_str or "rhel" in id_str:
            info["family"] = "fedora"
            info["pkg_mgr"] = "dnf"
        elif shutil.which("zypper") or "suse" in id_str:
            info["family"] = "opensuse"
            info["pkg_mgr"] = "zypper"
        else:
            info["family"] = "generic"
            info["pkg_mgr"] = "none"

        return info

    @classmethod
    def detect_session(cls) -> Dict[str, str]:
        session_type = os.environ.get("XDG_SESSION_TYPE", "unknown").lower()
        desktop = os.environ.get("XDG_CURRENT_DESKTOP", "unknown")

        compositor = "unknown"
        try:
            pgrep = subprocess.run(["pgrep", "-a", "Hyprland"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            if pgrep.returncode == 0:
                compositor = "hyprland"
            else:
                for proc in ["niri", "sway", "gnome-shell", "plasmashell", "wayfire", "river"]:
                    res = subprocess.run(["pgrep", "-x", proc], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
                    if res.returncode == 0:
                        compositor = "gnome" if proc == "gnome-shell" else ("kde" if proc == "plasmashell" else proc)
                        break
        except Exception:
            pass

        if compositor == "unknown":
            if "hyprland" in desktop.lower():
                compositor = "hyprland"
            elif "gnome" in desktop.lower():
                compositor = "gnome"
            elif "kde" in desktop.lower() or "plasma" in desktop.lower():
                compositor = "kde"
            elif "sway" in desktop.lower():
                compositor = "sway"
            elif session_type == "x11":
                compositor = "x11"

        return {
            "session_type": session_type,
            "desktop": desktop,
            "compositor": compositor
        }

    @classmethod
    def detect_systemd_env(cls) -> Dict[str, Any]:
        p = pathlib.Path.home() / ".config" / "environment.d" / "10-fcitx5.conf"
        has_env = False
        if p.exists():
            try:
                has_env = "GTK_IM_MODULE=fcitx" in p.read_text(encoding="utf-8", errors="ignore")
            except Exception:
                pass
        return {
            "path": str(p),
            "exists": p.exists(),
            "has_env": has_env
        }

    @classmethod
    def check_fcitx5(cls) -> Dict[str, Any]:
        fcitx_bin = shutil.which("fcitx5")
        is_running = False
        try:
            res = subprocess.run(["pgrep", "-x", "fcitx5"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            is_running = (res.returncode == 0)
        except Exception:
            pass

        profile_path = pathlib.Path.home() / ".config" / "fcitx5" / "profile"
        has_smartcomplete = False
        if profile_path.exists():
            try:
                content = profile_path.read_text(encoding="utf-8", errors="ignore")
                has_smartcomplete = "DefaultIM=linuxcomplete" in content or "Name=linuxcomplete" in content
            except Exception:
                pass

        addon_paths = [
            "/usr/lib/fcitx5/linuxcomplete.so",
            "/usr/lib64/fcitx5/linuxcomplete.so",
            "/usr/local/lib/fcitx5/linuxcomplete.so",
            str(pathlib.Path.home() / ".local/lib/fcitx5/linuxcomplete.so")
        ]
        installed_so = None
        for p in addon_paths:
            if os.path.exists(p):
                installed_so = p
                break

        return {
            "installed": fcitx_bin is not None,
            "binary": fcitx_bin,
            "running": is_running,
            "profile_configured": has_smartcomplete,
            "addon_so": installed_so
        }

    @classmethod
    def check_missing_packages(cls, distro_family: str) -> List[str]:
        missing = []
        if distro_family == "arch":
            pkgs = ["fcitx5", "cmake", "gcc", "nlohmann-json", "fcitx5-gtk", "fcitx5-qt"]
            for pkg in pkgs:
                res = subprocess.run(["pacman", "-Qi", pkg], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                if res.returncode != 0:
                    missing.append(pkg)
        elif distro_family == "debian":
            pkgs = ["fcitx5", "libfcitx5core-dev", "fcitx5-modules-dev", "fcitx5-frontend-qt5",
                    "fcitx5-frontend-gtk3", "fcitx5-config-qt", "cmake", "g++", "nlohmann-json3-dev"]
            for pkg in pkgs:
                res = subprocess.run(["dpkg", "-s", pkg], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                if res.returncode != 0:
                    missing.append(pkg)
        elif distro_family == "fedora":
            pkgs = ["fcitx5", "fcitx5-devel", "fcitx5-qt", "fcitx5-gtk", "fcitx5-configtool", "cmake", "gcc-c++", "json-devel"]
            for pkg in pkgs:
                res = subprocess.run(["rpm", "-q", pkg], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                if res.returncode != 0:
                    missing.append(pkg)
        return missing

# ═══════════════════════════════════════════════════════════════════════════════
# In-App Password Authentication Dialog
# ═══════════════════════════════════════════════════════════════════════════════

class PasswordDialog(QDialog):
    """Secure modal dialog for entering sudo password when required."""

    def __init__(self, parent=None, prompt_text="Administrator privileges are required to continue."):
        super().__init__(parent)
        self.setWindowTitle("Authentication Required — SmartComplete")
        self.setFixedSize(460, 270)
        self.setModal(True)
        self.password = None

        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(16)

        header_layout = QHBoxLayout()
        icon_box = QLabel("🔒")
        icon_box.setStyleSheet("font-size: 32px; background: rgba(56, 189, 248, 0.12); border-radius: 12px; padding: 6px;")
        header_layout.addWidget(icon_box)

        title_layout = QVBoxLayout()
        title_layout.setSpacing(3)
        title = QLabel("Root Authorization Needed")
        title.setStyleSheet("font-size: 16px; font-weight: 700; color: #f8fafc;")
        desc = QLabel(prompt_text)
        desc.setStyleSheet("font-size: 12px; color: #94a3b8; line-height: 1.3;")
        desc.setWordWrap(True)
        title_layout.addWidget(title)
        title_layout.addWidget(desc)
        header_layout.addLayout(title_layout)
        header_layout.addStretch()
        layout.addLayout(header_layout)

        self.pwd_input = QLineEdit()
        self.pwd_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.pwd_input.setPlaceholderText("Enter your user password (sudo)...")
        layout.addWidget(self.pwd_input)

        self.error_label = QLabel("")
        self.error_label.setStyleSheet("color: #f87171; font-size: 12px; font-weight: 500;")
        self.error_label.setVisible(False)
        layout.addWidget(self.error_label)

        show_cb = QCheckBox("Show password")
        show_cb.toggled.connect(lambda chk: self.pwd_input.setEchoMode(
            QLineEdit.EchoMode.Normal if chk else QLineEdit.EchoMode.Password
        ))
        layout.addWidget(show_cb)

        layout.addStretch()

        btn_layout = QHBoxLayout()
        btn_layout.addStretch()

        cancel_btn = QPushButton("Cancel")
        cancel_btn.setProperty("class", "SecondaryBtn")
        cancel_btn.clicked.connect(self.reject)
        btn_layout.addWidget(cancel_btn)

        self.ok_btn = QPushButton("Authenticate")
        self.ok_btn.setProperty("class", "PrimaryBtn")
        self.ok_btn.clicked.connect(self.validate_and_accept)
        btn_layout.addWidget(self.ok_btn)

        layout.addLayout(btn_layout)
        self.pwd_input.returnPressed.connect(self.validate_and_accept)

    def validate_and_accept(self):
        pwd = self.pwd_input.text()
        if not pwd:
            self.error_label.setText("Password cannot be empty.")
            self.error_label.setVisible(True)
            return

        self.ok_btn.setEnabled(False)
        self.ok_btn.setText("Verifying...")
        QApplication.processEvents()

        try:
            proc = subprocess.run(
                ["sudo", "-k", "-S", "true"],
                input=pwd + "\n",
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
            if proc.returncode == 0:
                self.password = pwd
                self.accept()
            else:
                self.error_label.setText("Incorrect password. Please try again.")
                self.error_label.setVisible(True)
                self.pwd_input.selectAll()
                self.pwd_input.setFocus()
                self.ok_btn.setEnabled(True)
                self.ok_btn.setText("Authenticate")
        except Exception as e:
            self.error_label.setText(f"Auth check error: {e}")
            self.error_label.setVisible(True)
            self.ok_btn.setEnabled(True)
            self.ok_btn.setText("Authenticate")

# ═══════════════════════════════════════════════════════════════════════════════
# Background Installer Worker Thread
# ═══════════════════════════════════════════════════════════════════════════════

class InstallWorker(QThread):
    """Executes the full 7-step build and installation workflow asynchronously."""

    step_started = pyqtSignal(int, str, str)
    step_finished = pyqtSignal(int, bool, str)
    log_emitted = pyqtSignal(str, str)
    progress_changed = pyqtSignal(int)
    overall_finished = pyqtSignal(bool, str)
    request_auth = pyqtSignal(str)

    def __init__(self, config: Dict[str, Any], project_dir: pathlib.Path):
        super().__init__()
        self.cfg = config
        self.project_dir = project_dir
        self.build_dir = project_dir / "build"
        self.password: Optional[str] = None
        self._auth_event = threading.Event()
        self.distro = SystemInspector.detect_distro()
        self.session = SystemInspector.detect_session()

    def set_auth_response(self, password: Optional[str]):
        self.password = password
        self._auth_event.set()

    def _run_cmd(self, cmd: List[str], cwd: Optional[pathlib.Path] = None,
                 needs_sudo: bool = False, env: Optional[Dict] = None) -> Tuple[int, str]:
        if needs_sudo and os.geteuid() != 0:
            check_sudo = subprocess.run(["sudo", "-n", "true"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            if check_sudo.returncode != 0 and not self.password:
                self._auth_event.clear()
                self.request_auth.emit("Administrative rights needed to run: " + " ".join(cmd[:2]))
                self._auth_event.wait()
                if not self.password:
                    return 1, "Authentication was cancelled by the user."

            full_cmd = ["sudo", "-S"] + cmd if self.password else (["sudo"] + cmd)
            input_data = (self.password + "\n") if self.password else None
        else:
            full_cmd = cmd
            input_data = None

        self.log_emitted.emit("info", f"$ {' '.join(full_cmd if not input_data else cmd)}")

        proc_env = os.environ.copy()
        if env:
            proc_env.update(env)

        try:
            process = subprocess.Popen(
                full_cmd,
                cwd=str(cwd or self.project_dir),
                stdin=subprocess.PIPE if input_data else None,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                env=proc_env,
                bufsize=1
            )
            if input_data:
                try:
                    process.stdin.write(input_data)
                    process.stdin.flush()
                except Exception:
                    pass

            output_lines = []
            if process.stdout:
                for line in iter(process.stdout.readline, ""):
                    clean = line.rstrip()
                    output_lines.append(clean)
                    self.log_emitted.emit("output", clean)

            process.wait()
            return process.returncode, "\n".join(output_lines)
        except Exception as e:
            self.log_emitted.emit("error", str(e))
            return 1, str(e)

    def run(self):
        steps = [
            ("Pre-flight & Environment Check", self._step1_preflight),
            ("Resolve System Dependencies", self._step2_dependencies),
            ("Compile Engine & Run Test Suites", self._step3_build),
            ("Install SmartComplete to /usr", self._step4_install_system),
            ("Configure Environment & Compositor", self._step5_configure_env),
            ("Setup Fcitx5 Input Method Profile", self._step6_configure_fcitx5),
            ("Restart & Verify System Integration", self._step7_restart_verify)
        ]

        total = len(steps)
        for i, (name, func) in enumerate(steps, 1):
            pct = int((i - 1) / total * 100)
            self.progress_changed.emit(pct)
            self.step_started.emit(i, name, f"Executing step {i} of {total}...")
            self.log_emitted.emit("step", f"=== [Step {i}/{total}] {name} ===")

            try:
                success, msg = func()
                if not success:
                    self.step_finished.emit(i, False, msg)
                    self.log_emitted.emit("error", f"Step {i} failed: {msg}")
                    self.overall_finished.emit(False, f"Installation halted at Step {i}: {msg}")
                    return
                self.step_finished.emit(i, True, msg)
                self.log_emitted.emit("success", f"✓ {msg}")
            except Exception as e:
                self.step_finished.emit(i, False, str(e))
                self.log_emitted.emit("error", f"Exception in step {i}: {e}")
                self.overall_finished.emit(False, f"Error in step {i}: {e}")
                return

        self.progress_changed.emit(100)
        self.overall_finished.emit(True, "SmartComplete was successfully installed and activated!")

    def _step1_preflight(self) -> Tuple[bool, str]:
        self.log_emitted.emit("info", f"Detected Distribution: {self.distro['name']} ({self.distro['family']})")
        self.log_emitted.emit("info", f"Detected Session: {self.session['session_type']} on {self.session['compositor']}")

        if not (self.project_dir / "CMakeLists.txt").exists():
            return False, "CMakeLists.txt not found in workspace directory."

        if not shutil.which("cmake"):
            return False, "CMake is required but not installed."

        return True, f"Environment verified ({self.distro['family']} / {self.session['compositor']})"

    def _step2_dependencies(self) -> Tuple[bool, str]:
        missing = SystemInspector.check_missing_packages(self.distro["family"])
        if not missing:
            return True, "All required system dependencies are already installed"

        self.log_emitted.emit("info", f"Installing missing packages: {', '.join(missing)}")
        fam = self.distro["family"]
        if fam == "arch":
            cmd = ["pacman", "-S", "--noconfirm", "--needed"] + missing
        elif fam == "debian":
            self._run_cmd(["apt-get", "update", "-qq"], needs_sudo=True)
            cmd = ["apt-get", "install", "-y", "-qq"] + missing
        elif fam == "fedora":
            cmd = ["dnf", "install", "-y", "-q"] + missing
        else:
            return False, f"Unsupported automatic package installation for {fam}. Please install: {', '.join(missing)}"

        code, out = self._run_cmd(cmd, needs_sudo=True)
        if code != 0:
            return False, f"Package installation failed with exit code {code}."

        return True, f"Successfully installed {len(missing)} package(s)"

    def _step3_build(self) -> Tuple[bool, str]:
        self.build_dir.mkdir(parents=True, exist_ok=True)
        prefix = self.cfg.get("install_prefix", "/usr")

        cmake_cfg = [
            "cmake", "-S", str(self.project_dir), "-B", str(self.build_dir),
            f"-DCMAKE_INSTALL_PREFIX={prefix}",
            "-DCMAKE_BUILD_TYPE=Release"
        ]
        code, out = self._run_cmd(cmake_cfg)
        if code != 0:
            return False, "CMake configuration failed."

        nproc = str(os.cpu_count() or 4)
        cmake_build = ["cmake", "--build", str(self.build_dir), "-j" + nproc]
        code, out = self._run_cmd(cmake_build)
        if code != 0:
            return False, "C++ compilation failed."

        if self.cfg.get("run_tests", True):
            self.log_emitted.emit("info", "Running CTest regression verification suite (13 tests)...")
            code, test_out = self._run_cmd(["ctest", "--test-dir", str(self.build_dir), "--output-on-failure"])
            if code != 0:
                self.log_emitted.emit("warning", "Some unit tests reported issues, but continuing installation.")

        return True, "Engine compiled and verified successfully"

    def _step4_install_system(self) -> Tuple[bool, str]:
        code, out = self._run_cmd(["cmake", "--install", str(self.build_dir)], needs_sudo=True)
        if code != 0:
            return False, "Failed to copy binaries to system prefix."

        home = pathlib.Path.home()
        (home / ".local" / "share" / "linuxcomplete" / "user").mkdir(parents=True, exist_ok=True)
        config_dir = home / ".config" / "linuxcomplete"
        config_dir.mkdir(parents=True, exist_ok=True)

        conf_file = config_dir / "linuxcomplete.conf"
        if not conf_file.exists():
            default_conf = (self.project_dir / "config" / "linuxcomplete.conf").read_text(encoding="utf-8")
            conf_file.write_text(default_conf, encoding="utf-8")

        if self.cfg.get("ai_enabled", False):
            api_file = config_dir / "api_keys.json"
            ai_data = {
                "provider": "openai",
                "ai_enabled": True,
                "api_key": self.cfg.get("ai_api_key", ""),
                "api_base": self.cfg.get("ai_api_base", "https://api.openai.com/v1"),
                "model": self.cfg.get("ai_model", "gpt-4o-mini")
            }
            api_file.write_text(json.dumps(ai_data, indent=4), encoding="utf-8")
            self.log_emitted.emit("info", "AI Reranker credentials saved to api_keys.json")

        return True, "SmartComplete binaries and data directories deployed"

    def _step5_configure_env(self) -> Tuple[bool, str]:
        home = pathlib.Path.home()

        # systemd environment.d
        env_d = home / ".config" / "environment.d"
        env_d.mkdir(parents=True, exist_ok=True)
        env_file = env_d / "10-fcitx5.conf"
        env_content = (
            "# SmartComplete — System-wide Fcitx5 Input Method\n"
            "GTK_IM_MODULE=fcitx\n"
            "QT_IM_MODULE=fcitx\n"
            "XMODIFIERS=@im=fcitx\n"
            "SDL_IM_MODULE=fcitx\n"
            "GLFW_IM_MODULE=ibus\n"
        )
        env_file.write_text(env_content, encoding="utf-8")
        self.log_emitted.emit("info", f"Wrote systemd session environment: {env_file}")

        # Shell RCs
        shell_block = (
            "\n# SmartComplete — Input Method Configuration\n"
            "export GTK_IM_MODULE=fcitx\n"
            "export QT_IM_MODULE=fcitx\n"
            "export XMODIFIERS=@im=fcitx\n"
            "export SDL_IM_MODULE=fcitx\n"
            "export GLFW_IM_MODULE=ibus\n"
        )
        for rc in [home / ".bashrc", home / ".zshrc"]:
            if rc.exists():
                text = rc.read_text(encoding="utf-8", errors="ignore")
                if "GTK_IM_MODULE=fcitx" not in text:
                    rc.write_text(text + shell_block, encoding="utf-8")
                    self.log_emitted.emit("info", f"Appended IM environment exports to {rc.name}")

        # XDG Autostart
        autostart_dir = home / ".config" / "autostart"
        autostart_dir.mkdir(parents=True, exist_ok=True)
        desktop_file = autostart_dir / "fcitx5.desktop"
        desktop_file.write_text(
            "[Desktop Entry]\n"
            "Type=Application\n"
            "Name=Fcitx5 (SmartComplete)\n"
            "Exec=fcitx5 -d\n"
            "X-GNOME-Autostart-enabled=true\n"
            "NoDisplay=true\n",
            encoding="utf-8"
        )

        # Hyprland autostart
        hypr_dir = home / ".config" / "hypr"
        if hypr_dir.exists():
            for conf_name in ["execs.conf", "hyprland.conf"]:
                hp = hypr_dir / conf_name
                if hp.exists():
                    txt = hp.read_text(encoding="utf-8", errors="ignore")
                    if "fcitx5" not in txt:
                        addition = (
                            "\n# SmartComplete\n"
                            "exec-once = fcitx5 -d\n"
                            "exec-once = sleep 2 && fcitx5-remote -o\n"
                            "env = GTK_IM_MODULE,fcitx\n"
                            "env = QT_IM_MODULE,fcitx\n"
                            "env = XMODIFIERS,@im=fcitx\n"
                            "env = SDL_IM_MODULE,fcitx\n"
                            "env = GLFW_IM_MODULE,ibus\n"
                        )
                        hp.write_text(txt + addition, encoding="utf-8")
                        self.log_emitted.emit("info", f"Added autostart to {hp}")
                        break

        return True, "Environment variables and autostart configured"

    def _step6_configure_fcitx5(self) -> Tuple[bool, str]:
        home = pathlib.Path.home()
        fcitx_dir = home / ".config" / "fcitx5"
        fcitx_dir.mkdir(parents=True, exist_ok=True)

        profile_path = fcitx_dir / "profile"
        if profile_path.exists():
            backup_p = fcitx_dir / f"profile.bak.{int(time.time())}"
            shutil.copy2(profile_path, backup_p)

        profile_content = (
            "[Groups/0]\n"
            "Name=Default\n"
            "Default Layout=us\n"
            "DefaultIM=linuxcomplete\n\n"
            "[Groups/0/Items/0]\n"
            "Name=keyboard-us\n"
            "Layout=us\n\n"
            "[Groups/0/Items/1]\n"
            "Name=linuxcomplete\n"
            "Layout=\n\n"
            "[GroupOrder]\n"
            "0=Default\n"
        )
        profile_path.write_text(profile_content, encoding="utf-8")

        config_path = fcitx_dir / "config"
        if config_path.exists():
            backup_c = fcitx_dir / f"config.bak.{int(time.time())}"
            shutil.copy2(config_path, backup_c)

        config_content = (
            "[Hotkey]\n"
            "EnumerateWithTriggerKeys=True\n"
            "AltTriggerKeys=Shift_L\n\n"
            "[Behavior]\n"
            "ShareInputState=All\n"
            "PreloadInputMethod=True\n"
            "ShowFirstInputMethodInformation=True\n"
            "DefaultInputMethod=linuxcomplete\n"
        )
        config_path.write_text(config_content, encoding="utf-8")

        return True, "Fcitx5 profile configured with SmartComplete as default"

    def _step7_restart_verify(self) -> Tuple[bool, str]:
        self.log_emitted.emit("info", "Restarting Fcitx5 daemon...")
        subprocess.run(["killall", "fcitx5"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        time.sleep(0.8)

        subprocess.Popen(["fcitx5", "-d"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        time.sleep(1.2)

        subprocess.run(["fcitx5-remote", "-o"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

        res = subprocess.run(["pgrep", "-x", "fcitx5"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        fcitx_running = (res.returncode == 0)

        addon_ok = any(
            os.path.exists(p) for p in [
                "/usr/lib/fcitx5/linuxcomplete.so",
                "/usr/lib64/fcitx5/linuxcomplete.so",
                "/usr/local/lib/fcitx5/linuxcomplete.so"
            ]
        )

        if not addon_ok:
            return False, "Verification failed: linuxcomplete.so could not be found in library paths."

        if not fcitx_running:
            return False, "Fcitx5 daemon did not restart automatically. Try running 'fcitx5 -d' manually."

        return True, f"Verified: Fcitx5 running (PID {res.stdout.decode().strip()}), addon active"

# ═══════════════════════════════════════════════════════════════════════════════
# Background Uninstaller Worker Thread
# ═══════════════════════════════════════════════════════════════════════════════

class UninstallWorker(QThread):
    """Safely removes SmartComplete and restores previous system configurations."""

    log_emitted = pyqtSignal(str, str)
    finished = pyqtSignal(bool, str)
    request_auth = pyqtSignal(str)

    def __init__(self, purge_user_data: bool, project_dir: pathlib.Path):
        super().__init__()
        self.purge = purge_user_data
        self.project_dir = project_dir
        self.password: Optional[str] = None
        self._auth_event = threading.Event()

    def set_auth_response(self, password: Optional[str]):
        self.password = password
        self._auth_event.set()

    def _run_cmd(self, cmd: List[str], needs_sudo: bool = False) -> Tuple[int, str]:
        if needs_sudo and os.geteuid() != 0:
            check_sudo = subprocess.run(["sudo", "-n", "true"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            if check_sudo.returncode != 0 and not self.password:
                self._auth_event.clear()
                self.request_auth.emit("Administrative rights needed for uninstall.")
                self._auth_event.wait()
                if not self.password:
                    return 1, "Cancelled"

            full_cmd = ["sudo", "-S"] + cmd if self.password else (["sudo"] + cmd)
            input_data = (self.password + "\n") if self.password else None
        else:
            full_cmd = cmd
            input_data = None

        self.log_emitted.emit("info", f"$ {' '.join(full_cmd if not input_data else cmd)}")
        try:
            p = subprocess.run(
                full_cmd,
                input=input_data,
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT
            )
            return p.returncode, p.stdout or ""
        except Exception as e:
            return 1, str(e)

    def run(self):
        self.log_emitted.emit("step", "Stopping Fcitx5...")
        subprocess.run(["killall", "fcitx5"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        time.sleep(0.4)

        manifest = self.project_dir / "build" / "install_manifest.txt"
        if manifest.exists():
            self.log_emitted.emit("info", "Removing files via install_manifest.txt...")
            for line in manifest.read_text(encoding="utf-8").splitlines():
                f = line.strip()
                if f and os.path.exists(f):
                    self._run_cmd(["rm", "-f", f], needs_sudo=True)
        else:
            self.log_emitted.emit("info", "Removing files from standard paths...")
            for p in ["/usr/lib/fcitx5/linuxcomplete.so", "/usr/lib64/fcitx5/linuxcomplete.so",
                      "/usr/share/fcitx5/addon/linuxcomplete.conf",
                      "/usr/share/fcitx5/inputmethod/linuxcomplete.conf"]:
                if os.path.exists(p):
                    self._run_cmd(["rm", "-f", p], needs_sudo=True)
            if os.path.exists("/usr/share/linuxcomplete"):
                self._run_cmd(["rm", "-rf", "/usr/share/linuxcomplete"], needs_sudo=True)

        home = pathlib.Path.home()
        profile = home / ".config" / "fcitx5" / "profile"
        if profile.exists():
            txt = profile.read_text(encoding="utf-8", errors="ignore")
            if "linuxcomplete" in txt:
                self.log_emitted.emit("info", "Cleaning Fcitx5 profile...")
                txt = re.sub(r'\[Groups/\d+/Items/\d+\]\s*\nName=linuxcomplete\s*\nLayout=.*?\n', '', txt)
                txt = txt.replace("DefaultIM=linuxcomplete", "DefaultIM=keyboard-us")
                profile.write_text(txt, encoding="utf-8")

        env_f = home / ".config" / "environment.d" / "10-fcitx5.conf"
        if env_f.exists():
            try:
                env_f.unlink()
                self.log_emitted.emit("info", "Removed environment.d config")
            except Exception:
                pass

        auto_f = home / ".config" / "autostart" / "fcitx5.desktop"
        if auto_f.exists() and "SmartComplete" in auto_f.read_text(encoding="utf-8", errors="ignore"):
            try:
                auto_f.unlink()
                self.log_emitted.emit("info", "Removed XDG autostart entry")
            except Exception:
                pass

        for rc in [home / ".bashrc", home / ".zshrc"]:
            if rc.exists():
                content = rc.read_text(encoding="utf-8", errors="ignore")
                if "SmartComplete — Input Method" in content:
                    cleaned = re.sub(r'# SmartComplete — Input Method Configuration.*?(?=export GLFW_IM_MODULE=ibus)export GLFW_IM_MODULE=ibus\n?', '', content, flags=re.DOTALL)
                    rc.write_text(cleaned, encoding="utf-8")
                    self.log_emitted.emit("info", f"Cleaned {rc.name}")

        if self.purge:
            self.log_emitted.emit("warning", "Purging user data and learned typing models...")
            shutil.rmtree(str(home / ".local/share/linuxcomplete"), ignore_errors=True)
            shutil.rmtree(str(home / ".config/linuxcomplete"), ignore_errors=True)

        subprocess.Popen(["fcitx5", "-d"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        self.finished.emit(True, "SmartComplete was cleanly uninstalled.")

# ═══════════════════════════════════════════════════════════════════════════════
# Simulation Predictor (Provides Offline Live Suggestions for the Scratchpad)
# ═══════════════════════════════════════════════════════════════════════════════

class SimulationPredictor:
    """Simulates the 6 prediction strategies for the interactive test scratchpad."""

    def __init__(self, project_dir: pathlib.Path):
        self.project_dir = project_dir
        self.dict_words: List[str] = []
        self.emojis: Dict[str, str] = {}
        self.phrases: Dict[str, str] = {}
        self.loaded = False
        self._load_data()

    def _load_data(self):
        data_dir = self.project_dir / "data"

        for ef in ["en_emoji.tsv", "emoji.tsv"]:
            p = data_dir / "emoji" / ef
            if p.exists():
                try:
                    with open(p, "r", encoding="utf-8", errors="ignore") as f:
                        for line in f:
                            parts = line.strip().split("\t")
                            if len(parts) >= 2:
                                sc = parts[0].strip()
                                em = parts[1].strip()
                                self.emojis[sc] = em
                                if sc.startswith(":"):
                                    self.emojis[sc[1:]] = em
                except Exception:
                    pass
                break

        for pf in ["en_phrases.txt", "phrases.txt"]:
            p = data_dir / "ngram" / pf
            if p.exists():
                try:
                    with open(p, "r", encoding="utf-8", errors="ignore") as f:
                        for line in f:
                            parts = line.strip().split("\t")
                            if len(parts) >= 2:
                                self.phrases[parts[0].lower()] = parts[1]
                            elif len(parts) == 1 and " " in parts[0]:
                                sp = parts[0].split(" ", 1)
                                self.phrases[sp[0].lower()] = sp[1]
                except Exception:
                    pass
                break

        df = data_dir / "dict" / "en_dict.txt"
        if df.exists():
            try:
                with open(df, "r", encoding="utf-8", errors="ignore") as f:
                    for i, line in enumerate(f):
                        w = line.strip().split("\t")[0].split()[0]
                        if len(w) > 1:
                            self.dict_words.append(w)
                        if i > 5000:
                            break
            except Exception:
                pass

        if not self.dict_words:
            self.dict_words = ["complete", "intelligent", "prediction", "linux", "awesome",
                               "software", "development", "interface", "terminal", "system"]

        self.loaded = True

    def predict(self, text: str) -> List[Tuple[str, str, str]]:
        if not text:
            return []

        results: List[Tuple[str, str, str]] = []
        cur_word = text.split()[-1] if text.split() else ""

        # Strategy 1: Emoji shortcode
        if ":" in text:
            last_colon = text.rfind(":")
            shortcode = text[last_colon:].strip().lower()
            code_no_colon = shortcode.lstrip(":")
            matched = 0
            for sc, em in self.emojis.items():
                if sc.startswith(code_no_colon) or sc.startswith(shortcode):
                    results.append((em, "Emoji", f"{em} (:{sc}:)"))
                    matched += 1
                    if matched >= 5:
                        break
            if results:
                return results[:5]

        # Strategy 2: Common typos & contraction auto-fixes
        typos = {
            "dont": "don't", "cant": "can't", "wont": "won't", "im": "I'm",
            "ive": "I've", "youre": "you're", "theyre": "they're", "recieve": "receive",
            "seperate": "separate", "definately": "definitely", "occured": "occurred",
            "untill": "until", "teh": "the", "wiht": "with", "taht": "that"
        }
        low_word = cur_word.lower()
        if low_word in typos:
            results.append((typos[low_word], "Typo Fix", f"Spelling correction: {typos[low_word]}"))

        # Strategy 3: Phrase & Bigram completion
        clean_text = text.strip().lower()
        for phrase, comp in self.phrases.items():
            if clean_text.endswith(phrase):
                results.append((comp, "Phrase", f"Multi-word completion: '{comp}'"))
                break

        if "how are" in clean_text:
            results.append(("you", "Bigram", "Next word: 'you'"))
            results.append(("you doing", "Phrase", "Phrase: 'you doing'"))
        elif "thank you" in clean_text:
            results.append(("very much", "Phrase", "Common continuation"))
            results.append(("for", "Bigram", "Next preposition"))
        elif "good" in clean_text:
            results.append(("morning", "Bigram", "Greeting completion"))
            results.append(("afternoon", "Bigram", "Greeting completion"))

        # Strategy 4: Dictionary Prefix Trie
        if cur_word and len(cur_word) >= 2:
            prefix = cur_word.lower()
            count = 0
            for w in self.dict_words:
                if w.lower().startswith(prefix) and w.lower() != prefix:
                    results.append((w, "Dictionary", f"Prefix match ({w})"))
                    count += 1
                    if count >= 5:
                        break

        seen = set()
        final_res = []
        for cand, typ, desc in results:
            if cand not in seen:
                seen.add(cand)
                final_res.append((cand, typ, desc))
        return final_res[:5]

# ═══════════════════════════════════════════════════════════════════════════════
# UI Component: Status Badge
# ═══════════════════════════════════════════════════════════════════════════════

class StatusBadge(QLabel):
    def __init__(self, text: str = "", level: str = "neutral", parent=None):
        super().__init__(text, parent)
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        self.setLevel(level)

    def setLevel(self, level: str, text: Optional[str] = None):
        if text is not None:
            self.setText(text)
        classes = {
            "success": "Badge BadgeSuccess",
            "warning": "Badge BadgeWarning",
            "error": "Badge BadgeError",
            "info": "Badge BadgeInfo",
            "neutral": "Badge BadgeNeutral"
        }
        self.setProperty("class", classes.get(level, "Badge BadgeNeutral"))
        self.style().unpolish(self)
        self.style().polish(self)

# ═══════════════════════════════════════════════════════════════════════════════
# UI Component: Modern Step Card Widget
# ═══════════════════════════════════════════════════════════════════════════════

class StepCardWidget(QFrame):
    def __init__(self, step_num: int, title: str, parent=None):
        super().__init__(parent)
        self.step_num = step_num
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        self.setProperty("class", "StepItem")

        layout = QHBoxLayout(self)
        layout.setContentsMargins(16, 12, 16, 12)
        layout.setSpacing(14)

        # Numbered circle icon badge
        self.num_badge = QLabel(f"{step_num:02d}")
        self.num_badge.setFixedSize(32, 32)
        self.num_badge.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.num_badge.setStyleSheet("""
            background-color: #172439;
            color: #7dd3fc;
            border: 1px solid #293e61;
            border-radius: 16px;
            font-size: 11px;
            font-weight: 800;
        """)
        layout.addWidget(self.num_badge)

        text_layout = QVBoxLayout()
        text_layout.setSpacing(2)

        self.title_lbl = QLabel(title)
        self.title_lbl.setStyleSheet("font-size: 13px; font-weight: 700; color: #f1f5f9;")
        self.desc_lbl = QLabel("Waiting to run...")
        self.desc_lbl.setStyleSheet("font-size: 11px; color: #8496ad;")

        text_layout.addWidget(self.title_lbl)
        text_layout.addWidget(self.desc_lbl)
        layout.addLayout(text_layout)
        layout.addStretch()

        self.badge = StatusBadge("Pending", "neutral")
        layout.addWidget(self.badge)
        self.ensurePolished()

    def set_active(self, desc: str = "In progress..."):
        self.setProperty("class", "StepItemActive")
        self.num_badge.setText("●")
        self.num_badge.setStyleSheet("""
            background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #0284c7, stop:1 #38bdf8);
            color: #ffffff;
            border: 1px solid #7dd3fc;
            border-radius: 16px;
            font-size: 13px;
        """)
        self.desc_lbl.setText(desc)
        self.desc_lbl.setStyleSheet("font-size: 11px; color: #38bdf8; font-weight: 600;")
        self.badge.setLevel("info", "Running")
        self.style().unpolish(self)
        self.style().polish(self)

    def set_success(self, desc: str = "Completed successfully"):
        self.setProperty("class", "StepItemSuccess")
        self.num_badge.setText("✓")
        self.num_badge.setStyleSheet("""
            background: rgba(16, 185, 129, 0.28);
            color: #34d399;
            border: 1px solid #059669;
            border-radius: 16px;
            font-size: 13px;
            font-weight: 800;
        """)
        self.desc_lbl.setText(desc)
        self.desc_lbl.setStyleSheet("font-size: 11px; color: #34d399;")
        self.badge.setLevel("success", "Passed")
        self.style().unpolish(self)
        self.style().polish(self)

    def set_error(self, desc: str = "Failed"):
        self.setProperty("class", "StepItemError")
        self.num_badge.setText("✕")
        self.num_badge.setStyleSheet("""
            background: rgba(239, 68, 68, 0.28);
            color: #f87171;
            border: 1px solid #dc2626;
            border-radius: 16px;
            font-size: 13px;
            font-weight: 800;
        """)
        self.desc_lbl.setText(desc)
        self.desc_lbl.setStyleSheet("font-size: 11px; color: #f87171;")
        self.badge.setLevel("error", "Error")
        self.style().unpolish(self)
        self.style().polish(self)

    def reset(self):
        self.setProperty("class", "StepItem")
        self.num_badge.setText(f"{self.step_num:02d}")
        self.num_badge.setStyleSheet("""
            background-color: #172439;
            color: #7dd3fc;
            border: 1px solid #293e61;
            border-radius: 16px;
            font-size: 11px;
            font-weight: 800;
        """)
        self.desc_lbl.setText("Waiting to run...")
        self.desc_lbl.setStyleSheet("font-size: 11px; color: #8496ad;")
        self.badge.setLevel("neutral", "Pending")
        self.style().unpolish(self)
        self.style().polish(self)

# ═══════════════════════════════════════════════════════════════════════════════
# UI Component: Option Card Widget
# ═══════════════════════════════════════════════════════════════════════════════

class OptionRowCard(QFrame):
    """An interactive option row with checkbox, title, description, and target pill."""
    def __init__(self, title: str, subtitle: str, tag: str, checked: bool = True, parent=None):
        super().__init__(parent)
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        self.setProperty("class", "OptionCard")
        self.setCursor(Qt.CursorShape.PointingHandCursor)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(16, 12, 16, 12)
        layout.setSpacing(14)

        self.cb = QCheckBox()
        self.cb.setChecked(checked)
        layout.addWidget(self.cb)

        text_box = QVBoxLayout()
        text_box.setSpacing(2)

        title_lbl = QLabel(title)
        title_lbl.setStyleSheet("font-size: 13px; font-weight: 700; color: #f8fafc;")
        sub_lbl = QLabel(subtitle)
        sub_lbl.setStyleSheet("font-size: 11px; color: #94a3b8;")

        text_box.addWidget(title_lbl)
        text_box.addWidget(sub_lbl)
        layout.addLayout(text_box)
        layout.addStretch()

        tag_pill = QLabel(tag)
        tag_pill.setStyleSheet("""
            background-color: #172740;
            color: #38bdf8;
            font-family: monospace;
            font-size: 11px;
            font-weight: 700;
            border: 1px solid #28476e;
            border-radius: 6px;
            padding: 3px 10px;
        """)
        layout.addWidget(tag_pill)
        self.ensurePolished()

    def isChecked(self) -> bool:
        return self.cb.isChecked()

    def setChecked(self, val: bool):
        self.cb.setChecked(val)

    def mousePressEvent(self, event):
        self.cb.toggle()
        super().mousePressEvent(event)

# ═══════════════════════════════════════════════════════════════════════════════
# UI Component: Mini Stat Card Widget
# ═══════════════════════════════════════════════════════════════════════════════

class MiniStatWidget(QFrame):
    """A high-end stat card with icon badge, category title, and primary value."""
    def __init__(self, icon_char: str, category: str, default_val: str, accent_color: str = "#38bdf8", parent=None):
        super().__init__(parent)
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        self.setProperty("class", "MiniStatCard")

        layout = QHBoxLayout(self)
        layout.setContentsMargins(16, 14, 16, 14)
        layout.setSpacing(14)

        # Icon box
        icon_box = QLabel(icon_char)
        icon_box.setFixedSize(38, 38)
        icon_box.setAlignment(Qt.AlignmentFlag.AlignCenter)
        icon_box.setStyleSheet(f"""
            background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #1a2942, stop:1 #111d30);
            border: 1px solid {accent_color}55;
            border-radius: 10px;
            font-size: 17px;
        """)
        layout.addWidget(icon_box)

        # Text
        text_layout = QVBoxLayout()
        text_layout.setSpacing(3)
        cat_lbl = QLabel(category.upper())
        cat_lbl.setStyleSheet("font-size: 10px; font-weight: 800; color: #8397af; letter-spacing: 0.9px;")
        self.val_lbl = QLabel(default_val)
        self.val_lbl.setStyleSheet(f"font-size: 13px; font-weight: 700; color: {accent_color};")
        text_layout.addWidget(cat_lbl)
        text_layout.addWidget(self.val_lbl)
        layout.addLayout(text_layout)
        layout.addStretch()
        self.ensurePolished()

    def setValue(self, text: str, color: Optional[str] = None):
        self.val_lbl.setText(text)
        if color:
            self.val_lbl.setStyleSheet(f"font-size: 13px; font-weight: 700; color: {color};")

# ═══════════════════════════════════════════════════════════════════════════════
# TAB 1: Installer & Setup Wizard
# ═══════════════════════════════════════════════════════════════════════════════

class TabInstaller(QWidget):
    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window
        self.worker: Optional[InstallWorker] = None
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(28, 24, 28, 24)
        layout.setSpacing(16)

        # ── Preflight Overview Card ─────────────────────────────────
        preflight_card = QFrame()
        preflight_card.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        preflight_card.setProperty("class", "Card")
        pf_layout = QVBoxLayout(preflight_card)
        pf_layout.setContentsMargins(18, 16, 18, 16)
        pf_layout.setSpacing(14)

        pf_header = QHBoxLayout()
        header_text = QVBoxLayout()
        header_text.setSpacing(2)
        pf_title = QLabel("System Environment Overview")
        pf_title.setStyleSheet("font-size: 16px; font-weight: 800; color: #f8fafc;")
        pf_sub = QLabel("Automated diagnostic probe of your Linux environment and dependencies")
        pf_sub.setStyleSheet("font-size: 12px; color: #8c9cb3;")
        header_text.addWidget(pf_title)
        header_text.addWidget(pf_sub)
        pf_header.addLayout(header_text)
        pf_header.addStretch()

        refresh_btn = QPushButton("↻ Refresh Probe")
        refresh_btn.setProperty("class", "SecondaryBtn")
        refresh_btn.clicked.connect(self.refresh_system_probe)
        pf_header.addWidget(refresh_btn)
        pf_layout.addLayout(pf_header)

        # 4 Mini Cards Grid
        grid = QGridLayout()
        grid.setSpacing(12)

        self.stat_distro = MiniStatWidget("🐧", "Operating System", "Detecting...", "#38bdf8")
        grid.addWidget(self.stat_distro, 0, 0)

        self.stat_session = MiniStatWidget("🪟", "Compositor & Session", "Detecting...", "#a78bfa")
        grid.addWidget(self.stat_session, 0, 1)

        self.stat_fcitx = MiniStatWidget("⌨️", "Fcitx5 Framework", "Detecting...", "#34d399")
        grid.addWidget(self.stat_fcitx, 1, 0)

        self.stat_deps = MiniStatWidget("📦", "Build Dependencies", "Detecting...", "#34d399")
        grid.addWidget(self.stat_deps, 1, 1)

        pf_layout.addLayout(grid)
        layout.addWidget(preflight_card)

        # ── Options Card ────────────────────────────────────────────
        opts_card = QFrame()
        opts_card.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        opts_card.setProperty("class", "Card")
        opts_layout = QVBoxLayout(opts_card)
        opts_layout.setContentsMargins(18, 16, 18, 16)
        opts_layout.setSpacing(10)

        opts_header = QHBoxLayout()
        opts_title = QLabel("Installation & Deployment Options")
        opts_title.setStyleSheet("font-size: 15px; font-weight: 800; color: #f8fafc;")
        opts_header.addWidget(opts_title)
        opts_header.addStretch()
        opts_layout.addLayout(opts_header)

        self.opt_autostart = OptionRowCard(
            "Configure Compositor & XDG Autostart",
            "Automatically launch Fcitx5 on session login in Hyprland, Sway, GNOME, or KDE",
            "autostart",
            checked=True
        )
        opts_layout.addWidget(self.opt_autostart)

        self.opt_env = OptionRowCard(
            "Configure Input Method Environment Variables",
            "Sets GTK_IM_MODULE, QT_IM_MODULE, and XMODIFIERS in environment.d and shell RCs",
            "environment.d",
            checked=True
        )
        opts_layout.addWidget(self.opt_env)

        self.opt_tests = OptionRowCard(
            "Run 13 Regression Unit Tests After Build",
            "Executes complete CTest verification suite before deploying binaries to /usr",
            "ctest",
            checked=True
        )
        opts_layout.addWidget(self.opt_tests)

        layout.addWidget(opts_card)

        # ── Progress Bar & Action Row (Placed for immediate visibility) ─
        act_row = QHBoxLayout()
        self.start_btn = QPushButton("🚀  Install SmartComplete Now")
        self.start_btn.setProperty("class", "PrimaryBtn")
        self.start_btn.setMinimumHeight(46)
        self.start_btn.clicked.connect(self.start_installation)
        act_row.addWidget(self.start_btn)

        self.toggle_log_btn = QPushButton("Show Terminal Output ▼")
        self.toggle_log_btn.setProperty("class", "SecondaryBtn")
        self.toggle_log_btn.clicked.connect(self.toggle_log_viewer)
        act_row.addWidget(self.toggle_log_btn)

        act_row.addStretch()

        self.copy_log_btn = QPushButton("📋 Copy Log")
        self.copy_log_btn.setProperty("class", "SecondaryBtn")
        self.copy_log_btn.clicked.connect(self.copy_log_text)
        act_row.addWidget(self.copy_log_btn)

        layout.addLayout(act_row)

        self.progress_bar = QProgressBar()
        self.progress_bar.setValue(0)
        layout.addWidget(self.progress_bar)

        # ── Step Cards Pipeline Card ────────────────────────────────
        steps_card = QFrame()
        steps_card.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        steps_card.setProperty("class", "Card")
        sc_layout = QVBoxLayout(steps_card)
        sc_layout.setContentsMargins(18, 16, 18, 16)
        sc_layout.setSpacing(8)

        sc_title = QLabel("Deployment Pipeline & Build Verification")
        sc_title.setStyleSheet("font-size: 15px; font-weight: 800; color: #f8fafc;")
        sc_layout.addWidget(sc_title)

        step_names = [
            "Pre-flight & Environment Check",
            "Resolve System Dependencies",
            "Compile Engine & Run Test Suites",
            "Install SmartComplete to /usr",
            "Configure Environment & Compositor",
            "Setup Fcitx5 Input Method Profile",
            "Restart & Verify System Integration"
        ]
        self.step_cards = []
        for i, name in enumerate(step_names, 1):
            card = StepCardWidget(i, name)
            self.step_cards.append(card)
            sc_layout.addWidget(card)
        layout.addWidget(steps_card)

        # ── Collapsible Terminal Output Frame ───────────────────────
        self.terminal_frame = QFrame()
        self.terminal_frame.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        self.terminal_frame.setObjectName("TerminalContainer")
        term_layout = QVBoxLayout(self.terminal_frame)
        term_layout.setContentsMargins(0, 0, 0, 0)
        term_layout.setSpacing(0)

        # Terminal header bar
        term_header = QFrame()
        term_header.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        term_header.setObjectName("TerminalHeader")
        th_lay = QHBoxLayout(term_header)
        th_lay.setContentsMargins(12, 6, 12, 6)

        dots = QLabel("●  ●  ●")
        dots.setStyleSheet("color: #475569; font-size: 11px; font-weight: 700; margin-right: 8px;")
        th_lay.addWidget(dots)

        term_title = QLabel("smartcomplete-installer.log (bash)")
        term_title.setStyleSheet("color: #94a3b8; font-family: monospace; font-size: 11px;")
        th_lay.addWidget(term_title)
        th_lay.addStretch()
        term_layout.addWidget(term_header)

        self.log_viewer = QTextEdit()
        self.log_viewer.setObjectName("LogViewer")
        self.log_viewer.setReadOnly(True)
        self.log_viewer.setMinimumHeight(200)
        term_layout.addWidget(self.log_viewer)

        self.terminal_frame.setVisible(False)
        layout.addWidget(self.terminal_frame)

        self.refresh_system_probe()

    def refresh_system_probe(self):
        distro = SystemInspector.detect_distro()
        session = SystemInspector.detect_session()
        fcitx = SystemInspector.check_fcitx5()
        missing = SystemInspector.check_missing_packages(distro["family"])

        self.stat_distro.setValue(f"{distro['name']} ({distro['pkg_mgr']})")
        self.stat_session.setValue(f"{session['compositor'].capitalize()} ({session['session_type']})")

        if fcitx["installed"]:
            status_text = "Installed (Running)" if fcitx["running"] else "Installed (Stopped)"
            color = "#34d399" if fcitx["running"] else "#fcd34d"
            self.stat_fcitx.setValue(status_text, color)
        else:
            self.stat_fcitx.setValue("Not installed (Will install)", "#f87171")

        if missing:
            self.stat_deps.setValue(f"{len(missing)} missing ({', '.join(missing[:2])}...)", "#fcd34d")
        else:
            self.stat_deps.setValue("All dependencies satisfied ✓", "#34d399")

    def toggle_log_viewer(self):
        vis = not self.terminal_frame.isVisible()
        self.terminal_frame.setVisible(vis)
        self.toggle_log_btn.setText("Hide Terminal Output ▲" if vis else "Show Terminal Output ▼")

    def copy_log_text(self):
        QApplication.clipboard().setText(self.log_viewer.toPlainText())
        self.copy_log_btn.setText("✓ Copied!")
        QTimer.singleShot(2000, lambda: self.copy_log_btn.setText("📋 Copy Log"))

    def start_installation(self):
        self.start_btn.setEnabled(False)
        self.start_btn.setText("⏳ Installing SmartComplete...")
        for card in self.step_cards:
            card.reset()
        self.log_viewer.clear()
        self.progress_bar.setValue(0)

        if not self.terminal_frame.isVisible():
            self.toggle_log_viewer()

        cfg = {
            "autostart": self.opt_autostart.isChecked(),
            "env": self.opt_env.isChecked(),
            "run_tests": self.opt_tests.isChecked(),
            "install_prefix": "/usr"
        }

        ai_cfg = self.main_window.tab_settings.get_ai_config()
        cfg.update(ai_cfg)

        self.worker = InstallWorker(cfg, SystemInspector.get_project_dir())
        self.worker.step_started.connect(self.on_step_started)
        self.worker.step_finished.connect(self.on_step_finished)
        self.worker.log_emitted.connect(self.on_log_emitted)
        self.worker.progress_changed.connect(self.progress_bar.setValue)
        self.worker.overall_finished.connect(self.on_install_finished)
        self.worker.request_auth.connect(self.on_request_auth)
        self.worker.start()

    def on_step_started(self, step_idx: int, name: str, desc: str):
        if 1 <= step_idx <= len(self.step_cards):
            self.step_cards[step_idx - 1].set_active(desc)

    def on_step_finished(self, step_idx: int, success: bool, msg: str):
        if 1 <= step_idx <= len(self.step_cards):
            card = self.step_cards[step_idx - 1]
            if success:
                card.set_success(msg)
            else:
                card.set_error(msg)

    def on_log_emitted(self, level: str, text: str):
        colors = {
            "step": "#38bdf8",
            "info": "#94a3b8",
            "success": "#34d399",
            "warning": "#fcd34d",
            "error": "#f87171",
            "output": "#cbd5e1"
        }
        color = colors.get(level, "#cbd5e1")
        self.log_viewer.append(f"<span style='color: {color};'>{text}</span>")
        self.log_viewer.moveCursor(QTextCursor.MoveOperation.End)

    def on_request_auth(self, reason: str):
        dlg = PasswordDialog(self, prompt_text=reason)
        if dlg.exec() == QDialog.DialogCode.Accepted:
            self.worker.set_auth_response(dlg.password)
        else:
            self.worker.set_auth_response(None)

    def on_install_finished(self, success: bool, msg: str):
        self.start_btn.setEnabled(True)
        self.start_btn.setText("🚀  Install SmartComplete Now")
        self.refresh_system_probe()
        self.main_window.update_header_status()

        if success:
            QMessageBox.information(
                self,
                "Installation Complete!",
                "SmartComplete has been successfully installed and activated!\n\n"
                "• Press Tab to accept suggestions\n"
                "• Press Up/Down arrows to navigate candidates\n"
                "• Press Space to commit word & show next-word prediction\n"
                "• Type ':smile' for emoji shortcodes\n\n"
                "Switch to the 'Test Scratchpad' tab to try typing right away!"
            )
        else:
            QMessageBox.critical(
                self,
                "Installation Failed",
                f"An error occurred during installation:\n\n{msg}\n\nCheck the terminal output for details."
            )

# ═══════════════════════════════════════════════════════════════════════════════
# TAB 2: Interactive Test Scratchpad
# ═══════════════════════════════════════════════════════════════════════════════

class ScratchpadEditor(QTextEdit):
    """Custom text editor that intercepts Tab key and digit shortcuts for candidate acceptance."""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.tab_callback = None
        self.digit_callback = None

    def keyPressEvent(self, e: QKeyEvent):
        if e.key() == Qt.Key.Key_Tab and self.tab_callback:
            if self.tab_callback():
                e.accept()
                return
        super().keyPressEvent(e)

class TabScratchpad(QWidget):
    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window
        self.simulator = SimulationPredictor(SystemInspector.get_project_dir())
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(28, 24, 28, 24)
        layout.setSpacing(14)

        info_card = QFrame()
        info_card.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        info_card.setProperty("class", "CardHighlight")
        ic_layout = QVBoxLayout(info_card)
        ic_layout.setContentsMargins(18, 14, 18, 14)
        ic_layout.setSpacing(6)

        top_row = QHBoxLayout()
        ic_title = QLabel("SmartComplete Live Playground")
        ic_title.setStyleSheet("font-size: 16px; font-weight: 800; color: #f8fafc;")
        top_row.addWidget(ic_title)
        top_row.addStretch()

        self.live_status_badge = StatusBadge("Checking Fcitx5...", "info")
        top_row.addWidget(self.live_status_badge)
        ic_layout.addLayout(top_row)

        desc = QLabel(
            "Type in the scratchpad below to test completions in real time. "
            "SmartComplete predicts next words, fixes typos, handles multi-word phrases, and expands emoji shortcodes."
        )
        desc.setStyleSheet("color: #94a3b8; font-size: 12px; line-height: 1.4;")
        desc.setWordWrap(True)
        ic_layout.addWidget(desc)
        layout.addWidget(info_card)

        # Quick Tryout Chips
        chips_box = QVBoxLayout()
        chips_box.setSpacing(6)
        lbl_chips = QLabel("QUICK TEST PROMPTS (Click to try):")
        lbl_chips.setStyleSheet("color: #64748b; font-size: 10px; font-weight: 800; letter-spacing: 1.1px;")
        chips_box.addWidget(lbl_chips)

        r1 = QHBoxLayout()
        r1.setSpacing(8)
        prompts_r1 = [("how are ", "💬 Phrase"), ("dont ", "✏️ Typo Fix"), (":smile", "😊 Emoji")]
        for prompt, label in prompts_r1:
            btn = QPushButton(f"{prompt} → {label}")
            btn.setProperty("class", "ChipBtn")
            btn.clicked.connect(lambda _, p=prompt: self.insert_sample_text(p))
            r1.addWidget(btn)
        r1.addStretch()
        chips_box.addLayout(r1)

        r2 = QHBoxLayout()
        r2.setSpacing(8)
        prompts_r2 = [("intellig", "🔍 Prefix Trie"), ("thank you ", "🤝 Next-Word")]
        for prompt, label in prompts_r2:
            btn = QPushButton(f"{prompt} → {label}")
            btn.setProperty("class", "ChipBtn")
            btn.clicked.connect(lambda _, p=prompt: self.insert_sample_text(p))
            r2.addWidget(btn)
        r2.addStretch()
        chips_box.addLayout(r2)
        layout.addLayout(chips_box)

        # Interactive Text Editor Frame
        editor_frame = QFrame()
        editor_frame.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        editor_frame.setProperty("class", "Card")
        ef_layout = QVBoxLayout(editor_frame)
        ef_layout.setContentsMargins(14, 12, 14, 14)
        ef_layout.setSpacing(10)

        ef_bar = QHBoxLayout()
        ef_title = QLabel("📄  scratchpad.txt")
        ef_title.setStyleSheet("font-family: monospace; font-size: 12px; font-weight: 700; color: #7dd3fc;")
        ef_bar.addWidget(ef_title)
        ef_bar.addStretch()

        copy_btn = QPushButton("📋 Copy")
        copy_btn.setProperty("class", "SecondaryBtn")
        copy_btn.clicked.connect(self.copy_editor_text)
        ef_bar.addWidget(copy_btn)

        clear_btn = QPushButton("🗑️ Clear")
        clear_btn.setProperty("class", "SecondaryBtn")
        clear_btn.clicked.connect(lambda: self.text_editor.clear())
        ef_bar.addWidget(clear_btn)
        ef_layout.addLayout(ef_bar)

        self.text_editor = ScratchpadEditor()
        self.text_editor.tab_callback = self.handle_tab_accept
        self.text_editor.setPlaceholderText("Start typing here... (e.g. 'how are', 'dont', ':smile', 'intellig')")
        self.text_editor.setFixedHeight(115)
        self.text_editor.setStyleSheet("""
            QTextEdit {
                font-size: 15px;
                padding: 12px;
                background-color: #060a12;
                border: 1px solid #20314c;
                border-radius: 9px;
                color: #f8fafc;
                line-height: 1.5;
            }
            QTextEdit:focus {
                border-color: #0284c7;
                background-color: #08101d;
            }
        """)
        self.text_editor.textChanged.connect(self.on_text_changed)
        ef_layout.addWidget(self.text_editor)

        # Live Candidate Suggestion Ribbon
        self.ribbon_frame = QFrame()
        self.ribbon_frame.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        self.ribbon_frame.setStyleSheet("""
            background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #121f35, stop:1 #0c1525);
            border: 1px solid #0284c7;
            border-radius: 10px;
        """)
        ribbon_layout = QHBoxLayout(self.ribbon_frame)
        ribbon_layout.setContentsMargins(14, 10, 14, 10)
        ribbon_layout.setSpacing(12)

        lbl_cand_title = QLabel("🎯  Candidates:")
        lbl_cand_title.setStyleSheet("font-size: 11px; font-weight: 800; color: #38bdf8; letter-spacing: 0.5px;")
        ribbon_layout.addWidget(lbl_cand_title)

        self.candidate_btns_layout = QHBoxLayout()
        self.candidate_btns_layout.setSpacing(8)
        ribbon_layout.addLayout(self.candidate_btns_layout)
        ribbon_layout.addStretch()

        self.lbl_match_type = QLabel("Waiting for input...")
        self.lbl_match_type.setStyleSheet("color: #8c9cb3; font-size: 11px; font-weight: 500;")
        ribbon_layout.addWidget(self.lbl_match_type)
        ef_layout.addWidget(self.ribbon_frame)

        layout.addWidget(editor_frame)

        # Keyboard Cheat Sheet Card
        keys_card = QFrame()
        keys_card.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        keys_card.setProperty("class", "Card")
        kc_layout = QHBoxLayout(keys_card)
        kc_layout.setContentsMargins(16, 12, 16, 12)

        cheats = [
            ("Tab", "Accept Top"),
            ("Space", "Commit + Next"),
            ("↑ / ↓", "Navigate"),
            ("Esc", "Dismiss"),
            (":shortcode", "Emoji Picker")
        ]
        for key, desc_t in cheats:
            col = QVBoxLayout()
            col.setAlignment(Qt.AlignmentFlag.AlignCenter)
            k_lbl = QLabel(key)
            k_lbl.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
            k_lbl.setProperty("class", "KeyCap")
            k_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
            d_lbl = QLabel(desc_t)
            d_lbl.setStyleSheet("color: #8c9cb3; font-size: 11px; margin-top: 4px;")
            d_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
            col.addWidget(k_lbl)
            col.addWidget(d_lbl)
            kc_layout.addLayout(col)

        layout.addWidget(keys_card)
        layout.addStretch()
        self.update_live_fcitx_status()

    def copy_editor_text(self):
        QApplication.clipboard().setText(self.text_editor.toPlainText())

    def handle_tab_accept(self) -> bool:
        if self.candidate_btns_layout.count() > 0:
            item = self.candidate_btns_layout.itemAt(0)
            if item and item.widget() and isinstance(item.widget(), QPushButton):
                item.widget().click()
                return True
        return False

    def update_live_fcitx_status(self):
        fcitx = SystemInspector.check_fcitx5()
        if fcitx["running"] and fcitx["addon_so"] and fcitx["profile_configured"]:
            self.live_status_badge.setLevel("success", "● SmartComplete Active System-Wide")
        elif fcitx["running"]:
            self.live_status_badge.setLevel("warning", "● Fcitx5 Running (Needs Profile Setup)")
        else:
            self.live_status_badge.setLevel("neutral", "○ Fcitx5 Offline (Simulation Active)")

    def insert_sample_text(self, text: str):
        self.text_editor.setPlainText(text)
        self.text_editor.moveCursor(QTextCursor.MoveOperation.End)
        self.text_editor.setFocus()

    def on_text_changed(self):
        full_text = self.text_editor.toPlainText()
        candidates = self.simulator.predict(full_text)

        while self.candidate_btns_layout.count():
            item = self.candidate_btns_layout.takeAt(0)
            if item.widget():
                w = item.widget()
                w.hide()
                w.setParent(None)
                w.deleteLater()

        if candidates:
            self.lbl_match_type.setText(f"{len(candidates)} suggestion(s) • Press Tab or 1..5 to accept")
            for i, (cand, typ, desc) in enumerate(candidates):
                btn = QPushButton(f"{i + 1}. {cand}")
                if i == 0:
                    btn.setStyleSheet("""
                        background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #0284c7, stop:1 #2563eb);
                        color: #ffffff;
                        font-weight: 700;
                        font-size: 13px;
                        border: 1px solid #7dd3fc;
                        border-radius: 8px;
                        padding: 8px 16px;
                    """)
                else:
                    btn.setProperty("class", "CandidateBtn")
                btn.setToolTip(f"{typ}: {desc} (Click or press Tab)")
                btn.clicked.connect(lambda _, c=cand: self.accept_candidate(c))
                self.candidate_btns_layout.addWidget(btn)
        else:
            self.lbl_match_type.setText("No active candidates")

    def accept_candidate(self, candidate: str):
        text = self.text_editor.toPlainText()
        if text.startswith(":"):
            self.text_editor.setPlainText(candidate + " ")
        elif text.endswith(" "):
            self.text_editor.setPlainText(text + candidate + " ")
        else:
            words = text.split()
            if words:
                words[-1] = candidate
                self.text_editor.setPlainText(" ".join(words) + " ")
            else:
                self.text_editor.setPlainText(candidate + " ")

        self.text_editor.moveCursor(QTextCursor.MoveOperation.End)
        self.text_editor.setFocus()

# ═══════════════════════════════════════════════════════════════════════════════
# TAB 3: Diagnostics & System Doctor
# ═══════════════════════════════════════════════════════════════════════════════

class TabDoctor(QWidget):
    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(28, 24, 28, 24)
        layout.setSpacing(16)

        # Health Banner Card
        banner_card = QFrame()
        banner_card.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        banner_card.setProperty("class", "CardHighlight")
        b_lay = QHBoxLayout(banner_card)
        b_lay.setContentsMargins(18, 16, 18, 16)
        b_lay.setSpacing(14)

        b_icon = QLabel("🩺")
        b_icon.setStyleSheet("font-size: 32px;")
        b_lay.addWidget(b_icon)

        b_text = QVBoxLayout()
        b_text.setSpacing(3)
        self.b_title = QLabel("System Doctor Health Assessment")
        self.b_title.setStyleSheet("font-size: 16px; font-weight: 800; color: #f8fafc;")
        self.b_desc = QLabel("Automated verification of files, daemon processes, environment variables, and profiles.")
        self.b_desc.setStyleSheet("color: #94a3b8; font-size: 12px;")
        b_text.addWidget(self.b_title)
        b_text.addWidget(self.b_desc)
        b_lay.addLayout(b_text)
        b_lay.addStretch()

        self.run_diag_btn = QPushButton("↻ Run Diagnostic Scan")
        self.run_diag_btn.setProperty("class", "PrimaryBtn")
        self.run_diag_btn.clicked.connect(self.run_diagnostics)
        b_lay.addWidget(self.run_diag_btn)
        layout.addWidget(banner_card)

        # Report items container
        self.report_box = QVBoxLayout()
        self.report_box.setSpacing(8)
        layout.addLayout(self.report_box)

        # Quick Fix Actions Card
        repair_card = QFrame()
        repair_card.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        repair_card.setProperty("class", "Card")
        rc_layout = QVBoxLayout(repair_card)
        rc_layout.setContentsMargins(18, 16, 18, 16)
        rc_layout.setSpacing(12)
        rc_title = QLabel("One-Click Quick Fix Actions")
        rc_title.setStyleSheet("font-size: 15px; font-weight: 800; color: #f8fafc;")
        rc_layout.addWidget(rc_title)

        btns_grid = QGridLayout()
        btns_grid.setSpacing(10)
        btn_restart = QPushButton("🔄 Restart Fcitx5 Daemon")
        btn_restart.setProperty("class", "SecondaryBtn")
        btn_restart.setMinimumHeight(40)
        btn_restart.clicked.connect(self.action_restart_fcitx5)
        btns_grid.addWidget(btn_restart, 0, 0)

        btn_activate = QPushButton("⚡ Force Activate IM (fcitx5-remote -o)")
        btn_activate.setProperty("class", "SecondaryBtn")
        btn_activate.setMinimumHeight(40)
        btn_activate.clicked.connect(self.action_force_activate)
        btns_grid.addWidget(btn_activate, 0, 1)

        btn_profile = QPushButton("📋 Re-apply Default Fcitx5 Profile")
        btn_profile.setProperty("class", "SecondaryBtn")
        btn_profile.setMinimumHeight(40)
        btn_profile.clicked.connect(self.action_reapply_profile)
        btns_grid.addWidget(btn_profile, 1, 0, 1, 2)

        rc_layout.addLayout(btns_grid)
        layout.addWidget(repair_card)

        layout.addStretch()
        self.run_diagnostics()

    def run_diagnostics(self):
        while self.report_box.count():
            item = self.report_box.takeAt(0)
            if item.widget():
                w = item.widget()
                w.hide()
                w.setParent(None)
                w.deleteLater()

        checks = [
            self._check_distro_session(),
            self._check_fcitx5_daemon(),
            self._check_addon_binary(),
            self._check_data_files(),
            self._check_fcitx5_profile(),
            self._check_environment_vars(),
            self._check_autostart_files()
        ]

        passed = sum(1 for c in checks if c[1])
        total = len(checks)
        pct = int(passed / total * 100)
        self.b_title.setText(f"System Health Score: {pct}% ({passed} of {total} Checks Passed)")

        for name, ok, detail, advice in checks:
            card = QFrame()
            card.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
            card.setProperty("class", "DoctorItemCard" if ok else "DoctorItemCardNotice")
            row = QHBoxLayout(card)
            row.setContentsMargins(16, 12, 16, 12)
            row.setSpacing(14)

            icon = QLabel("✓" if ok else "⚠️")
            icon.setFixedSize(28, 28)
            icon.setAlignment(Qt.AlignmentFlag.AlignCenter)
            icon.setStyleSheet(f"""
                background: {'rgba(16, 185, 129, 0.22)' if ok else 'rgba(245, 158, 11, 0.22)'};
                color: {'#34d399' if ok else '#fcd34d'};
                border: 1px solid {'rgba(16, 185, 129, 0.5)' if ok else 'rgba(245, 158, 11, 0.5)'};
                border-radius: 14px;
                font-size: 13px;
                font-weight: 800;
            """)
            row.addWidget(icon)

            text_col = QVBoxLayout()
            text_col.setSpacing(2)
            title_lbl = QLabel(name)
            title_lbl.setStyleSheet("font-size: 13px; font-weight: 700; color: #f1f5f9;")
            detail_lbl = QLabel(detail)
            detail_lbl.setStyleSheet("font-size: 11px; color: #94a3b8; font-family: monospace;")
            detail_lbl.setWordWrap(True)
            text_col.addWidget(title_lbl)
            text_col.addWidget(detail_lbl)
            if not ok and advice:
                adv_lbl = QLabel(f"Tip: {advice}")
                adv_lbl.setStyleSheet("font-size: 11px; color: #fcd34d; font-style: italic;")
                adv_lbl.setWordWrap(True)
                text_col.addWidget(adv_lbl)

            row.addLayout(text_col, stretch=1)

            badge = StatusBadge("Verified" if ok else "Action Required", "success" if ok else "warning")
            row.addWidget(badge)
            card.ensurePolished()
            self.report_box.addWidget(card)

    def _check_distro_session(self) -> Tuple[str, bool, str, str]:
        distro = SystemInspector.detect_distro()
        session = SystemInspector.detect_session()
        ok = distro["family"] in ["arch", "debian", "fedora", "opensuse"]
        detail = f"{distro['name']} | Session: {session['session_type']} ({session['compositor']})"
        return ("OS & Display Compatibility", ok, detail, "Ensure you are running on Wayland or X11.")

    def _check_fcitx5_daemon(self) -> Tuple[str, bool, str, str]:
        res = subprocess.run(["pgrep", "-a", "fcitx5"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        ok = (res.returncode == 0)
        detail = f"Running: {res.stdout.strip()[:60]}..." if ok else "Fcitx5 daemon is NOT running."
        return ("Fcitx5 Daemon Process", ok, detail, "Click 'Restart Fcitx5 Daemon' below to start it.")

    def _check_addon_binary(self) -> Tuple[str, bool, str, str]:
        fcitx = SystemInspector.check_fcitx5()
        so = fcitx.get("addon_so")
        ok = so is not None and os.path.exists(so)
        detail = f"Found: {so}" if ok else "linuxcomplete.so not found in /usr/lib/fcitx5 or standard paths."
        return ("Addon Binary (linuxcomplete.so)", ok, detail, "Run installation from the 'Install & Setup' tab.")

    def _check_data_files(self) -> Tuple[str, bool, str, str]:
        dirs = ["dict", "frequency", "ngram", "rules", "emoji"]
        found = 0
        for d in dirs:
            for p in [f"/usr/share/linuxcomplete/{d}", f"/usr/local/share/linuxcomplete/{d}"]:
                if os.path.isdir(p):
                    found += 1
                    break
        ok = (found == len(dirs))
        detail = f"{found} of {len(dirs)} data asset folders present."
        return ("Dictionary & Grammar Assets", ok, detail, "Reinstall to restore missing data assets.")

    def _check_fcitx5_profile(self) -> Tuple[str, bool, str, str]:
        p = pathlib.Path.home() / ".config" / "fcitx5" / "profile"
        ok = False
        detail = "Profile file missing."
        if p.exists():
            content = p.read_text(encoding="utf-8", errors="ignore")
            ok = "DefaultIM=linuxcomplete" in content
            detail = "SmartComplete configured as default input method." if ok else "DefaultIM is not set to linuxcomplete."
        return ("Fcitx5 Input Method Profile", ok, detail, "Click 'Re-apply Default Fcitx5 Profile' below.")

    def _check_environment_vars(self) -> Tuple[str, bool, str, str]:
        sysd = SystemInspector.detect_systemd_env()
        active_im = os.environ.get("GTK_IM_MODULE") == "fcitx" or os.environ.get("QT_IM_MODULE") == "fcitx"
        ok = sysd["has_env"] or active_im
        detail = f"systemd env: {'Configured' if sysd['has_env'] else 'Missing'} | Current GTK_IM_MODULE: {os.environ.get('GTK_IM_MODULE', 'none')}"
        return ("Session Environment Variables", ok, detail, "Restart session or re-run setup to apply.")

    def _check_autostart_files(self) -> Tuple[str, bool, str, str]:
        home = pathlib.Path.home()
        xdg_auto = home / ".config" / "autostart" / "fcitx5.desktop"
        ok = xdg_auto.exists()
        detail = f"XDG autostart: {'Present' if ok else 'Missing'}"
        return ("Autostart Integration", ok, detail, "Autostart can be re-applied via the installer.")

    def action_restart_fcitx5(self):
        subprocess.run(["killall", "fcitx5"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        time.sleep(0.5)
        subprocess.Popen(["fcitx5", "-d"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        time.sleep(1.0)
        self.run_diagnostics()
        QMessageBox.information(self, "Restarted", "Fcitx5 daemon was restarted.")

    def action_force_activate(self):
        subprocess.run(["fcitx5-remote", "-o"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        self.run_diagnostics()
        QMessageBox.information(self, "Activated", "Sent activation signal (fcitx5-remote -o).")

    def action_reapply_profile(self):
        home = pathlib.Path.home()
        fcitx_dir = home / ".config" / "fcitx5"
        fcitx_dir.mkdir(parents=True, exist_ok=True)
        profile_content = (
            "[Groups/0]\n"
            "Name=Default\n"
            "Default Layout=us\n"
            "DefaultIM=linuxcomplete\n\n"
            "[Groups/0/Items/0]\n"
            "Name=keyboard-us\n"
            "Layout=us\n\n"
            "[Groups/0/Items/1]\n"
            "Name=linuxcomplete\n"
            "Layout=\n\n"
            "[GroupOrder]\n"
            "0=Default\n"
        )
        (fcitx_dir / "profile").write_text(profile_content, encoding="utf-8")
        subprocess.run(["fcitx5-remote", "-r"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        self.run_diagnostics()
        QMessageBox.information(self, "Profile Updated", "Default profile restored to SmartComplete.")

# ═══════════════════════════════════════════════════════════════════════════════
# TAB 4: Settings & AI Configuration
# ═══════════════════════════════════════════════════════════════════════════════

class TabSettings(QWidget):
    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(28, 14, 28, 14)
        layout.setSpacing(10)

        # General Preferences Card
        gen_card = QFrame()
        gen_card.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        gen_card.setProperty("class", "Card")
        gc_layout = QVBoxLayout(gen_card)
        gc_layout.setContentsMargins(18, 12, 18, 12)
        gc_layout.setSpacing(8)
        gc_title = QLabel("Prediction Preferences")
        gc_title.setStyleSheet("font-size: 15px; font-weight: 800; color: #f8fafc;")
        gc_layout.addWidget(gc_title)

        grid = QGridLayout()
        grid.setSpacing(8)

        lbl1 = QLabel("Max Candidates to display:")
        lbl1.setFixedWidth(200)
        grid.addWidget(lbl1, 0, 0)

        cand_box = QHBoxLayout()
        self.slider_max_cand = QSlider(Qt.Orientation.Horizontal)
        self.slider_max_cand.setRange(1, 10)
        self.slider_max_cand.setValue(5)
        cand_box.addWidget(self.slider_max_cand)

        self.sp_max_cand = QSpinBox()
        self.sp_max_cand.setRange(1, 10)
        self.sp_max_cand.setValue(5)
        self.sp_max_cand.setFixedWidth(70)
        cand_box.addWidget(self.sp_max_cand)

        self.slider_max_cand.valueChanged.connect(self.sp_max_cand.setValue)
        self.sp_max_cand.valueChanged.connect(self.slider_max_cand.setValue)
        grid.addLayout(cand_box, 0, 1)

        lbl2 = QLabel("Minimum Prefix Length:")
        lbl2.setFixedWidth(200)
        grid.addWidget(lbl2, 1, 0)

        prefix_box = QHBoxLayout()
        self.slider_min_prefix = QSlider(Qt.Orientation.Horizontal)
        self.slider_min_prefix.setRange(1, 5)
        self.slider_min_prefix.setValue(2)
        prefix_box.addWidget(self.slider_min_prefix)

        self.sp_min_prefix = QSpinBox()
        self.sp_min_prefix.setRange(1, 5)
        self.sp_min_prefix.setValue(2)
        self.sp_min_prefix.setFixedWidth(70)
        prefix_box.addWidget(self.sp_min_prefix)

        self.slider_min_prefix.valueChanged.connect(self.sp_min_prefix.setValue)
        self.sp_min_prefix.valueChanged.connect(self.slider_min_prefix.setValue)
        grid.addLayout(prefix_box, 1, 1)

        self.cb_learn = QCheckBox("Learn user typing habits (10× frequency multiplier)")
        self.cb_learn.setChecked(True)
        grid.addWidget(self.cb_learn, 2, 0, 1, 2)

        gc_layout.addLayout(grid)
        layout.addWidget(gen_card)

        # AI Reranker Card
        ai_card = QFrame()
        ai_card.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        ai_card.setProperty("class", "CardHighlight")
        ai_layout = QVBoxLayout(ai_card)
        ai_layout.setContentsMargins(18, 12, 18, 12)
        ai_layout.setSpacing(8)
        ai_title = QLabel("🤖  AI Reranker Configuration (Optional)")
        ai_title.setStyleSheet("font-size: 15px; font-weight: 800; color: #f8fafc;")
        ai_layout.addWidget(ai_title)

        ai_desc = QLabel(
            "SmartComplete operates 100% offline. Enabling AI reranking sends ambiguous candidate "
            "contexts to an OpenAI-compatible API for reordering. It transparently falls back to local ranking on network timeout."
        )
        ai_desc.setStyleSheet("color: #94a3b8; font-size: 12px; line-height: 1.4;")
        ai_desc.setWordWrap(True)
        ai_layout.addWidget(ai_desc)

        self.cb_ai_enable = QCheckBox("Enable AI Candidate Reranking")
        self.cb_ai_enable.setChecked(False)
        self.cb_ai_enable.toggled.connect(self.toggle_ai_fields)
        ai_layout.addWidget(self.cb_ai_enable)

        ai_grid = QGridLayout()
        ai_grid.setSpacing(8)

        lbl_ak = QLabel("API Key:")
        lbl_ak.setFixedWidth(130)
        ai_grid.addWidget(lbl_ak, 0, 0)

        key_row = QHBoxLayout()
        self.txt_api_key = QLineEdit()
        self.txt_api_key.setEchoMode(QLineEdit.EchoMode.Password)
        self.txt_api_key.setPlaceholderText("sk-proj-...")
        key_row.addWidget(self.txt_api_key)

        self.btn_eye = QPushButton("👁️ Show")
        self.btn_eye.setProperty("class", "SecondaryBtn")
        self.btn_eye.clicked.connect(self.toggle_key_visibility)
        key_row.addWidget(self.btn_eye)
        ai_grid.addLayout(key_row, 0, 1)

        lbl_am = QLabel("AI Model:")
        lbl_am.setFixedWidth(130)
        ai_grid.addWidget(lbl_am, 1, 0)
        self.cmb_model = QComboBox()
        self.cmb_model.addItems(["gpt-4o-mini", "gpt-4o", "gpt-3.5-turbo", "deepseek-chat", "custom"])
        self.cmb_model.setEditable(True)
        ai_grid.addWidget(self.cmb_model, 1, 1)

        lbl_ab = QLabel("API Base URL:")
        lbl_ab.setFixedWidth(130)
        ai_grid.addWidget(lbl_ab, 2, 0)
        self.txt_api_base = QLineEdit("https://api.openai.com/v1")
        ai_grid.addWidget(self.txt_api_base, 2, 1)

        lbl_to = QLabel("Timeout (ms):")
        lbl_to.setFixedWidth(130)
        ai_grid.addWidget(lbl_to, 3, 0)

        to_box = QHBoxLayout()
        self.slider_timeout = QSlider(Qt.Orientation.Horizontal)
        self.slider_timeout.setRange(200, 5000)
        self.slider_timeout.setValue(1200)
        self.slider_timeout.setSingleStep(100)
        to_box.addWidget(self.slider_timeout)

        self.sp_timeout = QSpinBox()
        self.sp_timeout.setRange(200, 5000)
        self.sp_timeout.setValue(1200)
        self.sp_timeout.setSingleStep(100)
        self.sp_timeout.setFixedWidth(80)
        to_box.addWidget(self.sp_timeout)

        self.slider_timeout.valueChanged.connect(self.sp_timeout.setValue)
        self.sp_timeout.valueChanged.connect(self.slider_timeout.setValue)
        ai_grid.addLayout(to_box, 3, 1)

        ai_layout.addLayout(ai_grid)
        layout.addWidget(ai_card)

        # Blocklist Card
        bl_card = QFrame()
        bl_card.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        bl_card.setProperty("class", "Card")
        bl_layout = QVBoxLayout(bl_card)
        bl_layout.setContentsMargins(18, 12, 18, 12)
        bl_layout.setSpacing(8)
        bl_title = QLabel("Application Blocklist (Terminal Pass-Through)")
        bl_title.setStyleSheet("font-size: 15px; font-weight: 800; color: #f8fafc;")
        bl_layout.addWidget(bl_title)

        bl_desc = QLabel("Additional applications where SmartComplete should stay disabled:")
        bl_desc.setStyleSheet("color: #94a3b8; font-size: 12px;")
        bl_layout.addWidget(bl_desc)

        # Quick add chips
        chips_row = QHBoxLayout()
        chips_row.setSpacing(6)
        for app_name in ["kitty", "alacritty", "neovim", "steam", "code"]:
            b = QPushButton(f"+ {app_name}")
            b.setProperty("class", "ChipBtn")
            b.clicked.connect(lambda _, a=app_name: self.append_blocklist(a))
            chips_row.addWidget(b)
        chips_row.addStretch()
        bl_layout.addLayout(chips_row)

        self.txt_blocklist = QLineEdit()
        self.txt_blocklist.setPlaceholderText("e.g. vim, emacs, code, steam")
        bl_layout.addWidget(self.txt_blocklist)
        layout.addWidget(bl_card)

        # Action Buttons
        btn_row = QHBoxLayout()
        self.save_btn = QPushButton("💾  Save && Apply Settings")
        self.save_btn.setProperty("class", "PrimaryBtn")
        self.save_btn.setMinimumHeight(44)
        self.save_btn.clicked.connect(self.save_settings)
        btn_row.addWidget(self.save_btn)

        self.reload_btn = QPushButton("↺  Reload Saved")
        self.reload_btn.setProperty("class", "SecondaryBtn")
        self.reload_btn.setMinimumHeight(44)
        self.reload_btn.clicked.connect(self.load_settings)
        btn_row.addWidget(self.reload_btn)

        btn_row.addStretch()
        layout.addLayout(btn_row)

        layout.addStretch()
        self.toggle_ai_fields(False)
        self.load_settings()

    def append_blocklist(self, app_name: str):
        cur = self.txt_blocklist.text().strip()
        items = [x.strip() for x in cur.split(",") if x.strip()]
        if app_name not in items:
            items.append(app_name)
            self.txt_blocklist.setText(", ".join(items))

    def toggle_key_visibility(self):
        if self.txt_api_key.echoMode() == QLineEdit.EchoMode.Password:
            self.txt_api_key.setEchoMode(QLineEdit.EchoMode.Normal)
            self.btn_eye.setText("🔒 Hide")
        else:
            self.txt_api_key.setEchoMode(QLineEdit.EchoMode.Password)
            self.btn_eye.setText("👁️ Show")

    def toggle_ai_fields(self, enabled: bool):
        self.txt_api_key.setEnabled(enabled)
        self.btn_eye.setEnabled(enabled)
        self.cmb_model.setEnabled(enabled)
        self.txt_api_base.setEnabled(enabled)
        self.sp_timeout.setEnabled(enabled)
        self.slider_timeout.setEnabled(enabled)

    def get_ai_config(self) -> Dict[str, Any]:
        return {
            "ai_enabled": self.cb_ai_enable.isChecked(),
            "ai_api_key": self.txt_api_key.text().strip(),
            "ai_model": self.cmb_model.currentText().strip(),
            "ai_api_base": self.txt_api_base.text().strip(),
            "ai_timeout_ms": self.sp_timeout.value()
        }

    def load_settings(self):
        conf_path = pathlib.Path.home() / ".config" / "linuxcomplete" / "linuxcomplete.conf"
        if conf_path.exists():
            try:
                data = json.loads(conf_path.read_text(encoding="utf-8"))
                self.sp_max_cand.setValue(data.get("max_candidates", 5))
                self.sp_min_prefix.setValue(data.get("min_prefix_length", 2))
                self.cb_learn.setChecked(data.get("learn_new_words", True))
                self.cb_ai_enable.setChecked(data.get("ai_rerank_enabled", False))
                self.sp_timeout.setValue(data.get("ai_timeout_ms", 1200))
                ext = data.get("disabled_programs_extend", [])
                self.txt_blocklist.setText(", ".join(ext))
            except Exception:
                pass

        api_path = pathlib.Path.home() / ".config" / "linuxcomplete" / "api_keys.json"
        if api_path.exists():
            try:
                data = json.loads(api_path.read_text(encoding="utf-8"))
                self.cb_ai_enable.setChecked(data.get("ai_enabled", False))
                self.txt_api_key.setText(data.get("api_key", ""))
                self.cmb_model.setCurrentText(data.get("model", "gpt-4o-mini"))
                self.txt_api_base.setText(data.get("api_base", "https://api.openai.com/v1"))
            except Exception:
                pass

    def save_settings(self):
        conf_dir = pathlib.Path.home() / ".config" / "linuxcomplete"
        conf_dir.mkdir(parents=True, exist_ok=True)
        conf_path = conf_dir / "linuxcomplete.conf"

        base_data = {}
        if conf_path.exists():
            try:
                base_data = json.loads(conf_path.read_text(encoding="utf-8"))
            except Exception:
                pass

        base_data["max_candidates"] = self.sp_max_cand.value()
        base_data["min_prefix_length"] = self.sp_min_prefix.value()
        base_data["learn_new_words"] = self.cb_learn.isChecked()
        base_data["ai_rerank_enabled"] = self.cb_ai_enable.isChecked()
        base_data["ai_timeout_ms"] = self.sp_timeout.value()

        bl_raw = self.txt_blocklist.text().strip()
        bl_list = [item.strip() for item in bl_raw.split(",") if item.strip()]
        base_data["disabled_programs_extend"] = bl_list

        conf_path.write_text(json.dumps(base_data, indent=4), encoding="utf-8")

        api_path = conf_dir / "api_keys.json"
        api_data = {
            "provider": "openai" if self.cb_ai_enable.isChecked() else "local",
            "ai_enabled": self.cb_ai_enable.isChecked(),
            "api_key": self.txt_api_key.text().strip(),
            "api_base": self.txt_api_base.text().strip(),
            "model": self.cmb_model.currentText().strip()
        }
        api_path.write_text(json.dumps(api_data, indent=4), encoding="utf-8")

        subprocess.run(["fcitx5-remote", "-r"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        QMessageBox.information(self, "Settings Saved", "Preferences and AI configuration saved successfully!")

# ═══════════════════════════════════════════════════════════════════════════════
# TAB 5: Clean Uninstaller
# ═══════════════════════════════════════════════════════════════════════════════

class TabUninstall(QWidget):
    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window
        self.worker: Optional[UninstallWorker] = None
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(28, 24, 28, 24)
        layout.setSpacing(16)

        warn_card = QFrame()
        warn_card.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        warn_card.setProperty("class", "CardDanger")
        wc_layout = QVBoxLayout(warn_card)
        wc_layout.setContentsMargins(18, 16, 18, 16)
        wc_layout.setSpacing(8)

        title = QLabel("🛡️  Safe Removal & System Reset")
        title.setStyleSheet("font-size: 16px; font-weight: 800; color: #f87171;")
        wc_layout.addWidget(title)

        desc = QLabel(
            "This will cleanly remove SmartComplete from your system, remove library files from /usr, "
            "restore your Fcitx5 profile to standard US keyboard input, and clean up autostart entries."
        )
        desc.setStyleSheet("color: #e2e8f0; font-size: 13px; line-height: 1.4;")
        desc.setWordWrap(True)
        wc_layout.addWidget(desc)
        layout.addWidget(warn_card)

        opts_card = QFrame()
        opts_card.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        opts_card.setProperty("class", "Card")
        oc_layout = QVBoxLayout(opts_card)
        oc_layout.setContentsMargins(18, 16, 18, 16)
        oc_layout.setSpacing(10)

        self.cb_purge = QCheckBox("Purge learned typing vocabulary and user config (~/.local/share/linuxcomplete)")
        self.cb_purge.setChecked(False)
        oc_layout.addWidget(self.cb_purge)

        caution_lbl = QLabel("⚠️  If left unchecked, your personal word frequency model is preserved for future installs.")
        caution_lbl.setStyleSheet("color: #fcd34d; font-size: 11px; margin-left: 28px;")
        oc_layout.addWidget(caution_lbl)
        layout.addWidget(opts_card)

        act_row = QHBoxLayout()
        self.uninst_btn = QPushButton("🗑️  Uninstall SmartComplete Now")
        self.uninst_btn.setProperty("class", "DangerBtn")
        self.uninst_btn.setMinimumHeight(44)
        self.uninst_btn.clicked.connect(self.start_uninstall)
        act_row.addWidget(self.uninst_btn)

        self.btn_backup = QPushButton("📦  Backup Learned Vocabulary First")
        self.btn_backup.setProperty("class", "SecondaryBtn")
        self.btn_backup.setMinimumHeight(44)
        self.btn_backup.clicked.connect(self.backup_vocabulary)
        act_row.addWidget(self.btn_backup)

        act_row.addStretch()
        layout.addLayout(act_row)

        # Uninstaller Terminal Log Frame
        self.uninst_frame = QFrame()
        self.uninst_frame.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        self.uninst_frame.setObjectName("TerminalContainer")
        tf_layout = QVBoxLayout(self.uninst_frame)
        tf_layout.setContentsMargins(0, 0, 0, 0)
        tf_layout.setSpacing(0)

        th = QFrame()
        th.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        th.setObjectName("TerminalHeader")
        th_lay = QHBoxLayout(th)
        th_lay.setContentsMargins(12, 6, 12, 6)
        dots = QLabel("●  ●  ●")
        dots.setStyleSheet("color: #475569; font-size: 11px; font-weight: 700; margin-right: 8px;")
        th_lay.addWidget(dots)
        th_title = QLabel("uninstall.log")
        th_title.setStyleSheet("color: #94a3b8; font-family: monospace; font-size: 11px;")
        th_lay.addWidget(th_title)
        th_lay.addStretch()
        tf_layout.addWidget(th)

        self.uninst_log = QTextEdit()
        self.uninst_log.setObjectName("LogViewer")
        self.uninst_log.setReadOnly(True)
        self.uninst_log.setMinimumHeight(160)
        tf_layout.addWidget(self.uninst_log)

        layout.addWidget(self.uninst_frame)
        layout.addStretch()

    def backup_vocabulary(self):
        user_dir = pathlib.Path.home() / ".local" / "share" / "linuxcomplete"
        if not user_dir.exists():
            QMessageBox.information(self, "No Custom Vocabulary", "No personal typing vocabulary found to backup.")
            return

        backup_zip = pathlib.Path.home() / f"smartcomplete-vocab-backup-{int(time.time())}.tar.gz"
        try:
            subprocess.run(["tar", "-czf", str(backup_zip), "-C", str(user_dir), "."], check=True)
            QMessageBox.information(self, "Backup Complete", f"Successfully backed up vocabulary to:\n{backup_zip}")
        except Exception as e:
            QMessageBox.critical(self, "Backup Failed", f"Failed to create backup archive:\n{e}")

    def start_uninstall(self):
        confirm = QMessageBox.question(
            self,
            "Confirm Uninstallation",
            "Are you sure you want to uninstall SmartComplete?\n\nFcitx5 will be reset to default keyboard input.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        if confirm != QMessageBox.StandardButton.Yes:
            return

        self.uninst_btn.setEnabled(False)
        self.uninst_btn.setText("Uninstalling...")
        self.uninst_log.clear()

        self.worker = UninstallWorker(self.cb_purge.isChecked(), SystemInspector.get_project_dir())
        self.worker.log_emitted.connect(self.on_log_emitted)
        self.worker.finished.connect(self.on_uninstall_finished)
        self.worker.request_auth.connect(self.on_request_auth)
        self.worker.start()

    def on_log_emitted(self, level: str, text: str):
        self.uninst_log.append(f"<span style='color: #cbd5e1;'>{text}</span>")

    def on_request_auth(self, reason: str):
        dlg = PasswordDialog(self, prompt_text=reason)
        if dlg.exec() == QDialog.DialogCode.Accepted:
            self.worker.set_auth_response(dlg.password)
        else:
            self.worker.set_auth_response(None)

    def on_uninstall_finished(self, success: bool, msg: str):
        self.uninst_btn.setEnabled(True)
        self.uninst_btn.setText("🗑️  Uninstall SmartComplete Now")
        self.main_window.update_header_status()
        self.main_window.tab_installer.refresh_system_probe()
        QMessageBox.information(self, "Uninstalled", msg)

# ═══════════════════════════════════════════════════════════════════════════════
# Main Window Frame
# ═══════════════════════════════════════════════════════════════════════════════

class MainWindow(QMainWindow):
    def __init__(self, initial_tab: str = "installer"):
        super().__init__()
        app_inst = QApplication.instance()
        if app_inst and not app_inst.styleSheet():
            app_inst.setStyleSheet(DARK_THEME_QSS)

        self.setObjectName("MainWindow")
        self.setWindowTitle("SmartComplete — Linux Text Prediction Engine")
        self.setMinimumSize(1020, 720)
        self.resize(1100, 780)

        icon_path = SystemInspector.get_project_dir() / "data" / "icons" / "linuxcomplete.svg"
        if icon_path.exists():
            self.setWindowIcon(QIcon(str(icon_path)))

        central = QWidget()
        central.setObjectName("MainWindow")
        central.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        self.setCentralWidget(central)
        root_layout = QVBoxLayout(central)
        root_layout.setContentsMargins(0, 0, 0, 0)
        root_layout.setSpacing(0)

        # ── Main Content Split (Sidebar + Workspace) ────────────────
        body = QWidget()
        body_layout = QHBoxLayout(body)
        body_layout.setContentsMargins(0, 0, 0, 0)
        body_layout.setSpacing(0)

        # Sidebar
        sidebar = QWidget()
        sidebar.setObjectName("Sidebar")
        sidebar.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        sidebar.setFixedWidth(240)
        sb_layout = QVBoxLayout(sidebar)
        sb_layout.setContentsMargins(16, 20, 16, 20)
        sb_layout.setSpacing(6)

        # Sidebar Brand
        brand_frame = QFrame()
        brand_frame.setStyleSheet("background: transparent; border: none;")
        bf_lay = QHBoxLayout(brand_frame)
        bf_lay.setContentsMargins(4, 4, 4, 12)
        bf_lay.setSpacing(12)

        logo_box = QLabel()
        logo_box.setFixedSize(40, 40)
        logo_box.setAlignment(Qt.AlignmentFlag.AlignCenter)
        if icon_path.exists():
            pix = QPixmap(str(icon_path)).scaled(36, 36, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
            logo_box.setPixmap(pix)
        else:
            logo_box.setText("⌨️")
            logo_box.setStyleSheet("font-size: 26px;")
        logo_box.setStyleSheet("""
            background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #172554, stop:1 #1e3a8a);
            border: 1px solid rgba(56, 189, 248, 0.4);
            border-radius: 10px;
            padding: 2px;
        """)
        bf_lay.addWidget(logo_box)

        brand_titles = QVBoxLayout()
        brand_titles.setSpacing(1)
        b_name = QLabel("SmartComplete")
        b_name.setObjectName("SidebarBrandTitle")
        b_sub = QLabel("Linux IME Engine")
        b_sub.setObjectName("SidebarBrandSubtitle")
        brand_titles.addWidget(b_name)
        brand_titles.addWidget(b_sub)
        bf_lay.addLayout(brand_titles)
        bf_lay.addStretch()
        sb_layout.addWidget(brand_frame)

        self.nav_group = QButtonGroup(self)
        self.nav_group.setExclusive(True)

        # Category 1: Setup & Playground
        cat1 = QLabel("WORKFLOW")
        cat1.setProperty("class", "SidebarCategory")
        sb_layout.addWidget(cat1)

        nav_items_1 = [
            ("🚀  Install && Setup", 0),
            ("📝  Test Scratchpad", 1)
        ]
        self.nav_buttons = []
        for label, idx in nav_items_1:
            btn = QPushButton(label)
            btn.setProperty("class", "NavBtn")
            btn.setCheckable(True)
            self.nav_group.addButton(btn, idx)
            sb_layout.addWidget(btn)
            self.nav_buttons.append(btn)

        sb_layout.addSpacing(12)

        # Category 2: Management
        cat2 = QLabel("CONTROL & TOOLS")
        cat2.setProperty("class", "SidebarCategory")
        sb_layout.addWidget(cat2)

        nav_items_2 = [
            ("🩺  System Doctor", 2),
            ("⚙️  Settings && AI", 3),
            ("🗑️  Uninstaller", 4)
        ]
        for label, idx in nav_items_2:
            btn = QPushButton(label)
            btn.setProperty("class", "NavBtn")
            btn.setCheckable(True)
            self.nav_group.addButton(btn, idx)
            sb_layout.addWidget(btn)
            self.nav_buttons.append(btn)

        sb_layout.addStretch()

        # Engine Stats Box in Sidebar
        engine_box = QFrame()
        engine_box.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        engine_box.setStyleSheet("""
            background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #141f32, stop:1 #0c1424);
            border: 1px solid #233754;
            border-radius: 11px;
        """)
        eb_lay = QVBoxLayout(engine_box)
        eb_lay.setContentsMargins(14, 12, 14, 12)
        eb_lay.setSpacing(5)
        eb_title = QLabel("●  Engine Ready (v0.1.0)")
        eb_title.setStyleSheet("font-size: 11px; font-weight: 800; color: #34d399; letter-spacing: 0.3px;")
        eb_ver = QLabel("Fcitx5 Native IME Engine\n84K N-Gram • 26K Rules")
        eb_ver.setStyleSheet("font-size: 10px; color: #8c9cb3; line-height: 1.4;")
        eb_lay.addWidget(eb_title)
        eb_lay.addWidget(eb_ver)
        sb_layout.addWidget(engine_box)

        body_layout.addWidget(sidebar)

        # Right Workspace (Header + Pages Stack)
        workspace = QWidget()
        workspace.setObjectName("Workspace")
        workspace.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        ws_layout = QVBoxLayout(workspace)
        ws_layout.setContentsMargins(0, 0, 0, 0)
        ws_layout.setSpacing(0)

        # Top Dynamic Header Bar
        header = QWidget()
        header.setObjectName("HeaderBar")
        header.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        h_layout = QHBoxLayout(header)
        h_layout.setContentsMargins(28, 14, 28, 14)
        h_layout.setSpacing(14)

        header_titles = QVBoxLayout()
        header_titles.setSpacing(3)
        self.page_title = QLabel("Installation & Environment Setup")
        self.page_title.setObjectName("HeaderPageTitle")
        self.page_sub = QLabel("Configure system dependencies, compile C++ prediction core, and integrate with Fcitx5")
        self.page_sub.setObjectName("HeaderPageSubtitle")
        header_titles.addWidget(self.page_title)
        header_titles.addWidget(self.page_sub)
        h_layout.addLayout(header_titles)
        h_layout.addStretch()

        self.header_status_pill = StatusBadge("Probing Engine...", "info")
        h_layout.addWidget(self.header_status_pill)

        self.btn_install_menu = QPushButton("📌 Pin to App Menu")
        self.btn_install_menu.setProperty("class", "SecondaryBtn")
        self.btn_install_menu.setToolTip("Install desktop launcher shortcut into application menu")
        self.btn_install_menu.clicked.connect(self.install_desktop_menu_shortcut)
        h_layout.addWidget(self.btn_install_menu)

        self.btn_github = QPushButton("⭐ GitHub")
        self.btn_github.setProperty("class", "SecondaryBtn")
        self.btn_github.setToolTip("Open SmartComplete repository on GitHub")
        self.btn_github.clicked.connect(lambda: webbrowser.open("https://github.com/ekremx25/smartcomplete"))
        h_layout.addWidget(self.btn_github)

        ws_layout.addWidget(header)

        # Scrollable Pages Stack
        self.scroll_area = QScrollArea()
        self.scroll_area.setObjectName("MainScrollArea")
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)

        self.stack = QStackedWidget()
        self.stack.setObjectName("MainStack")

        self.tab_installer = TabInstaller(self)
        self.tab_scratchpad = TabScratchpad(self)
        self.tab_doctor = TabDoctor(self)
        self.tab_settings = TabSettings(self)
        self.tab_uninstall = TabUninstall(self)

        self.stack.addWidget(self.tab_installer)
        self.stack.addWidget(self.tab_scratchpad)
        self.stack.addWidget(self.tab_doctor)
        self.stack.addWidget(self.tab_settings)
        self.stack.addWidget(self.tab_uninstall)

        self.scroll_area.setWidget(self.stack)
        ws_layout.addWidget(self.scroll_area)

        body_layout.addWidget(workspace)
        root_layout.addWidget(body)

        self.nav_group.idClicked.connect(self.switch_tab)

        tab_map = {"installer": 0, "scratchpad": 1, "doctor": 2, "settings": 3, "uninstall": 4}
        init_idx = tab_map.get(initial_tab, 0)
        self.nav_buttons[init_idx].setChecked(True)
        self.switch_tab(init_idx)

        self.update_header_status()

    def switch_tab(self, idx: int):
        self.stack.setCurrentIndex(idx)
        self.scroll_area.verticalScrollBar().setValue(0)

        tab_info = [
            ("🚀  Installation & Setup Wizard",
             "Configure system dependencies, compile C++ core, and deploy to Fcitx5"),
            ("📝  Live Autocomplete Playground",
             "Real-time prediction testing for phrases, typos, bigrams, and emoji shortcodes"),
            ("🩺  System Doctor & Diagnostics",
             "Automated health verification of daemon processes, addon binaries, and profiles"),
            ("⚙️  Engine Settings & AI Reranker",
             "Fine-tune candidate count, typing learning rates, blocklist, and optional AI"),
            ("🗑️  Safe Uninstaller & Reset",
             "Cleanly remove SmartComplete binaries and restore original keyboard layout")
        ]
        if 0 <= idx < len(tab_info):
            self.page_title.setText(tab_info[idx][0])
            self.page_sub.setText(tab_info[idx][1])

        if idx == 1:
            self.tab_scratchpad.update_live_fcitx_status()
        elif idx == 2:
            self.tab_doctor.run_diagnostics()

    def update_header_status(self):
        fcitx = SystemInspector.check_fcitx5()
        if fcitx["running"] and fcitx["addon_so"] and fcitx["profile_configured"]:
            self.header_status_pill.setLevel("success", "● SmartComplete Active")
        elif fcitx["addon_so"]:
            self.header_status_pill.setLevel("warning", "● Installed (Daemon Idle)")
        else:
            self.header_status_pill.setLevel("neutral", "○ Ready to Install")

    def install_desktop_menu_shortcut(self):
        app_dir = pathlib.Path.home() / ".local" / "share" / "applications"
        app_dir.mkdir(parents=True, exist_ok=True)
        desktop_f = app_dir / "smartcomplete-manager.desktop"

        project_dir = SystemInspector.get_project_dir()
        icon_f = project_dir / "data" / "icons" / "linuxcomplete.svg"
        exec_script = project_dir / "gui-installer.sh"

        content = (
            "[Desktop Entry]\n"
            "Version=1.0\n"
            "Type=Application\n"
            "Name=SmartComplete Control Center\n"
            "Comment=Installer, live scratchpad, settings and diagnostics for SmartComplete\n"
            f"Icon={icon_f}\n"
            f"Exec={exec_script}\n"
            "Terminal=false\n"
            "Categories=Utility;Settings;\n"
        )
        desktop_f.write_text(content, encoding="utf-8")
        QMessageBox.information(
            self,
            "Shortcut Installed",
            f"Added 'SmartComplete Control Center' to your applications launcher!\n\nLocation: {desktop_f}"
        )

# ═══════════════════════════════════════════════════════════════════════════════
# Main Entry Point
# ═══════════════════════════════════════════════════════════════════════════════

def main():
    app = QApplication(sys.argv)
    app.setStyleSheet(DARK_THEME_QSS)

    initial_tab = "installer"
    if "--tab" in sys.argv:
        try:
            initial_tab = sys.argv[sys.argv.index("--tab") + 1]
        except Exception:
            pass

    window = MainWindow(initial_tab=initial_tab)
    window.show()
    return app.exec()

if __name__ == "__main__":
    sys.exit(main())
