# -*- coding: utf-8 -*-
"""完整翻译窗口 — 支持手动输入、粘贴、多引擎切换"""
from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QPlainTextEdit, QComboBox, QSplitter,
    QStatusBar, QApplication,
)
from PySide6.QtCore import Qt, Signal, QTimer

from .mini_window import LANGUAGES


class MainWindow(QMainWindow):
    translate_requested = Signal(str, str, str, str)
    engine_changed = Signal(str)
    switch_to_mini = Signal()
    history_clicked = Signal()

    def __init__(self, config_manager, icon=None):
        super().__init__()
        self.config = config_manager
        self._icon = icon
        self._init_ui()
        self._apply_style()
        if icon:
            self.setWindowIcon(icon)

        self.debounce_timer = QTimer()
        self.debounce_timer.setSingleShot(True)
        self.debounce_timer.setInterval(600)
        self.debounce_timer.timeout.connect(self._do_translate)
        self.input_area.textChanged.connect(lambda: self.debounce_timer.start())

    def _init_ui(self):
        self.setWindowTitle("翻译工具")
        self.resize(900, 560)
        self.setMinimumSize(640, 420)
        self.setWindowFlags(
            Qt.Window
            | Qt.WindowMinimizeButtonHint
            | Qt.WindowMaximizeButtonHint
            | Qt.WindowCloseButtonHint
        )
        self.setObjectName("mainWindow")

        central = QWidget()
        self.setCentralWidget(central)
        layout = QVBoxLayout()
        layout.setContentsMargins(18, 12, 18, 14)
        layout.setSpacing(8)

        # ── 工具栏第一行：引擎 + 语言 ──
        toolbar1 = QHBoxLayout()
        toolbar1.setSpacing(10)

        toolbar1.addWidget(QLabel("翻译引擎"))
        self.engine_combo = QComboBox()
        self.engine_combo.setMinimumWidth(140)
        self.engine_combo.addItem("Google 翻译", "google")
        self.engine_combo.currentIndexChanged.connect(self._on_engine_changed)

        toolbar1.addWidget(self.engine_combo)

        toolbar1.addSpacing(20)

        toolbar1.addWidget(QLabel("原文语言"))
        self.source_lang = QComboBox()
        self.source_lang.setMinimumWidth(105)
        for code, name in LANGUAGES:
            self.source_lang.addItem(name, code)
        self.source_lang.setCurrentIndex(0)
        self.source_lang.currentIndexChanged.connect(self._on_lang_changed)
        toolbar1.addWidget(self.source_lang)

        self.swap_btn = QPushButton("⇄")
        self.swap_btn.setFixedWidth(36)
        self.swap_btn.setToolTip("交换语言")
        self.swap_btn.clicked.connect(self._swap_languages)
        toolbar1.addWidget(self.swap_btn)

        toolbar1.addWidget(QLabel("译文语言"))
        self.to_lang = QComboBox()
        self.to_lang.setMinimumWidth(105)
        for code, name in LANGUAGES:
            if code != "auto":
                self.to_lang.addItem(name, code)
        self.to_lang.setCurrentText("英语")
        self.to_lang.currentIndexChanged.connect(self._on_lang_changed)
        toolbar1.addWidget(self.to_lang)

        toolbar1.addStretch()

        self.history_btn = QPushButton("历史记录")
        self.history_btn.setObjectName("textBtn")
        self.history_btn.clicked.connect(self.history_clicked)
        toolbar1.addWidget(self.history_btn)

        self.mini_btn = QPushButton("切换到小窗口")
        self.mini_btn.setObjectName("accentBtn")
        self.mini_btn.clicked.connect(self._switch_to_mini)
        toolbar1.addWidget(self.mini_btn)

        layout.addLayout(toolbar1)

        # ── 输入区域 ──
        self.input_area = QPlainTextEdit()
        self.input_area.setObjectName("mainInputArea")
        self.input_area.setPlaceholderText("在此输入或粘贴要翻译的文字...")
        layout.addWidget(self.input_area, stretch=3)

        # ── 译文标题行 ──
        output_header = QHBoxLayout()
        output_header.addWidget(QLabel("译文"))
        output_header.addStretch()

        self.copy_btn = QPushButton("复制结果")
        self.copy_btn.clicked.connect(self._copy_result)
        output_header.addWidget(self.copy_btn)

        self.clear_btn = QPushButton("清空")
        self.clear_btn.clicked.connect(self._clear)
        output_header.addWidget(self.clear_btn)

        layout.addLayout(output_header)

        # ── 输出区域 ──
        self.output_area = QPlainTextEdit()
        self.output_area.setObjectName("mainOutputArea")
        self.output_area.setReadOnly(True)
        self.output_area.setPlaceholderText("翻译结果将显示在这里...")
        layout.addWidget(self.output_area, stretch=4)

        central.setLayout(layout)

        # ── 状态栏 ──
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_label = QLabel("就绪 — Google 翻译")
        self.status_bar.addWidget(self.status_label)

    def _apply_style(self):
        from ui.styles import APP_STYLE
        self.setStyleSheet(APP_STYLE)

    def _do_translate(self):
        text = self.input_area.toPlainText().strip()
        if not text:
            self.output_area.clear()
            return
        self.translate_requested.emit(
            text,
            self.source_lang.currentData(),
            self.to_lang.currentData(),
            self.engine_combo.currentData(),
        )

    def _on_lang_changed(self):
        if self.input_area.toPlainText().strip():
            self._do_translate()

    def _on_engine_changed(self):
        engine = self.engine_combo.currentData()
        self.engine_changed.emit(engine)
        if self.input_area.toPlainText().strip():
            self._do_translate()

    def _swap_languages(self):
        src_idx = self.source_lang.currentIndex()
        if self.source_lang.itemData(src_idx) == "auto":
            return
        src_text = self.source_lang.currentText()
        tgt_text = self.to_lang.currentText()
        self.source_lang.setCurrentText(tgt_text)
        self.to_lang.setCurrentText(src_text)

    def _copy_result(self):
        text = self.output_area.toPlainText()
        if text:
            QApplication.clipboard().setText(text)
            self.status_bar.showMessage("已复制到剪贴板", 2000)

    def _clear(self):
        self.input_area.clear()
        self.output_area.clear()

    def _switch_to_mini(self):
        """切换回小窗口 — 无论有无文字都允许切换"""
        self.switch_to_mini.emit()

    def set_source_text(self, text):
        self.input_area.setPlainText(text)

    def set_result_text(self, text):
        self.output_area.setPlainText(text)

    def set_status(self, text):
        self.status_label.setText(text)
        self.status_bar.showMessage(text, 3000)

    def update_engines(self, engines):
        current = self.engine_combo.currentData()
        self.engine_combo.blockSignals(True)
        self.engine_combo.clear()
        for key, translator in engines:
            self.engine_combo.addItem(translator.name, key)
        idx = self.engine_combo.findData(current)
        if idx >= 0:
            self.engine_combo.setCurrentIndex(idx)
        self.engine_combo.blockSignals(False)
