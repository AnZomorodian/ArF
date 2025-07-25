import sys
import os
import json
import subprocess
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QFileDialog, QMessageBox, QScrollArea,
    QFrame, QSizePolicy, QGridLayout
)
from PyQt6.QtGui import (
    QFont, QPalette, QColor, QIcon, QPixmap, QPainter, QBrush, QLinearGradient, QCursor,
    QDrag
)
from PyQt6.QtCore import Qt, QSize, QRect, QMimeData, QPoint

CONFIG_FILE = "f1_analysis_config.json"
SESSIONS = [
    ("Free Practice 1", "🏁", "FP1"),
    ("Free Practice 2", "🏁", "FP2"),
    ("Free Practice 3", "🏁", "FP3"),
    ("Qualifying", "⏱️", "Q"),
    ("Race", "🏆", "R"),
    ("Sprint", "⭐", "S"),
    ("Sprint Qualifying", "⚡", "SQ"),
]

TOP_GRADIENT = "qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #a18cd1, stop:1 #fbc2eb);"
CARD_BG = "#23233c"
CARD_BG_HOVER = "#343457"
ACCENT_GRADIENT = "qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #a18cd1, stop:1 #fbc2eb);"
SOFT_TEXT = "#ecebff"
SUBTLE_TEXT = "#b9b8cc"
ACTIVE_TILE_BG = "#a18cd1"
TILE_BG = "#282846"
TILE_BG_HOVER = "#3c3c5c"
TILE_BORDER = "#baf0ff"
SESSION_GRADIENT = [
    "qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #a18cd1, stop:1 #fbc2eb);", # FP1
    "qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #a1c4fd, stop:1 #c2e9fb);", # FP2
    "qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #b2fefa, stop:1 #f6d365);", # FP3
    "qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #fbc2eb, stop:1 #a6c1ee);", # Q
    "qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #f7797d, stop:1 #FBD786);", # R
    "qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #a1c4fd, stop:1 #c2e9fb);", # S
    "qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #fbc2eb, stop:1 #a6c1ee);"  # SQ
]

KALAMEH_FONT = "Kalameh"
KALAMEH_FONT_PATH = "Kalameh-Regular.ttf"
if os.path.exists(KALAMEH_FONT_PATH):
    QFontDatabase = None
    try:
        from PyQt6.QtGui import QFontDatabase
        QFontDatabase.addApplicationFont(KALAMEH_FONT_PATH)
    except Exception:
        pass

def load_config():
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, "r") as f:
                return json.load(f)
        except Exception:
            pass
    return {sess[2]: [] for sess in SESSIONS}

def save_config(file_map):
    try:
        with open(CONFIG_FILE, "w") as f:
            json.dump(file_map, f)
    except Exception:
        pass

class PyIcon(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedSize(44, 44)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        rect = QRect(0, 0, 44, 44)
        grad = QLinearGradient(0, 0, 44, 44)
        grad.setColorAt(0, QColor("#a18cd1"))
        grad.setColorAt(1, QColor("#fbc2eb"))
        painter.setBrush(QBrush(grad))
        painter.setPen(QColor(TILE_BORDER))
        painter.drawRoundedRect(rect.adjusted(1, 1, -1, -1), 14, 14)
        painter.setPen(QColor("#fff"))
        font = QFont(KALAMEH_FONT, 16, QFont.Weight.Bold)
        painter.setFont(font)
        painter.drawText(rect, Qt.AlignmentFlag.AlignCenter, "Py")

class ScriptTile(QWidget):
    def __init__(self, path, run_callback, remove_callback, reorder_callback, file_list, parent=None):
        super().__init__(parent)
        self.path = path
        self.run_callback = run_callback
        self.remove_callback = remove_callback
        self.reorder_callback = reorder_callback
        self.file_list = file_list
        self.setAcceptDrops(True)
        self.setMinimumSize(260, 60)
        self.setMaximumWidth(400)
        self.setStyleSheet(f"""
            QWidget {{
                background: {TILE_BG};
                border-radius: 14px;
                border: 2px solid {TILE_BORDER};
                margin-bottom: 28px;
            }}
            QWidget[dragOver="true"] {{
                border: 2.5px dashed {ACTIVE_TILE_BG};
                background: {CARD_BG_HOVER};
            }}
            QWidget:hover {{
                background: {TILE_BG_HOVER};
                border: 2px solid {ACTIVE_TILE_BG};
                box-shadow: 0 4px 32px #a18cd155;
            }}
        """)
        self.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        layout = QHBoxLayout(self)
        layout.setContentsMargins(13, 10, 13, 10)
        layout.setSpacing(12)

        # Py icon (rounded)
        py_icon = PyIcon(self)
        layout.addWidget(py_icon, alignment=Qt.AlignmentFlag.AlignVCenter)

        # Filename (rounded bg, extra padding! Kalameh font)
        label_name = QLabel(self)
        filename = os.path.basename(path)
        label_name.setText(filename)
        label_name.setFont(QFont(KALAMEH_FONT, 15, QFont.Weight.Bold))
        label_name.setStyleSheet(f"""
            QLabel {{
                color: {SOFT_TEXT};
                background: transparent;
                border: 2px solid {TILE_BORDER};
                border-radius: 11px;
                padding: 6px 28px 6px 28px;
                font-family: "{KALAMEH_FONT}";
            }}
        """)
        label_name.setToolTip(filename)
        label_name.setWordWrap(True)
        label_name.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
        layout.addWidget(label_name)

        self.label_name = label_name
        self.dragOver = False

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self._drag_start_pos = event.pos()
        elif event.button() == Qt.MouseButton.RightButton:
            self.remove_callback(self.path)
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        if hasattr(self, '_drag_start_pos') and (event.pos() - self._drag_start_pos).manhattanLength() > QApplication.startDragDistance():
            drag = QDrag(self)
            mime = QMimeData()
            idx = self.file_list.index(self.path)
            mime.setText(str(idx))
            drag.setMimeData(mime)
            # Grab pixmap for drag image
            pixmap = self.grab()
            drag.setPixmap(pixmap)
            drag.setHotSpot(event.pos())
            drag.exec(Qt.DropAction.MoveAction)
        super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            if not hasattr(self, '_drag_start_pos') or (event.pos() - self._drag_start_pos).manhattanLength() < QApplication.startDragDistance():
                self.run_callback(self.path)
        super().mouseReleaseEvent(event)

    def dragEnterEvent(self, event):
        if event.mimeData().hasText():
            event.acceptProposedAction()
            self.setProperty("dragOver", True)
            self.setStyle(self.style())
        else:
            event.ignore()

    def dragLeaveEvent(self, event):
        self.setProperty("dragOver", False)
        self.setStyle(self.style())

    def dropEvent(self, event):
        self.setProperty("dragOver", False)
        self.setStyle(self.style())
        src_idx = int(event.mimeData().text())
        dst_idx = self.file_list.index(self.path)
        if src_idx != dst_idx:
            self.reorder_callback(src_idx, dst_idx)
        event.acceptProposedAction()

class GlassCard(QFrame):
    def __init__(self, parent=None, min_height=180, pad_v=0):
        super().__init__(parent)
        self.setStyleSheet(f"""
            QFrame {{
                background: {CARD_BG};
                border-radius: 18px;
                box-shadow: 0 4px 32px #15152488;
                padding-top: {pad_v}px;
                padding-bottom: {pad_v}px;
            }}
        """)
        self.setMinimumHeight(min_height)

class SessionCard(GlassCard):
    def __init__(self, name, icon, idx, key, get_files, add_files, run_code, remove_file, handle_drop, reorder_files):
        super().__init__()
        self.setAcceptDrops(True)
        self.handle_drop = handle_drop
        self.name = name
        self.icon = icon
        self.get_files = get_files
        self.add_files = add_files
        self.run_code = run_code
        self.remove_file = remove_file
        self.idx = idx
        self.reorder_files = reorder_files
        self.key = key

        content = QVBoxLayout()
        # Header row
        head = QHBoxLayout()
        icon_label = QLabel(self.icon)
        # Larger emoji font
        icon_label.setStyleSheet(f"font-size: 2.4em; font-family: '{KALAMEH_FONT}'; margin-right: 6px;")
        head.addWidget(icon_label)
        # Session name in larger, bold Kalameh font
        title = QLabel(self.name)
        title.setFont(QFont(KALAMEH_FONT, 20, QFont.Weight.Bold))
        title.setStyleSheet(f"""
            font-size: 1.47em;
            font-weight: bold;
            color: {SOFT_TEXT};
            margin-right: 10px;
            font-family: "{KALAMEH_FONT}";
        """)
        head.addWidget(title)
        # Short session code tag (FP1, Q, etc.)
        code = QLabel(self.key)
        code.setFont(QFont(KALAMEH_FONT, 15, QFont.Weight.Medium))
        code.setStyleSheet(f"""
            font-size: 1.13em;
            color: {SUBTLE_TEXT};
            margin-left: 0.7em;
            font-family: "{KALAMEH_FONT}";
        """)
        head.addWidget(code)
        head.addStretch(1)
        add_btn = QPushButton("＋ Add Files")
        add_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        add_btn.setStyleSheet(f"""
            QPushButton {{
                background: {SESSION_GRADIENT[idx]};
                color: #23233c;
                border-radius: 8px;
                padding: 4px 14px;
                font-weight: 600;
                font-family: "{KALAMEH_FONT}";
            }}
            QPushButton:hover {{
                background: {ACCENT_GRADIENT};
                color: #23233c;
            }}
        """)
        add_btn.setFont(QFont(KALAMEH_FONT, 13, QFont.Weight.Bold))
        add_btn.clicked.connect(lambda: self.add_files(self.key))
        head.addWidget(add_btn)
        content.addLayout(head)
        # Tiles grid
        self.grid = QGridLayout()
        self.grid.setHorizontalSpacing(36)
        self.grid.setVerticalSpacing(44)
        self.grid.setContentsMargins(24, 24, 24, 24)
        content.addLayout(self.grid)
        self.setLayout(content)
        self.refresh_tiles()

    def refresh_tiles(self):
        while self.grid.count():
            item = self.grid.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()
        files = self.get_files(self.key)
        cols = 5
        for idx, f in enumerate(files):
            tile = ScriptTile(
                f,
                run_callback=self.run_code,
                remove_callback=lambda p, n=self.key: self.remove_file(n, p),
                reorder_callback=self.reorder_files,
                file_list=files,
                parent=self
            )
            row, col = divmod(idx, cols)
            self.grid.addWidget(tile, row, col, alignment=Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignTop)

    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls() or event.mimeData().hasText():
            event.acceptProposedAction()

    def dropEvent(self, event):
        files = []
        if event.mimeData().hasUrls():
            files = [u.toLocalFile() for u in event.mimeData().urls() if u.toLocalFile().endswith(".py")]
        if files:
            self.handle_drop(self.key, files)

class OutputDialog(QMessageBox):
    def __init__(self, filename, out, err, full_path):
        super().__init__()
        self.setWindowTitle(f"Output: {filename}")
        self.setIcon(QMessageBox.Icon.Information)
        style = f"""
        <style>
        pre {{
            background: {CARD_BG};
            color: {SOFT_TEXT};
            font-size: 1em;
            padding: 8px;
            border-radius: 6px;
            font-family: 'Fira Mono', 'Consolas', monospace;
        }}
        .stderr {{
            color: #f7797d;
        }}
        </style>
        """
        html = f"""{style}
        <b>STDOUT:</b>
        <pre>{out if out.strip() else "(none)"}</pre>
        <b class='stderr'>STDERR:</b>
        <pre class='stderr'>{err if err.strip() else "(none)"}</pre>
        <div style="font-size:0.9em;color:{SUBTLE_TEXT};">{full_path}</div>
        """
        self.setTextFormat(Qt.TextFormat.RichText)
        self.setText(html)
        self.setStandardButtons(QMessageBox.StandardButton.Ok)

class TopBar(QFrame):
    def __init__(self):
        super().__init__()
        self.setFixedHeight(64)
        self.setStyleSheet(f"""
            QFrame {{
                background: {TOP_GRADIENT};
                border-bottom-left-radius: 24px;
                border-bottom-right-radius: 24px;
            }}
        """)
        layout = QHBoxLayout()
        layout.setContentsMargins(28, 10, 28, 10)
        icon = QLabel("🏎️")
        icon.setFont(QFont(KALAMEH_FONT, 25, QFont.Weight.Bold))
        icon.setStyleSheet("font-size: 2.2em; font-family: '{}';".format(KALAMEH_FONT))
        layout.addWidget(icon, alignment=Qt.AlignmentFlag.AlignVCenter)
        title = QLabel("<b>Amir Formula</b>")
        title.setFont(QFont(KALAMEH_FONT, 25, QFont.Weight.Bold))
        title.setStyleSheet(f"font-size: 1.7em; color: {SOFT_TEXT}; font-weight: bold; font-family: '{KALAMEH_FONT}';")
        layout.addWidget(title)
        layout.addStretch(1)
        user = QLabel("AMYV7418")
        user.setFont(QFont(KALAMEH_FONT, 15, QFont.Weight.Bold))
        user.setStyleSheet(f"font-size: 1.08em; color: {SOFT_TEXT}; font-weight: bold; margin-right: 18px; font-family: '{KALAMEH_FONT}';")
        layout.addWidget(user)
        avatar = QLabel()
        avatar.setPixmap(QPixmap(32, 32))
        avatar.setFixedSize(32, 32)
        avatar.setStyleSheet("border-radius: 16px; background: #fff2;")
        layout.addWidget(avatar)
        self.setLayout(layout)

class F1AnalysisApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("F1 Analysis")
        self.setWindowIcon(QIcon())
        self.setMinimumSize(1300, 750)
        self.file_map = load_config()
        self.groups = {}

        # Modern palette
        pal = QPalette()
        pal.setColor(QPalette.ColorRole.Window, QColor("#202036"))
        pal.setColor(QPalette.ColorRole.WindowText, QColor(SOFT_TEXT))
        self.setPalette(pal)
        self.setStyleSheet(f"""
            QMainWindow {{ background: #202036; }}
            QLabel, QTextEdit {{ color: {SOFT_TEXT}; font-size: 1.05em; font-family: '{KALAMEH_FONT}'; }}
            QScrollArea {{ border: none; background: transparent; }}
        """)

        main_layout = QVBoxLayout()
        main_layout.setSpacing(12)
        main_layout.setContentsMargins(0, 0, 0, 0)

        main_layout.addWidget(TopBar())

        # Info block -- reduce height & font
        info_card = GlassCard(min_height=30, pad_v=0)
        info_layout = QHBoxLayout()
        info_card.setLayout(info_layout)
        hello = QLabel("Hello, AMYV7418! Welcome to F1 Analysis. Select or drag-and-drop Python scripts for each session. Click a tile to execute. Right-click to delete. Drag tiles to reorder.")
        hello.setFont(QFont(KALAMEH_FONT, 13))
        hello.setStyleSheet(f"font-size: 1.07em; color: {SOFT_TEXT}; margin: 0px; padding: 0px; font-family: '{KALAMEH_FONT}';")
        info_layout.setContentsMargins(6, 1, 6, 1)
        info_layout.addWidget(hello)
        info_layout.addStretch(1)
        main_layout.addWidget(info_card)

        # Scrollable session cards
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_content = QWidget()
        session_layout = QVBoxLayout(scroll_content)
        session_layout.setSpacing(18)
        session_layout.setContentsMargins(20, 10, 20, 10)

        # Cards for each session
        for idx, (name, icon, key) in enumerate(SESSIONS):
            group = SessionCard(
                name=name,
                icon=icon,
                idx=idx,
                key=key,
                get_files=lambda n, m=self.file_map: m[n],
                add_files=self.add_files,
                run_code=self.run_code,
                remove_file=self.remove_file,
                handle_drop=self.handle_drop,
                reorder_files=lambda src, dst, n=key: self.reorder_files(n, src, dst)
            )
            self.groups[key] = group
            session_layout.addWidget(group)

        session_layout.addStretch(1)
        scroll_area.setWidget(scroll_content)
        main_layout.addWidget(scroll_area)

        # Footer -- reduce height & font
        footer_card = GlassCard(min_height=35, pad_v=0)
        footer_layout = QHBoxLayout()
        footer_card.setLayout(footer_layout)
        footer = QLabel("Amir Formula • Inspired by modern smart home dashboards • Powered by Python")
        footer.setFont(QFont(KALAMEH_FONT, 13))
        footer.setStyleSheet(f"color: {SUBTLE_TEXT}; font-size: 0.98em; margin: 0px; padding: 0px; font-family: '{KALAMEH_FONT}';")
        footer_layout.setContentsMargins(0, 0, 0, 0)
        footer_layout.addWidget(footer, alignment=Qt.AlignmentFlag.AlignCenter)
        main_layout.addWidget(footer_card, alignment=Qt.AlignmentFlag.AlignCenter)

        container = QWidget()
        container.setLayout(main_layout)
        self.setCentralWidget(container)

    def add_files(self, session):
        files, _ = QFileDialog.getOpenFileNames(self, f"Select Python files for {session}", "",
                                                "Python Files (*.py);;All Files (*)")
        if files:
            for file in files:
                if file not in self.file_map[session]:
                    self.file_map[session].append(file)
            save_config(self.file_map)
            self.groups[session].refresh_tiles()

    def remove_file(self, session, file):
        if file in self.file_map[session]:
            self.file_map[session].remove(file)
            save_config(self.file_map)
            self.groups[session].refresh_tiles()

    def run_code(self, file_path):
        if not os.path.exists(file_path):
            QMessageBox.critical(self, "File not found", f"{file_path} does not exist.")
            return
        try:
            result = subprocess.run([sys.executable, file_path], capture_output=True, text=True)
            out = result.stdout
            err = result.stderr
            dlg = OutputDialog(os.path.basename(file_path), out, err, file_path)
            dlg.exec()
        except Exception as e:
            QMessageBox.critical(self, "Execution Error", str(e))

    def handle_drop(self, session, files):
        changed = False
        for f in files:
            if f.endswith(".py") and f not in self.file_map[session]:
                self.file_map[session].append(f)
                changed = True
        if changed:
            save_config(self.file_map)
            self.groups[session].refresh_tiles()

    def reorder_files(self, session, src_idx, dst_idx):
        if src_idx == dst_idx:
            return
        files = self.file_map[session]
        file = files.pop(src_idx)
        files.insert(dst_idx, file)
        save_config(self.file_map)
        self.groups[session].refresh_tiles()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    win = F1AnalysisApp()
    win.show()
    sys.exit(app.exec())