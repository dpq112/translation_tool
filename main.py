# -*- coding: utf-8 -*-
"""翻译工具 — 入口"""
import sys
from PySide6.QtWidgets import QApplication
from PySide6.QtCore import Qt
from PySide6.QtGui import QIcon, QPixmap, QPainter, QColor, QFont
from app import App


def _create_app_icon():
    pixmap = QPixmap(64, 64)
    pixmap.fill(Qt.transparent)
    painter = QPainter(pixmap)
    painter.setRenderHint(QPainter.Antialiasing)
    painter.setBrush(QColor("#1a73e8"))
    painter.setPen(Qt.NoPen)
    painter.drawRoundedRect(2, 2, 60, 60, 12, 12)
    painter.setPen(Qt.white)
    font = QFont("Microsoft YaHei", 28, QFont.Bold)
    painter.setFont(font)
    painter.drawText(pixmap.rect(), Qt.AlignCenter, "译")
    painter.end()
    return QIcon(pixmap)


def main():
    # 设置 Windows 任务栏独立应用 ID，确保图标正确显示
    try:
        import ctypes
        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(
            "TranslationTool.App.1.0"
        )
    except Exception:
        pass

    app = QApplication(sys.argv)
    app.setQuitOnLastWindowClosed(False)

    # 全局应用图标（影响任务栏图标）
    icon = _create_app_icon()
    app.setWindowIcon(icon)

    translator_app = App(icon)
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
