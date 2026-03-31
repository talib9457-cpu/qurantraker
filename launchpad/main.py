"""
LaunchPad - لوحة التحكم السريعة
تطبيق Windows لتجميع الأدوات والملفات والروابط في مكان واحد
"""

import sys
import os
import subprocess
import webbrowser

from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QLineEdit, QScrollArea, QFrame,
    QGridLayout, QMenu, QMessageBox, QSizePolicy, QToolButton,
    QSystemTrayIcon, QStyle
)
from PyQt6.QtCore import Qt, QSize, QTimer, pyqtSignal, QThread
from PyQt6.QtGui import (
    QFont, QColor, QIcon, QPalette, QCursor, QPixmap,
    QPainter, QBrush, QLinearGradient, QAction
)

from models import Tool, ToolType, DataManager
from dialogs import AddEditToolDialog


# ─────────────────────── Styles ────────────────────────────────────────────

MAIN_STYLE = """
QMainWindow, QWidget#centralWidget {
    background-color: #11111B;
}
QScrollArea {
    background-color: transparent;
    border: none;
}
QScrollBar:vertical {
    background-color: #1E1E2E;
    width: 8px;
    border-radius: 4px;
}
QScrollBar::handle:vertical {
    background-color: #45475A;
    border-radius: 4px;
    min-height: 20px;
}
QScrollBar::handle:vertical:hover {
    background-color: #585B70;
}
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical { height: 0; }
QScrollBar:horizontal {
    background-color: #1E1E2E;
    height: 8px;
    border-radius: 4px;
}
QScrollBar::handle:horizontal {
    background-color: #45475A;
    border-radius: 4px;
}
QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal { width: 0; }
"""

SEARCH_STYLE = """
QLineEdit {
    background-color: #1E1E2E;
    color: #CDD6F4;
    border: 1px solid #313244;
    border-radius: 12px;
    padding: 10px 16px 10px 40px;
    font-size: 14px;
    font-family: 'Segoe UI', Arial;
}
QLineEdit:focus {
    border: 1px solid #2563EB;
    background-color: #1E1E2E;
}
QLineEdit::placeholder {
    color: #585B70;
}
"""

CAT_BTN_ACTIVE = """
QPushButton {
    background-color: #2563EB;
    color: white;
    border: none;
    border-radius: 20px;
    padding: 6px 18px;
    font-size: 13px;
    font-weight: bold;
    font-family: 'Segoe UI', Arial;
}
"""

CAT_BTN_INACTIVE = """
QPushButton {
    background-color: #1E1E2E;
    color: #89B4FA;
    border: 1px solid #313244;
    border-radius: 20px;
    padding: 6px 18px;
    font-size: 13px;
    font-family: 'Segoe UI', Arial;
}
QPushButton:hover {
    background-color: #313244;
    border-color: #45475A;
}
"""

ADD_BTN_STYLE = """
QPushButton {
    background-color: #2563EB;
    color: white;
    border: none;
    border-radius: 12px;
    padding: 10px 24px;
    font-size: 14px;
    font-weight: bold;
    font-family: 'Segoe UI', Arial;
}
QPushButton:hover {
    background-color: #1D4ED8;
}
QPushButton:pressed {
    background-color: #1E40AF;
}
"""

HEADER_BTN_STYLE = """
QPushButton {
    background-color: transparent;
    color: #6C7086;
    border: none;
    border-radius: 8px;
    padding: 6px 10px;
    font-size: 18px;
}
QPushButton:hover {
    background-color: #1E1E2E;
    color: #CDD6F4;
}
"""

WINDOW_CTRL_STYLE = """
QPushButton {
    background-color: transparent;
    border: none;
    border-radius: 6px;
    padding: 4px 10px;
    font-size: 14px;
    color: #6C7086;
}
QPushButton:hover { background-color: #313244; color: #CDD6F4; }
"""

CLOSE_BTN_STYLE = """
QPushButton {
    background-color: transparent;
    border: none;
    border-radius: 6px;
    padding: 4px 10px;
    font-size: 14px;
    color: #6C7086;
}
QPushButton:hover { background-color: #DC2626; color: white; }
"""


# ─────────────────────── Tool Card Widget ──────────────────────────────────

class ToolCard(QFrame):
    launched = pyqtSignal(str)  # tool id

    def __init__(self, tool: Tool, parent=None):
        super().__init__(parent)
        self.tool = tool
        self._build()

    def _build(self):
        self.setFixedSize(160, 120)
        self.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.setObjectName("toolCard")
        self._apply_style(False)

        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.setSpacing(6)
        layout.setContentsMargins(12, 12, 12, 12)

        # Icon
        icon_label = QLabel(self.tool.get_display_icon())
        icon_label.setFont(QFont("Segoe UI Emoji", 28))
        icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        icon_label.setStyleSheet("background: transparent; border: none;")
        layout.addWidget(icon_label)

        # Name
        name_label = QLabel(self.tool.name)
        name_label.setFont(QFont("Segoe UI", 11, QFont.Weight.Bold))
        name_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        name_label.setStyleSheet(f"color: #CDD6F4; background: transparent; border: none;")
        name_label.setWordWrap(True)
        layout.addWidget(name_label)

        # Type badge
        type_colors = {
            "folder": "#16A34A", "file": "#D97706", "url": "#0891B2",
            "program": "#7C3AED", "command": "#BE185D",
        }
        badge_color = type_colors.get(self.tool.tool_type, "#374151")
        from models import TOOL_TYPE_LABELS, ToolType
        type_label = TOOL_TYPE_LABELS.get(ToolType(self.tool.tool_type), self.tool.tool_type)

        badge = QLabel(type_label)
        badge.setFont(QFont("Segoe UI", 8))
        badge.setAlignment(Qt.AlignmentFlag.AlignCenter)
        badge.setStyleSheet(f"""
            color: white;
            background-color: {badge_color};
            border-radius: 6px;
            padding: 1px 6px;
            border: none;
        """)
        layout.addWidget(badge)

    def _apply_style(self, hovered: bool):
        base_color = self.tool.color
        border = "2px solid " + base_color if hovered else "1px solid #313244"
        bg = "#1E1E2E" if not hovered else "#252535"
        self.setStyleSheet(f"""
            QFrame#toolCard {{
                background-color: {bg};
                border-radius: 14px;
                border: {border};
            }}
        """)

    def enterEvent(self, event):
        self._apply_style(True)
        super().enterEvent(event)

    def leaveEvent(self, event):
        self._apply_style(False)
        super().leaveEvent(event)

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.launched.emit(self.tool.id)
        super().mousePressEvent(event)

    def contextMenuEvent(self, event):
        menu = QMenu(self)
        menu.setStyleSheet("""
            QMenu {
                background-color: #1E1E2E;
                color: #CDD6F4;
                border: 1px solid #313244;
                border-radius: 8px;
                padding: 4px;
            }
            QMenu::item {
                padding: 8px 20px;
                border-radius: 6px;
                font-size: 13px;
            }
            QMenu::item:selected { background-color: #313244; }
        """)

        launch_action = menu.addAction("▶️  تشغيل")
        edit_action = menu.addAction("✏️  تعديل")
        menu.addSeparator()
        delete_action = menu.addAction("🗑️  حذف")

        action = menu.exec(event.globalPos())
        if action == launch_action:
            self.launched.emit(self.tool.id)
        elif action == edit_action:
            self.parent().parent().parent().parent().edit_tool(self.tool)
        elif action == delete_action:
            self.parent().parent().parent().parent().delete_tool(self.tool)


# ─────────────────────── Empty State Widget ────────────────────────────────

class EmptyState(QWidget):
    add_clicked = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.setSpacing(16)

        icon = QLabel("🚀")
        icon.setFont(QFont("Segoe UI Emoji", 56))
        icon.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(icon)

        msg = QLabel("لا توجد أدوات بعد")
        msg.setFont(QFont("Segoe UI", 18, QFont.Weight.Bold))
        msg.setStyleSheet("color: #585B70;")
        msg.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(msg)

        sub = QLabel("ابدأ بإضافة أدواتك وملفاتك وروابطك المفضلة")
        sub.setFont(QFont("Segoe UI", 13))
        sub.setStyleSheet("color: #45475A;")
        sub.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(sub)

        btn = QPushButton("➕  إضافة أول أداة")
        btn.setStyleSheet(ADD_BTN_STYLE)
        btn.setFixedSize(200, 46)
        btn.clicked.connect(self.add_clicked)
        layout.addWidget(btn, alignment=Qt.AlignmentFlag.AlignCenter)


# ─────────────────────── Tools Grid Panel ──────────────────────────────────

class ToolsPanel(QWidget):
    tool_launched = pyqtSignal(str)
    empty_add_clicked = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setStyleSheet("background: transparent;")
        self._layout = QVBoxLayout(self)
        self._layout.setContentsMargins(0, 0, 0, 0)

    def display(self, tools):
        # Clear existing
        while self._layout.count():
            item = self._layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        if not tools:
            empty = EmptyState()
            empty.add_clicked.connect(self.empty_add_clicked)
            self._layout.addWidget(empty, alignment=Qt.AlignmentFlag.AlignCenter)
            return

        grid = QGridLayout()
        grid.setSpacing(16)
        grid.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignRight)

        cols = 5
        for i, tool in enumerate(tools):
            card = ToolCard(tool)
            card.launched.connect(self.tool_launched)
            grid.addWidget(card, i // cols, i % cols)

        grid_widget = QWidget()
        grid_widget.setLayout(grid)
        grid_widget.setStyleSheet("background: transparent;")
        self._layout.addWidget(grid_widget)
        self._layout.addStretch()


# ─────────────────────── Main Window ───────────────────────────────────────

class LaunchPadWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.data_manager = DataManager()
        self.current_category = "الكل"
        self.search_query = ""
        self._drag_pos = None
        self._init_ui()
        self._refresh_tools()

    def _init_ui(self):
        self.setWindowTitle("LaunchPad")
        self.setMinimumSize(920, 620)
        self.resize(1100, 700)
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setStyleSheet(MAIN_STYLE)
        self.setLayoutDirection(Qt.LayoutDirection.RightToLeft)

        central = QWidget()
        central.setObjectName("centralWidget")
        central.setStyleSheet("""
            QWidget#centralWidget {
                background-color: #11111B;
                border-radius: 16px;
                border: 1px solid #1E1E2E;
            }
        """)
        self.setCentralWidget(central)

        root = QVBoxLayout(central)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        # ── Title Bar ──────────────────────────────────────────────────────
        title_bar = QWidget()
        title_bar.setFixedHeight(52)
        title_bar.setStyleSheet("""
            background-color: #1E1E2E;
            border-top-left-radius: 16px;
            border-top-right-radius: 16px;
            border-bottom: 1px solid #313244;
        """)
        title_bar.mousePressEvent = self._title_mouse_press
        title_bar.mouseMoveEvent = self._title_mouse_move
        title_bar.mouseReleaseEvent = self._title_mouse_release

        tb_layout = QHBoxLayout(title_bar)
        tb_layout.setContentsMargins(16, 0, 8, 0)

        # Window controls (right side for RTL)
        close_btn = QPushButton("✕")
        close_btn.setObjectName("closeBtn")
        close_btn.setStyleSheet(CLOSE_BTN_STYLE)
        close_btn.clicked.connect(self.close)

        min_btn = QPushButton("─")
        min_btn.setStyleSheet(WINDOW_CTRL_STYLE)
        min_btn.clicked.connect(self.showMinimized)

        max_btn = QPushButton("□")
        max_btn.setStyleSheet(WINDOW_CTRL_STYLE)
        max_btn.clicked.connect(self._toggle_maximize)

        tb_layout.addWidget(close_btn)
        tb_layout.addWidget(min_btn)
        tb_layout.addWidget(max_btn)

        # App title
        app_title = QLabel("🚀 LaunchPad")
        app_title.setFont(QFont("Segoe UI", 14, QFont.Weight.Bold))
        app_title.setStyleSheet("color: #CDD6F4; background: transparent;")
        tb_layout.addWidget(app_title)

        tb_layout.addStretch()

        # Stats label
        self.stats_label = QLabel("")
        self.stats_label.setFont(QFont("Segoe UI", 11))
        self.stats_label.setStyleSheet("color: #585B70; background: transparent;")
        tb_layout.addWidget(self.stats_label)

        root.addWidget(title_bar)

        # ── Body ───────────────────────────────────────────────────────────
        body = QHBoxLayout()
        body.setContentsMargins(0, 0, 0, 0)
        body.setSpacing(0)

        # ── Sidebar ────────────────────────────────────────────────────────
        sidebar = QWidget()
        sidebar.setFixedWidth(200)
        sidebar.setStyleSheet("background-color: #181825; border-left: 1px solid #1E1E2E;")
        sidebar_layout = QVBoxLayout(sidebar)
        sidebar_layout.setContentsMargins(12, 20, 12, 20)
        sidebar_layout.setSpacing(8)

        sidebar_title = QLabel("التصنيفات")
        sidebar_title.setFont(QFont("Segoe UI", 11, QFont.Weight.Bold))
        sidebar_title.setStyleSheet("color: #585B70; padding-bottom: 4px;")
        sidebar_layout.addWidget(sidebar_title)

        self.cat_buttons = {}
        self._build_category_buttons(sidebar_layout)

        sidebar_layout.addStretch()

        # Data path info
        path_label = QLabel("📂 بيانات محفوظة محلياً")
        path_label.setFont(QFont("Segoe UI", 9))
        path_label.setStyleSheet("color: #313244; padding-top: 8px;")
        path_label.setWordWrap(True)
        sidebar_layout.addWidget(path_label)

        body.addWidget(sidebar)

        # ── Main Content ───────────────────────────────────────────────────
        content = QWidget()
        content.setStyleSheet("background-color: #11111B;")
        content_layout = QVBoxLayout(content)
        content_layout.setContentsMargins(24, 20, 24, 20)
        content_layout.setSpacing(16)

        # Top bar: search + add button
        top_bar = QHBoxLayout()

        # Search
        search_wrapper = QWidget()
        search_wrapper.setStyleSheet("background: transparent;")
        sw_layout = QHBoxLayout(search_wrapper)
        sw_layout.setContentsMargins(0, 0, 0, 0)
        sw_layout.setSpacing(0)

        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("🔍  ابحث عن أي أداة...")
        self.search_input.setStyleSheet(SEARCH_STYLE)
        self.search_input.setFixedHeight(44)
        self.search_input.textChanged.connect(self._on_search)
        sw_layout.addWidget(self.search_input)
        top_bar.addWidget(search_wrapper, 1)

        top_bar.addSpacing(12)

        # Add button
        add_btn = QPushButton("➕  إضافة جديد")
        add_btn.setStyleSheet(ADD_BTN_STYLE)
        add_btn.setFixedHeight(44)
        add_btn.setMinimumWidth(140)
        add_btn.clicked.connect(self.add_tool)
        top_bar.addWidget(add_btn)

        content_layout.addLayout(top_bar)

        # Section title
        self.section_label = QLabel("الكل")
        self.section_label.setFont(QFont("Segoe UI", 16, QFont.Weight.Bold))
        self.section_label.setStyleSheet("color: #CDD6F4;")
        content_layout.addWidget(self.section_label)

        # Scroll area for tools
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll.setStyleSheet("background: transparent; border: none;")

        self.tools_panel = ToolsPanel()
        self.tools_panel.tool_launched.connect(self._launch_tool)
        self.tools_panel.empty_add_clicked.connect(self.add_tool)
        scroll.setWidget(self.tools_panel)

        content_layout.addWidget(scroll)

        body.addWidget(content)
        root.addLayout(body)

    def _build_category_buttons(self, layout):
        all_cats = ["الكل"] + self.data_manager.get_categories()
        for cat in all_cats:
            btn = QPushButton(cat)
            btn.setStyleSheet(CAT_BTN_ACTIVE if cat == self.current_category else CAT_BTN_INACTIVE)
            btn.clicked.connect(lambda checked, c=cat: self._select_category(c))
            layout.addWidget(btn)
            self.cat_buttons[cat] = btn

    def _refresh_sidebar(self):
        # Remove old buttons
        for btn in self.cat_buttons.values():
            btn.deleteLater()
        self.cat_buttons.clear()

        # Find sidebar layout
        sidebar = self.centralWidget().layout().itemAt(1).layout().itemAt(0).widget()
        sidebar_layout = sidebar.layout()

        # Remove all items except title (index 0) and stretch/path label at end
        while sidebar_layout.count() > 1:
            item = sidebar_layout.takeAt(1)
            if item.widget():
                item.widget().deleteLater()

        all_cats = ["الكل"] + self.data_manager.get_categories()
        for cat in all_cats:
            btn = QPushButton(cat)
            btn.setStyleSheet(CAT_BTN_ACTIVE if cat == self.current_category else CAT_BTN_INACTIVE)
            btn.clicked.connect(lambda checked, c=cat: self._select_category(c))
            sidebar_layout.addWidget(btn)
            self.cat_buttons[cat] = btn

        sidebar_layout.addStretch()
        path_label = QLabel("📂 بيانات محفوظة محلياً")
        path_label.setFont(QFont("Segoe UI", 9))
        path_label.setStyleSheet("color: #313244; padding-top: 8px;")
        path_label.setWordWrap(True)
        sidebar_layout.addWidget(path_label)

    def _select_category(self, category: str):
        self.current_category = category
        self.search_input.clear()
        self.search_query = ""
        for cat, btn in self.cat_buttons.items():
            btn.setStyleSheet(CAT_BTN_ACTIVE if cat == category else CAT_BTN_INACTIVE)
        self.section_label.setText(category)
        self._refresh_tools()

    def _on_search(self, text: str):
        self.search_query = text
        self._refresh_tools()

    def _refresh_tools(self):
        if self.search_query:
            tools = self.data_manager.search_tools(self.search_query)
        else:
            tools = self.data_manager.get_tools_by_category(self.current_category)

        self.tools_panel.display(tools)
        total = len(self.data_manager.app_data.tools)
        self.stats_label.setText(f"{total} أداة")

    def add_tool(self):
        dialog = AddEditToolDialog(self, data_manager=self.data_manager)
        dialog.setLayoutDirection(Qt.LayoutDirection.RightToLeft)
        if dialog.exec():
            tool = dialog.get_tool()
            self.data_manager.add_tool(tool)
            self._refresh_sidebar()
            self._select_category(tool.category)

    def edit_tool(self, tool: Tool):
        dialog = AddEditToolDialog(self, tool=tool, data_manager=self.data_manager)
        dialog.setLayoutDirection(Qt.LayoutDirection.RightToLeft)
        if dialog.exec():
            self.data_manager.update_tool(tool)
            self._refresh_sidebar()
            self._refresh_tools()

    def delete_tool(self, tool: Tool):
        reply = QMessageBox.question(
            self, "تأكيد الحذف",
            f"هل تريد حذف \"{tool.name}\"؟",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        )
        if reply == QMessageBox.StandardButton.Yes:
            self.data_manager.delete_tool(tool.id)
            self._refresh_tools()

    def _launch_tool(self, tool_id: str):
        tool = next((t for t in self.data_manager.app_data.tools if t.id == tool_id), None)
        if not tool:
            return
        try:
            t = tool.get_type()
            if t == ToolType.FOLDER:
                if sys.platform == "win32":
                    os.startfile(tool.target)
                else:
                    subprocess.Popen(["xdg-open", tool.target])
            elif t == ToolType.FILE:
                if sys.platform == "win32":
                    os.startfile(tool.target)
                else:
                    subprocess.Popen(["xdg-open", tool.target])
            elif t == ToolType.URL:
                webbrowser.open(tool.target)
            elif t == ToolType.PROGRAM:
                subprocess.Popen([tool.target], shell=True)
            elif t == ToolType.COMMAND:
                if sys.platform == "win32":
                    subprocess.Popen(
                        ["powershell", "-WindowStyle", "Hidden", "-Command", tool.target],
                        creationflags=subprocess.CREATE_NO_WINDOW
                    )
                else:
                    subprocess.Popen(["bash", "-c", tool.target])
        except Exception as e:
            QMessageBox.critical(self, "خطأ", f"تعذر تشغيل الأداة:\n{e}")

    # ── Window drag ────────────────────────────────────────────────────────
    def _title_mouse_press(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self._drag_pos = event.globalPosition().toPoint() - self.frameGeometry().topLeft()

    def _title_mouse_move(self, event):
        if self._drag_pos and event.buttons() == Qt.MouseButton.LeftButton:
            self.move(event.globalPosition().toPoint() - self._drag_pos)

    def _title_mouse_release(self, event):
        self._drag_pos = None

    def _toggle_maximize(self):
        if self.isMaximized():
            self.showNormal()
        else:
            self.showMaximized()

    def keyPressEvent(self, event):
        key = event.key()
        # Ctrl+N → add new tool
        if event.modifiers() == Qt.KeyboardModifier.ControlModifier and key == Qt.Key.Key_N:
            self.add_tool()
        # Escape → clear search
        elif key == Qt.Key.Key_Escape:
            self.search_input.clear()
        # Ctrl+F → focus search
        elif event.modifiers() == Qt.KeyboardModifier.ControlModifier and key == Qt.Key.Key_F:
            self.search_input.setFocus()
            self.search_input.selectAll()
        super().keyPressEvent(event)


# ─────────────────────── Entry Point ───────────────────────────────────────

def main():
    app = QApplication(sys.argv)
    app.setApplicationName("LaunchPad")
    app.setOrganizationName("LaunchPad")
    app.setLayoutDirection(Qt.LayoutDirection.RightToLeft)

    # Font
    font = QFont("Segoe UI", 11)
    app.setFont(font)

    window = LaunchPadWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
