# -*- coding: utf-8 -*-
"""剪贴板监听器 — 定时检测剪贴板变化，发现新文本时发出信号"""
from PySide6.QtCore import QTimer, QObject, Signal
from PySide6.QtWidgets import QApplication


class ClipboardMonitor(QObject):
    text_copied = Signal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.last_text = ""
        self.enabled = True

        self.timer = QTimer(self)
        self.timer.setInterval(400)
        self.timer.timeout.connect(self._check_clipboard)
        self.timer.start()

    def _check_clipboard(self):
        if not self.enabled:
            return
        try:
            clipboard = QApplication.clipboard()
            if clipboard is None:
                return
            text = clipboard.text()
            if text and text != self.last_text and len(text.strip()) > 0:
                self.last_text = text
                self.text_copied.emit(text.strip())
        except Exception:
            pass

    def set_enabled(self, enabled):
        self.enabled = enabled
        if not enabled:
            self.last_text = ""
