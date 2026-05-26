# -*- coding: utf-8 -*-
"""共享 UI 工具函数"""
from PySide6.QtWidgets import QMessageBox, QApplication
from PySide6.QtCore import QObject, QEvent, QPropertyAnimation, QEasingCurve, QPoint, Qt


def shake_widget(widget):
    """抖动控件，提醒用户注意"""
    if getattr(widget, '_shaking', False):
        return
    widget._shaking = True
    pos = widget.pos()
    anim = QPropertyAnimation(widget, b"pos")
    anim.setDuration(100)
    anim.setLoopCount(6)
    anim.setKeyValueAt(0, pos)
    anim.setKeyValueAt(0.3, pos)
    anim.setKeyValueAt(0.5, QPoint(pos.x() + 10, pos.y()))
    anim.setKeyValueAt(0.7, QPoint(pos.x() - 10, pos.y()))
    anim.setEndValue(pos)
    anim.setEasingCurve(QEasingCurve.InOutCubic)
    anim.finished.connect(lambda: setattr(widget, '_shaking', False))
    anim.finished.connect(lambda p=pos, w=widget: w.move(p))
    anim.start()


class _ModalShakeFilter(QObject):
    """安装到模态对话框上，失焦时抖动"""
    def eventFilter(self, watched, event):
        if event.type() == QEvent.WindowDeactivate and watched.isVisible():
            shake_widget(watched)
        return False


def show_modal(parent, icon, title, text, buttons=QMessageBox.Ok):
    """显示 ApplicationModal 对话框，点击其他窗口时抖动提醒"""
    msg = QMessageBox(icon, title, text, buttons, parent)
    msg.setWindowModality(Qt.ApplicationModal)
    msg.installEventFilter(_ModalShakeFilter(msg))
    return msg.exec()
