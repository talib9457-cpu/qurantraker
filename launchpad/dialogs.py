"""
LaunchPad - Dialogs
نوافذ الحوار لإضافة وتعديل الأدوات
"""

import uuid
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QComboBox, QTextEdit, QPushButton, QColorDialog,
    QFileDialog, QFrame, QMessageBox, QGridLayout, QWidget
)
from PyQt6.QtCore import Qt, QSize
from PyQt6.QtGui import QColor, QFont, QIcon

from models import Tool, ToolType, TOOL_TYPE_LABELS, DataManager


DARK_DIALOG_STYLE = """
QDialog {
    background-color: #1E1E2E;
    color: #CDD6F4;
    font-family: 'Segoe UI', Arial;
}
QLabel {
    color: #CDD6F4;
    font-size: 13px;
    font-weight: bold;
}
QLineEdit, QTextEdit, QComboBox {
    background-color: #313244;
    color: #CDD6F4;
    border: 1px solid #45475A;
    border-radius: 8px;
    padding: 8px 12px;
    font-size: 13px;
    selection-background-color: #2563EB;
}
QLineEdit:focus, QTextEdit:focus, QComboBox:focus {
    border: 1px solid #2563EB;
}
QComboBox::drop-down {
    border: none;
    width: 24px;
}
QComboBox::down-arrow {
    image: none;
    border-left: 5px solid transparent;
    border-right: 5px solid transparent;
    border-top: 6px solid #CDD6F4;
    margin-right: 6px;
}
QComboBox QAbstractItemView {
    background-color: #313244;
    color: #CDD6F4;
    border: 1px solid #45475A;
    selection-background-color: #2563EB;
    outline: none;
}
QPushButton {
    border-radius: 8px;
    padding: 10px 20px;
    font-size: 13px;
    font-weight: bold;
}
QPushButton#saveBtn {
    background-color: #2563EB;
    color: white;
    border: none;
}
QPushButton#saveBtn:hover {
    background-color: #1D4ED8;
}
QPushButton#cancelBtn {
    background-color: #313244;
    color: #CDD6F4;
    border: 1px solid #45475A;
}
QPushButton#cancelBtn:hover {
    background-color: #45475A;
}
QPushButton#browseBtn {
    background-color: #374151;
    color: #CDD6F4;
    border: 1px solid #4B5563;
    padding: 8px 14px;
    min-width: 70px;
}
QPushButton#browseBtn:hover {
    background-color: #4B5563;
}
QPushButton#colorBtn {
    border-radius: 8px;
    border: 2px solid #45475A;
    min-width: 40px;
    max-width: 40px;
    min-height: 36px;
    max-height: 36px;
}
QFrame#separator {
    background-color: #45475A;
    max-height: 1px;
}
"""

ICON_EMOJI_LIST = [
    "📁", "📄", "🌐", "⚙️", "💻", "🔧", "🗂️", "📊", "📈", "🗃️",
    "🖥️", "🖨️", "📧", "📱", "🔑", "🔒", "🔓", "📌", "📍", "⭐",
    "🚀", "🎯", "💡", "🔔", "📝", "🗒️", "📋", "🗓️", "⏰", "🔍",
    "📦", "🏠", "🏢", "📺", "🎮", "🎵", "🎬", "🖼️", "📷", "🗄️",
]


class AddEditToolDialog(QDialog):
    def __init__(self, parent=None, tool: Tool = None, data_manager: DataManager = None):
        super().__init__(parent)
        self.tool = tool
        self.data_manager = data_manager
        self.selected_color = tool.color if tool else "#2563EB"
        self.selected_icon = tool.icon if tool else ""
        self._init_ui()
        if tool:
            self._populate_fields(tool)

    def _init_ui(self):
        is_edit = self.tool is not None
        self.setWindowTitle("تعديل أداة" if is_edit else "إضافة أداة جديدة")
        self.setMinimumWidth(520)
        self.setLayoutDirection(Qt.LayoutDirection.RightToLeft)
        self.setStyleSheet(DARK_DIALOG_STYLE)

        layout = QVBoxLayout(self)
        layout.setSpacing(16)
        layout.setContentsMargins(24, 24, 24, 24)

        # Title
        title = QLabel("تعديل أداة" if is_edit else "➕ إضافة أداة جديدة")
        title.setFont(QFont("Segoe UI", 16, QFont.Weight.Bold))
        title.setStyleSheet("color: #CDD6F4; margin-bottom: 8px;")
        layout.addWidget(title)

        sep = QFrame()
        sep.setObjectName("separator")
        sep.setFrameShape(QFrame.Shape.HLine)
        layout.addWidget(sep)

        grid = QGridLayout()
        grid.setSpacing(12)
        grid.setColumnStretch(1, 1)

        # Tool Name
        grid.addWidget(QLabel("اسم الأداة *"), 0, 0)
        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("مثال: قاعدة البيانات، مجلد المشاريع...")
        grid.addWidget(self.name_input, 0, 1)

        # Tool Type
        grid.addWidget(QLabel("نوع الأداة *"), 1, 0)
        self.type_combo = QComboBox()
        for t in ToolType:
            self.type_combo.addItem(
                f"{TOOL_TYPE_LABELS[t]}",
                t.value
            )
        self.type_combo.currentIndexChanged.connect(self._on_type_changed)
        grid.addWidget(self.type_combo, 1, 1)

        # Target / Path
        grid.addWidget(QLabel("المسار / الرابط *"), 2, 0)
        target_row = QHBoxLayout()
        self.target_input = QLineEdit()
        self.target_input.setPlaceholderText("أدخل المسار أو الرابط أو الأمر...")
        target_row.addWidget(self.target_input)
        self.browse_btn = QPushButton("استعرض")
        self.browse_btn.setObjectName("browseBtn")
        self.browse_btn.clicked.connect(self._browse_target)
        target_row.addWidget(self.browse_btn)
        target_widget = QWidget()
        target_widget.setLayout(target_row)
        target_widget.setStyleSheet("background: transparent;")
        grid.addWidget(target_widget, 2, 1)

        # Category
        grid.addWidget(QLabel("التصنيف"), 3, 0)
        self.category_combo = QComboBox()
        self.category_combo.setEditable(True)
        if self.data_manager:
            for cat in self.data_manager.get_categories():
                self.category_combo.addItem(cat)
        grid.addWidget(self.category_combo, 3, 1)

        # Description
        grid.addWidget(QLabel("الوصف"), 4, 0)
        self.desc_input = QTextEdit()
        self.desc_input.setPlaceholderText("وصف اختياري للأداة...")
        self.desc_input.setMaximumHeight(70)
        grid.addWidget(self.desc_input, 4, 1)

        # Icon + Color row
        grid.addWidget(QLabel("الأيقونة"), 5, 0)
        icon_row = QHBoxLayout()
        self.icon_input = QLineEdit()
        self.icon_input.setPlaceholderText("رمز تعبيري مثل: 📁 🔧 ⚙️")
        self.icon_input.setMaximumWidth(120)
        icon_row.addWidget(self.icon_input)

        # Quick emoji picker
        for emoji in ICON_EMOJI_LIST[:8]:
            btn = QPushButton(emoji)
            btn.setFixedSize(32, 32)
            btn.setStyleSheet("""
                QPushButton {
                    background-color: #313244;
                    border: 1px solid #45475A;
                    border-radius: 6px;
                    font-size: 16px;
                    padding: 0;
                }
                QPushButton:hover { background-color: #45475A; }
            """)
            btn.clicked.connect(lambda checked, e=emoji: self._set_icon(e))
            icon_row.addWidget(btn)

        icon_row.addStretch()
        icon_widget = QWidget()
        icon_widget.setLayout(icon_row)
        icon_widget.setStyleSheet("background: transparent;")
        grid.addWidget(icon_widget, 5, 1)

        # Color
        grid.addWidget(QLabel("اللون"), 6, 0)
        color_row = QHBoxLayout()
        self.color_btn = QPushButton()
        self.color_btn.setObjectName("colorBtn")
        self._update_color_btn()
        self.color_btn.clicked.connect(self._pick_color)
        color_row.addWidget(self.color_btn)

        self.color_label = QLabel(self.selected_color)
        self.color_label.setStyleSheet("color: #89B4FA; font-size: 12px; font-weight: normal;")
        color_row.addWidget(self.color_label)

        # Preset colors
        presets = ["#2563EB", "#DC2626", "#16A34A", "#D97706", "#7C3AED", "#0891B2", "#BE185D", "#374151"]
        for color in presets:
            btn = QPushButton()
            btn.setFixedSize(24, 24)
            btn.setStyleSheet(f"""
                QPushButton {{
                    background-color: {color};
                    border-radius: 4px;
                    border: 2px solid transparent;
                }}
                QPushButton:hover {{ border-color: white; }}
            """)
            btn.clicked.connect(lambda checked, c=color: self._set_color(c))
            color_row.addWidget(btn)

        color_row.addStretch()
        color_widget = QWidget()
        color_widget.setLayout(color_row)
        color_widget.setStyleSheet("background: transparent;")
        grid.addWidget(color_widget, 6, 1)

        layout.addLayout(grid)

        # Buttons
        btn_row = QHBoxLayout()
        btn_row.addStretch()

        cancel_btn = QPushButton("إلغاء")
        cancel_btn.setObjectName("cancelBtn")
        cancel_btn.clicked.connect(self.reject)
        btn_row.addWidget(cancel_btn)

        save_btn = QPushButton("💾 حفظ")
        save_btn.setObjectName("saveBtn")
        save_btn.setMinimumWidth(120)
        save_btn.clicked.connect(self._save)
        btn_row.addWidget(save_btn)

        layout.addLayout(btn_row)

    def _set_icon(self, emoji: str):
        self.icon_input.setText(emoji)
        self.selected_icon = emoji

    def _on_type_changed(self, index: int):
        tool_type = self.type_combo.currentData()
        show_browse = tool_type in (ToolType.FOLDER.value, ToolType.FILE.value, ToolType.PROGRAM.value)
        self.browse_btn.setVisible(show_browse)

        placeholders = {
            ToolType.FOLDER.value: "مثال: C:\\Users\\Ahmad\\Documents",
            ToolType.FILE.value: "مثال: C:\\Projects\\report.xlsx",
            ToolType.URL.value: "مثال: https://github.com",
            ToolType.PROGRAM.value: "مثال: C:\\Program Files\\app.exe",
            ToolType.COMMAND.value: "مثال: powershell -Command \"Get-Date\"",
        }
        self.target_input.setPlaceholderText(placeholders.get(tool_type, ""))

    def _browse_target(self):
        tool_type = self.type_combo.currentData()
        if tool_type == ToolType.FOLDER.value:
            path = QFileDialog.getExistingDirectory(self, "اختر مجلد")
        else:
            path, _ = QFileDialog.getOpenFileName(self, "اختر ملف")
        if path:
            self.target_input.setText(path)

    def _pick_color(self):
        color = QColorDialog.getColor(
            QColor(self.selected_color), self, "اختر لون"
        )
        if color.isValid():
            self._set_color(color.name())

    def _set_color(self, hex_color: str):
        self.selected_color = hex_color
        self.color_label.setText(hex_color)
        self._update_color_btn()

    def _update_color_btn(self):
        self.color_btn.setStyleSheet(f"""
            QPushButton#colorBtn {{
                background-color: {self.selected_color};
                border-radius: 8px;
                border: 2px solid #45475A;
                min-width: 40px; max-width: 40px;
                min-height: 36px; max-height: 36px;
            }}
            QPushButton#colorBtn:hover {{ border-color: white; }}
        """)

    def _populate_fields(self, tool: Tool):
        self.name_input.setText(tool.name)
        idx = self.type_combo.findData(tool.tool_type)
        if idx >= 0:
            self.type_combo.setCurrentIndex(idx)
        self.target_input.setText(tool.target)
        idx_cat = self.category_combo.findText(tool.category)
        if idx_cat >= 0:
            self.category_combo.setCurrentIndex(idx_cat)
        self.desc_input.setPlainText(tool.description)
        self.icon_input.setText(tool.icon)
        self._set_color(tool.color)

    def _save(self):
        name = self.name_input.text().strip()
        target = self.target_input.text().strip()
        tool_type = self.type_combo.currentData()

        if not name:
            QMessageBox.warning(self, "تنبيه", "يرجى إدخال اسم الأداة")
            self.name_input.setFocus()
            return
        if not target:
            QMessageBox.warning(self, "تنبيه", "يرجى إدخال المسار أو الرابط")
            self.target_input.setFocus()
            return

        category = self.category_combo.currentText().strip() or "عام"
        if self.data_manager and category not in self.data_manager.get_categories():
            self.data_manager.add_category(category)

        if self.tool:
            self.tool.name = name
            self.tool.tool_type = tool_type
            self.tool.target = target
            self.tool.description = self.desc_input.toPlainText().strip()
            self.tool.category = category
            self.tool.color = self.selected_color
            self.tool.icon = self.icon_input.text().strip()
        else:
            self.tool = Tool(
                id=str(uuid.uuid4()),
                name=name,
                tool_type=tool_type,
                target=target,
                description=self.desc_input.toPlainText().strip(),
                category=category,
                color=self.selected_color,
                icon=self.icon_input.text().strip(),
            )

        self.accept()

    def get_tool(self) -> Tool:
        return self.tool
