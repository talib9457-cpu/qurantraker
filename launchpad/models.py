"""
LaunchPad - Data Models
نماذج البيانات لتطبيق LaunchPad
"""

import json
import os
from dataclasses import dataclass, field, asdict
from typing import List, Optional
from enum import Enum


class ToolType(Enum):
    FOLDER = "folder"
    FILE = "file"
    URL = "url"
    PROGRAM = "program"
    COMMAND = "command"


TOOL_TYPE_LABELS = {
    ToolType.FOLDER: "مجلد",
    ToolType.FILE: "ملف",
    ToolType.URL: "رابط ويب",
    ToolType.PROGRAM: "برنامج",
    ToolType.COMMAND: "أمر Windows",
}

TOOL_TYPE_ICONS = {
    ToolType.FOLDER: "📁",
    ToolType.FILE: "📄",
    ToolType.URL: "🌐",
    ToolType.PROGRAM: "⚙️",
    ToolType.COMMAND: "💻",
}


@dataclass
class Tool:
    id: str
    name: str
    tool_type: str
    target: str
    description: str = ""
    category: str = "عام"
    color: str = "#2563EB"
    icon: str = ""
    shortcut: str = ""

    def get_type(self) -> ToolType:
        return ToolType(self.tool_type)

    def get_display_icon(self) -> str:
        if self.icon:
            return self.icon
        return TOOL_TYPE_ICONS.get(self.get_type(), "🔧")

    def to_dict(self) -> dict:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict) -> "Tool":
        return cls(**data)


@dataclass
class AppData:
    tools: List[Tool] = field(default_factory=list)
    categories: List[str] = field(default_factory=lambda: ["عام", "أدوات", "ملفات", "روابط", "أوامر"])
    theme: str = "dark"
    version: str = "1.0.0"


class DataManager:
    def __init__(self):
        self.data_dir = os.path.join(
            os.path.expanduser("~"), "AppData", "Local", "LaunchPad"
        )
        # Fallback for non-Windows systems
        if not os.path.exists(os.path.expanduser("~\\AppData")):
            self.data_dir = os.path.join(os.path.expanduser("~"), ".launchpad")

        self.data_file = os.path.join(self.data_dir, "shortcuts.json")
        self._ensure_dir()
        self.app_data = self._load()

    def _ensure_dir(self):
        os.makedirs(self.data_dir, exist_ok=True)

    def _load(self) -> AppData:
        if not os.path.exists(self.data_file):
            return AppData()
        try:
            with open(self.data_file, "r", encoding="utf-8") as f:
                raw = json.load(f)
            tools = [Tool.from_dict(t) for t in raw.get("tools", [])]
            categories = raw.get("categories", AppData().categories)
            theme = raw.get("theme", "dark")
            return AppData(tools=tools, categories=categories, theme=theme)
        except Exception:
            return AppData()

    def save(self):
        data = {
            "version": self.app_data.version,
            "theme": self.app_data.theme,
            "categories": self.app_data.categories,
            "tools": [t.to_dict() for t in self.app_data.tools],
        }
        with open(self.data_file, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    def add_tool(self, tool: Tool):
        self.app_data.tools.append(tool)
        self.save()

    def update_tool(self, tool: Tool):
        for i, t in enumerate(self.app_data.tools):
            if t.id == tool.id:
                self.app_data.tools[i] = tool
                break
        self.save()

    def delete_tool(self, tool_id: str):
        self.app_data.tools = [t for t in self.app_data.tools if t.id != tool_id]
        self.save()

    def get_categories(self) -> List[str]:
        return self.app_data.categories

    def add_category(self, name: str):
        if name not in self.app_data.categories:
            self.app_data.categories.append(name)
            self.save()

    def get_tools_by_category(self, category: str) -> List[Tool]:
        if category == "الكل":
            return self.app_data.tools
        return [t for t in self.app_data.tools if t.category == category]

    def search_tools(self, query: str) -> List[Tool]:
        q = query.lower()
        return [
            t for t in self.app_data.tools
            if q in t.name.lower() or q in t.description.lower() or q in t.target.lower()
        ]
