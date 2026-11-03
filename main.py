import sys
from pathlib import Path
from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QListWidget, QStackedWidget, QFrame, QTableWidget,
    QTableWidgetItem, QMessageBox, QTextEdit, QComboBox, QLineEdit,
    QFormLayout, QGroupBox
)
from scanner import scan_system, scan_skyrim
from settings import load_settings, save_settings

APP_NAME = "AI Mod Analyzer"
APP_VERSION = "0.1.0"

STYLE = """
QMainWindow, QWidget { background: #171a21; color: #e7eaf0; font-family: Segoe UI; font-size: 10pt; }
QFrame#Sidebar { background: #11141a; border: none; }
QLabel#Brand { font-size: 17pt; font-weight: 700; color: #ffffff; padding: 8px 2px 18px 2px; }
QLabel#PageTitle { font-size: 21pt; font-weight: 650; color: #ffffff; }
QLabel#Muted { color: #9ba5b5; }
QPushButton { background: #282e39; border: 1px solid #3a4352; border-radius: 7px; padding: 9px 13px; }
QPushButton:hover { background: #343d4b; }
QPushButton:checked { background: #315b91; border-color: #4b83c4; }
QListWidget { background: transparent; border: none; outline: none; }
QListWidget::item { padding: 12px; border-radius: 7px; margin: 2px 0; }
QListWidget::item:selected { background: #263b55; }
QFrame#Panel, QGroupBox { background: #202630; border: 1px solid #303a49; border-radius: 10px; }
QGroupBox { margin-top: 12px; padding: 12px; font-weight: 600; }
QGroupBox::title { subcontrol-origin: margin; left: 12px; padding: 0 5px; }
QTableWidget { background: #202630; alternate-background-color: #252d39; gridline-color: #364050; border: 1px solid #303a49; border-radius: 8px; }
QHeaderView::section { background: #293240; padding: 8px; border: none; }
QTextEdit, QLineEdit, QComboBox { background: #202630; border: 1px solid #3a4352; border-radius: 7px; padding: 8px; }
"""

def panel(title, value, note=""):
    box = QFrame()
    box.setObjectName("Panel")
    lay = QVBoxLayout(box)
    t = QLabel(title); t.setObjectName("Muted")
    v = QLabel(value); v.setStyleSheet("font-size: 20pt; font-weight: 700;")
    lay.addWidget(t); lay.addWidget(v)
    if note:
        n = QLabel(note); n.setObjectName("Muted"); lay.addWidget(n)
    return box

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle(f"{APP_NAME} {APP_VERSION}")
        self.resize(1120, 740)
        self.settings = load_settings()
        self.system_scan = scan_system()
        self.game_scan = scan_skyrim()
        self._build_ui()
        self.refresh_dashboard()

    def _build_ui(self):
        base = QWidget()
        outer = QHBoxLayout(base); outer.setContentsMargins(0,0,0,0); outer.setSpacing(0)
        sidebar = QFrame(); sidebar.setObjectName("Sidebar"); sidebar.setFixedWidth(220)
        sl = QVBoxLayout(sidebar); sl.setContentsMargins(16,18,16,16)
        brand = QLabel("AI MOD ANALYZER"); brand.setObjectName("Brand"); sl.addWidget(brand)
        self.nav = QListWidget()
        for name in ["Dashboard", "Scanner", "Troubleshooter", "Settings"]:
            self.nav.addItem(name)
        self.nav.setCurrentRow(0)
        sl.addWidget(self.nav); sl.addStretch()
        foot = QLabel("Version 0.1.0\nRead-only preview")
        foot.setObjectName("Muted"); sl.addWidget(foot)
        self.pages = QStackedWidget()
        self.pages.addWidget(self.dashboard_page())
        self.pages.addWidget(self.scanner_page())
        self.pages.addWidget(self.troubleshooter_page())
        self.pages.addWidget(self.settings_page())
        outer.addWidget(sidebar); outer.addWidget(self.pages, 1)
        self.setCentralWidget(base)
        self.nav.currentRowChanged.connect(self.pages.setCurrentIndex)

    def heading(self, title, subtitle):
        w = QWidget(); l = QVBoxLayout(w); l.setContentsMargins(0,0,0,12)
        t = QLabel(title); t.setObjectName("PageTitle")
        s = QLabel(subtitle); s.setObjectName("Muted")
        l.addWidget(t); l.addWidget(s)
        return w

    def dashboard_page(self):
        page = QWidget(); l = QVBoxLayout(page); l.setContentsMargins(28,26,28,24)
        l.addWidget(self.heading("Dashboard", "Your Skyrim modding environment at a glance."))
        row = QHBoxLayout()
        self.game_card = panel("GAME DETECTION", "Checking…", "Skyrim Special Edition / Anniversary Edition")
        self.manager_card = panel("MOD MANAGERS", "Checking…", "Vortex and Mod Organizer 2")
        self.plugin_card = panel("ACTIVE PLUGINS", "—", "From the active Skyrim profile")
        row.addWidget(self.game_card); row.addWidget(self.manager_card); row.addWidget(self.plugin_card)
        l.addLayout(row)
        group = QGroupBox("Environment summary"); gl = QVBoxLayout(group)
        self.summary = QLabel("Scanning…"); self.summary.setWordWrap(True)
        gl.addWidget(self.summary); l.addWidget(group)
        actions = QHBoxLayout()
        scan_btn = QPushButton("Run read-only scan"); scan_btn.clicked.connect(self.run_scan)
        actions.addWidget(scan_btn); actions.addStretch()
        l.addLayout(actions); l.addStretch()
        return page

    def scanner_page(self):
        page = QWidget(); l = QVBoxLayout(page); l.setContentsMargins(28,26,28,24)
        l.addWidget(self.heading("Scanner", "Initial inventory of detected game files and plugin configuration."))
        self.scan_status = QLabel("Run a scan to populate this view."); self.scan_status.setObjectName("Muted")
        l.addWidget(self.scan_status)
        self.table = QTableWidget(0, 3)
        self.table.setHorizontalHeaderLabels(["Item", "Status", "Details"])
        self.table.horizontalHeader().setStretchLastSection(True)
        self.table.setAlternatingRowColors(True)
        l.addWidget(self.table, 1)
        btn = QPushButton("Scan now"); btn.clicked.connect(self.run_scan); l.addWidget(btn, 0, Qt.AlignLeft)
        return page

    def troubleshooter_page(self):
        page = QWidget(); l = QVBoxLayout(page); l.setContentsMargins(28,26,28,24)
        l.addWidget(self.heading("Troubleshooter", "Describe an issue. Version 0.1 records the report; diagnostic reasoning is coming in a later milestone."))
        form = QFormLayout()
        self.symptom = QTextEdit(); self.symptom.setPlaceholderText("Describe exactly what happens, what you expected, and when it started…")
        self.symptom.setMinimumHeight(150)
        self.frequency = QComboBox(); self.frequency.addItems(["Every time", "Frequently", "Occasionally", "Once"])
        self.changed = QComboBox(); self.changed.addItems(["Yes", "No", "Not sure"])
        self.crashlog = QComboBox(); self.crashlog.addItems(["No crash log", "I have a crash log", "Not sure"])
        form.addRow("What is happening?", self.symptom)
        form.addRow("How often?", self.frequency)
        form.addRow("Recent mod changes?", self.changed)
        form.addRow("Crash log?", self.crashlog)
        l.addLayout(form)
        self.trouble_result = QLabel("Your report stays on this screen for now. Nothing is uploaded or changed.")
        self.trouble_result.setWordWrap(True); self.trouble_result.setObjectName("Muted")
        save = QPushButton("Prepare diagnostic report"); save.clicked.connect(self.prepare_report)
        l.addWidget(save, 0, Qt.AlignLeft); l.addWidget(self.trouble_result); l.addStretch()
        return page

    def settings_page(self):
        page = QWidget(); l = QVBoxLayout(page); l.setContentsMargins(28,26,28,24)
        l.addWidget(self.heading("Settings", "Choose the intended AI mode. AI providers are not connected in this foundation build."))
        group = QGroupBox("AI configuration"); form = QFormLayout(group)
        self.ai_mode = QComboBox(); self.ai_mode.addItems(["Hybrid (local + cloud)", "Local only", "Cloud only", "Disabled for now"])
        self.ai_mode.setCurrentIndex({"hybrid":0,"local":1,"cloud":2,"disabled":3}.get(self.settings.get("ai_mode","hybrid"),0))
        self.cloud_key = QLineEdit(); self.cloud_key.setEchoMode(QLineEdit.Password)
        self.cloud_key.setPlaceholderText("Not needed yet — cloud integration is not implemented")
        self.cloud_key.setEnabled(False)
        form.addRow("Preferred mode", self.ai_mode); form.addRow("Cloud API key", self.cloud_key)
        l.addWidget(group)
        privacy = QLabel("Privacy: version 0.1 performs local read-only detection. It does not send mod lists, file paths, logs, or other data to an AI service.")
        privacy.setWordWrap(True); privacy.setObjectName("Muted"); l.addWidget(privacy)
        save = QPushButton("Save settings"); save.clicked.connect(self.save_app_settings); l.addWidget(save, 0, Qt.AlignLeft)
        l.addStretch()
        return page

    def refresh_dashboard(self):
        game = self.game_scan
        game_name = "Found" if game.get("found") else "Not found"
        self._set_card(self.game_card, game_name, game.get("path") or "Install path not detected")
        managers = [m for m in self.system_scan["managers"] if m["found"]]
        self._set_card(self.manager_card, str(len(managers)), ", ".join(m["name"] for m in managers) or "No manager detected")
        plugins = game.get("plugins", [])
        self._set_card(self.plugin_card, str(len(plugins)), "Enabled entries in plugins.txt" if plugins else "No active plugin list detected")
        lines = [
            f"Windows: {self.system_scan.get('windows', 'Unknown')}",
            f"Skyrim: {game.get('path') or 'Not detected'}",
            f"Vortex: {self._manager_path('Vortex')}",
            f"Mod Organizer 2: {self._manager_path('Mod Organizer 2')}",
            f"Plugin list: {game.get('plugins_file') or 'Not found'}",
            "All checks are read-only. Detection can be incomplete for portable/custom installations."
        ]
        self.summary.setText("\n".join(lines))

    def _manager_path(self, name):
        for m in self.system_scan["managers"]:
            if m["name"] == name and m["found"]:
                return m["path"]
        return "Not detected"

    def _set_card(self, card, value, note):
        labels = card.findChildren(QLabel)
        if len(labels) >= 2:
            labels[1].setText(value)
        if len(labels) >= 3:
            labels[2].setText(note)

    def run_scan(self):
        self.system_scan = scan_system()
        self.game_scan = scan_skyrim()
        self.refresh_dashboard()
        rows = []
        rows.append(("Skyrim installation", "Found" if self.game_scan.get("found") else "Not found", self.game_scan.get("path") or "Could not locate"))
        rows.append(("Data directory", "Found" if self.game_scan.get("data_path") else "Not found", self.game_scan.get("data_path") or "—"))
        rows.append(("plugins.txt", "Found" if self.game_scan.get("plugins_file") else "Not found", self.game_scan.get("plugins_file") or "—"))
        rows.append(("loadorder.txt", "Found" if self.game_scan.get("loadorder_file") else "Not found", self.game_scan.get("loadorder_file") or "—"))
        rows.append(("Enabled plugins", str(len(self.game_scan.get("plugins", []))), "Entries read from plugins.txt"))
        rows.append(("Data files", str(self.game_scan.get("data_file_count", 0)), "Recursive file count; no file contents modified"))
        for m in self.system_scan["managers"]:
            rows.append((m["name"], "Found" if m["found"] else "Not found", m.get("path") or "—"))
        self.table.setRowCount(len(rows))
        for r, row in enumerate(rows):
            for c, value in enumerate(row):
                self.table.setItem(r, c, QTableWidgetItem(str(value)))
        self.scan_status.setText("Scan complete. This is an initial inventory, not yet a compatibility or conflict analysis.")

    def prepare_report(self):
        if not self.symptom.toPlainText().strip():
            QMessageBox.information(self, "Missing description", "Please describe the issue first.")
            return
        report = (
            "Diagnostic intake captured locally (not uploaded).\n"
            f"Frequency: {self.frequency.currentText()}\n"
            f"Recent mod changes: {self.changed.currentText()}\n"
            f"Crash log: {self.crashlog.currentText()}\n"
            f"Symptom: {self.symptom.toPlainText().strip()}"
        )
        self.trouble_result.setText(report)

    def save_app_settings(self):
        self.settings["ai_mode"] = ["hybrid","local","cloud","disabled"][self.ai_mode.currentIndex()]
        save_settings(self.settings)
        QMessageBox.information(self, "Settings saved", "Your preference was saved locally. AI providers are not connected in v0.1.")

def main():
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    app.setStyleSheet(STYLE)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
