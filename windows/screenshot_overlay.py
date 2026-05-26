# -*- coding: utf-8 -*-
"""截图选区浮层 — 全屏透明覆盖层，屏幕内容可见，拖拽选择截图区域"""
from PySide6.QtWidgets import QWidget, QApplication
from PySide6.QtCore import Qt, Signal, QRect, QPoint, QByteArray, QBuffer
from PySide6.QtGui import QPainter, QPen, QColor, QFont


class ScreenshotOverlay(QWidget):
    screenshot_taken = Signal(bytes)
    cancelled = Signal()

    def __init__(self):
        super().__init__()
        self.setWindowFlags(
            Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.Tool
        )
        self.setAttribute(Qt.WA_TranslucentBackground, False)
        self.setCursor(Qt.CrossCursor)

        screen = QApplication.primaryScreen()
        self.screenshot = screen.grabWindow(0)
        self.setGeometry(screen.geometry())

        self.start_point = None
        self.end_point = None
        self.selected_rect = None
        self._selection_made = False

        self.showFullScreen()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        # 先绘制完整屏幕截图，让用户看到所有内容
        painter.drawPixmap(self.rect(), self.screenshot)

        if self.selected_rect and self.selected_rect.width() > 0 and self.selected_rect.height() > 0:
            r = self.selected_rect
            # 在选区之外绘制半透明遮罩，突出选区
            mask = QColor(0, 0, 0, 110)
            # 上部
            if r.top() > 0:
                painter.fillRect(0, 0, self.width(), r.top(), mask)
            # 下部
            if r.bottom() < self.height() - 1:
                painter.fillRect(0, r.bottom() + 1, self.width(), self.height() - r.bottom() - 1, mask)
            # 左侧
            if r.left() > 0:
                painter.fillRect(0, r.top(), r.left(), r.height(), mask)
            # 右侧
            if r.right() < self.width() - 1:
                painter.fillRect(r.right() + 1, r.top(), self.width() - r.right() - 1, r.height(), mask)

            # 选区边框
            painter.setPen(QPen(QColor("#1a73e8"), 2))
            painter.drawRect(r)

            # 选区尺寸标签
            info = f"{r.width()} x {r.height()}"
            font = QFont("Microsoft YaHei", 10)
            painter.setFont(font)
            label_rect = QRect(r.left() + 4, r.top() + 2, 120, 24)
            if r.top() < 30:
                # 选区太靠顶部，标签放到选区内部下方
                label_rect.moveTop(r.bottom() - 26)
            painter.fillRect(label_rect, QColor(0, 0, 0, 170))
            painter.setPen(Qt.white)
            painter.drawText(label_rect, Qt.AlignCenter, info)

        else:
            # 未选择时：仅覆盖极浅的遮罩，提示用户处于截图模式
            painter.fillRect(self.rect(), QColor(0, 0, 0, 50))

            # 居中提示文字
            hint = "拖拽鼠标选择截图区域  |  ESC 取消  |  右键取消"
            font = QFont("Microsoft YaHei", 13)
            painter.setFont(font)
            hint_rect = painter.boundingRect(self.rect(), Qt.AlignCenter, hint)
            hint_rect.adjust(-20, -10, 20, 10)
            hint_rect.moveCenter(self.rect().center())
            painter.fillRect(hint_rect, QColor(0, 0, 0, 150))
            painter.setPen(Qt.white)
            painter.drawText(hint_rect, Qt.AlignCenter, hint)

        painter.end()

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.start_point = event.position().toPoint()
            self.end_point = None
            self.selected_rect = None
            self.update()
        elif event.button() == Qt.RightButton:
            self.close()

    def mouseMoveEvent(self, event):
        if self.start_point:
            self.end_point = event.position().toPoint()
            self.selected_rect = QRect(self.start_point, self.end_point).normalized()
            self.update()

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton:
            if self.selected_rect and self.selected_rect.width() > 10 and self.selected_rect.height() > 10:
                self._selection_made = True
                cropped = self.screenshot.copy(self.selected_rect)
                ba = QByteArray()
                buf = QBuffer(ba)
                buf.open(QBuffer.WriteOnly)
                cropped.save(buf, "PNG")
                buf.close()
                image_data = bytes(ba)
                self.screenshot_taken.emit(image_data)
            self.close()

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Escape:
            self.close()

    def closeEvent(self, event):
        if not self._selection_made:
            self.cancelled.emit()
        super().closeEvent(event)
