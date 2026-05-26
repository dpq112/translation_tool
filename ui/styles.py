# -*- coding: utf-8 -*-
"""白色主题 — QSS 样式表"""
# 主色: #1a73e8 (蓝)  背景: #ffffff  次要背景: #f5f6f8
# 边框: #e0e4e8  文字: #1f2933  次要文字: #6b7280

APP_STYLE = """
* {
    font-family: "Microsoft YaHei UI", "Segoe UI", sans-serif;
    font-size: 13px;
    color: #1f2933;
}

/* ===== 迷你翻译窗口 ===== */
#miniWindow {
    background-color: #ffffff;
    border: 1px solid #dde1e6;
    border-radius: 10px;
}

#miniTitleBar {
    background-color: #f8f9fb;
    border-bottom: 1px solid #e8ecf0;
    border-top-left-radius: 10px;
    border-top-right-radius: 10px;
    padding: 5px 6px 5px 10px;
}

#miniTitleLabel {
    font-size: 12px;
    font-weight: bold;
    color: #4b5563;
}

#miniCloseBtn, #miniSettingsBtn {
    background: transparent;
    border: none;
    border-radius: 4px;
    padding: 3px 7px;
    font-size: 13px;
    color: #6b7280;
}

#miniCloseBtn:hover, #miniSettingsBtn:hover {
    background-color: #e5e7eb;
    color: #1f2933;
}

#miniCloseBtn:hover {
    background-color: #fee2e2;
    color: #ef4444;
}

#miniSourceText {
    border: 1px solid #e0e4e8;
    border-radius: 6px;
    padding: 7px 9px;
    font-size: 13px;
    background-color: #fafbfc;
    color: #1f2933;
    selection-background-color: #1a73e8;
    selection-color: #ffffff;
}

#miniSourceText:focus {
    border-color: #1a73e8;
    background-color: #ffffff;
}

#miniResultText {
    border: 1px solid #e0e4e8;
    border-radius: 6px;
    padding: 7px 9px;
    font-size: 13px;
    background-color: #f0f7ff;
    color: #1a73e8;
    selection-background-color: #1a73e8;
    selection-color: #ffffff;
}

/* ===== 完整翻译窗口 ===== */
#mainWindow {
    background-color: #ffffff;
}

#mainInputArea {
    border: 1px solid #dde1e6;
    border-radius: 8px;
    padding: 12px;
    font-size: 14px;
    background-color: #ffffff;
    color: #1f2933;
    selection-background-color: #1a73e8;
    selection-color: #ffffff;
}

#mainInputArea:focus {
    border-color: #1a73e8;
}

#mainOutputArea {
    border: 1px solid #dde1e6;
    border-radius: 8px;
    padding: 12px;
    font-size: 14px;
    background-color: #f8fafc;
    color: #1f2933;
    selection-background-color: #1a73e8;
    selection-color: #ffffff;
}

/* ===== 下拉框 ===== */
QComboBox {
    border: 1px solid #d0d5db;
    border-radius: 5px;
    padding: 4px 24px 4px 10px;
    background-color: #ffffff;
    color: #1f2933;
}

QComboBox:hover {
    border-color: #1a73e8;
}

QComboBox:focus {
    border-color: #1a73e8;
}

QComboBox::drop-down {
    border: none;
    width: 22px;
}

QComboBox::down-arrow {
    image: none;
    border-left: 4px solid transparent;
    border-right: 4px solid transparent;
    border-top: 5px solid #6b7280;
    margin-right: 7px;
}

QComboBox QAbstractItemView {
    border: 1px solid #dde1e6;
    border-radius: 6px;
    background-color: #ffffff;
    color: #1f2933;
    selection-background-color: #e8f0fe;
    selection-color: #1a73e8;
    outline: none;
    padding: 4px;
}

QComboBox QAbstractItemView::item {
    padding: 5px 10px;
    border-radius: 3px;
    min-height: 22px;
}

QComboBox QAbstractItemView::item:hover {
    background-color: #f0f4f8;
}

/* ===== 按钮 ===== */
QPushButton {
    border: 1px solid #d0d5db;
    border-radius: 5px;
    padding: 5px 14px;
    background-color: #ffffff;
    color: #374151;
    font-size: 12px;
}

QPushButton:hover {
    background-color: #f3f4f6;
    border-color: #b0b7c0;
}

QPushButton:pressed {
    background-color: #e5e7eb;
}

QPushButton#primaryBtn {
    background-color: #1a73e8;
    color: #ffffff;
    border: none;
    border-radius: 6px;
    padding: 7px 22px;
    font-weight: bold;
    font-size: 13px;
}

QPushButton#primaryBtn:hover {
    background-color: #1557b0;
}

QPushButton#primaryBtn:pressed {
    background-color: #1249a0;
}

QPushButton#textBtn {
    background: transparent;
    border: none;
    color: #6b7280;
    padding: 3px 8px;
    font-size: 12px;
}

QPushButton#textBtn:hover {
    color: #1a73e8;
}

QPushButton#accentBtn {
    background: transparent;
    border: 1px solid #1a73e850;
    color: #1a73e8;
    border-radius: 5px;
    padding: 5px 14px;
}

QPushButton#accentBtn:hover {
    background-color: #1a73e810;
    border-color: #1a73e8;
}

/* ===== 设置窗口 ===== */
#settingsWindow {
    background-color: #ffffff;
}

QGroupBox {
    border: 1px solid #e0e4e8;
    border-radius: 8px;
    margin-top: 14px;
    padding: 18px 14px 14px 14px;
    font-weight: bold;
    color: #374151;
    font-size: 13px;
}

QGroupBox::title {
    subcontrol-origin: margin;
    left: 12px;
    padding: 0 8px;
    color: #1a73e8;
}

QLineEdit {
    border: 1px solid #d0d5db;
    border-radius: 5px;
    padding: 7px 10px;
    min-height: 16px;
    font-size: 13px;
    background-color: #ffffff;
    color: #1f2933;
    selection-background-color: #1a73e8;
    selection-color: #ffffff;
}

QLineEdit:focus {
    border-color: #1a73e8;
}

QLineEdit:disabled {
    background-color: #f3f4f6;
    color: #9ca3af;
}

/* ===== 标签页 ===== */
QTabWidget::pane {
    border: 1px solid #e0e4e8;
    border-radius: 8px;
    background-color: #ffffff;
    top: -1px;
}

QTabBar::tab {
    background-color: transparent;
    color: #6b7280;
    padding: 7px 18px;
    border: none;
    border-bottom: 2px solid transparent;
    font-size: 13px;
    margin-right: 2px;
}

QTabBar::tab:selected {
    color: #1a73e8;
    border-bottom: 2px solid #1a73e8;
}

QTabBar::tab:hover:!selected {
    color: #374151;
    border-bottom: 2px solid #dde1e6;
}

/* ===== 标签和辅助文字 ===== */
QLabel {
    color: #374151;
    background: transparent;
}

QLabel#hintLabel {
    color: #6b7280;
    font-size: 12px;
}

/* ===== 滚动条 ===== */
QScrollBar:vertical {
    border: none;
    background: transparent;
    width: 6px;
    margin: 2px;
}

QScrollBar::handle:vertical {
    background: #cbd5e1;
    border-radius: 3px;
    min-height: 24px;
}

QScrollBar::handle:vertical:hover {
    background: #94a3b8;
}

QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
    border: none;
    background: none;
    height: 0;
}

QScrollBar:horizontal {
    border: none;
    background: transparent;
    height: 6px;
    margin: 2px;
}

QScrollBar::handle:horizontal {
    background: #cbd5e1;
    border-radius: 3px;
    min-width: 24px;
}

QScrollBar::handle:horizontal:hover {
    background: #94a3b8;
}

QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {
    border: none;
    background: none;
    width: 0;
}

/* ===== 工具提示 ===== */
QToolTip {
    background-color: #ffffff;
    color: #374151;
    border: 1px solid #dde1e6;
    border-radius: 5px;
    padding: 5px 9px;
    font-size: 12px;
}

/* ===== 状态栏 ===== */
QStatusBar {
    background-color: #f8f9fb;
    border-top: 1px solid #e8ecf0;
    color: #6b7280;
    font-size: 12px;
    padding: 3px 10px;
}

/* ===== 分割线 ===== */
QSplitter::handle {
    background-color: #e0e4e8;
    margin: 2px 0;
}

QSplitter::handle:horizontal { width: 1px; }
QSplitter::handle:vertical { height: 1px; }

/* ===== 快捷键标签 ===== */
#hotkeyTag {
    background-color: #e8f0fe;
    color: #1a73e8;
    border: 1px solid #1a73e830;
    border-radius: 5px;
    padding: 4px 10px;
    font-family: "Consolas", "Cascadia Code", monospace;
    font-size: 13px;
    font-weight: bold;
}

#hotkeyTag:hover {
    background-color: #d2e3fc;
    border-color: #1a73e860;
}

/* ===== 消息框 ===== */
QMessageBox {
    background-color: #ffffff;
}

QMessageBox QLabel {
    color: #1f2933;
    font-size: 13px;
}

QMessageBox QPushButton {
    min-width: 80px;
    padding: 5px 18px;
}
"""
