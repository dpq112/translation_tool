# -*- coding: utf-8 -*-
"""迷你翻译窗口 — 无边框、始终置顶、实时翻译"""
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QPlainTextEdit, QComboBox, QApplication,
)
from PySide6.QtCore import Qt, Signal, QTimer, QPoint
from PySide6.QtGui import QMouseEvent, QIcon


LANGUAGES = [
    ("auto", "自动检测"),
    ("zh", "中文"),
    ("en", "英语"),
    ("ja", "日语"),
    ("ko", "韩语"),
    ("fr", "法语"),
    ("de", "德语"),
    ("es", "西班牙语"),
    ("ru", "俄语"),
    ("pt", "葡萄牙语"),
    ("it", "意大利语"),
    ("th", "泰语"),
    ("vi", "越南语"),
    ("ar", "阿拉伯语"),
]


class MiniWindow(QWidget):
    translate_requested = Signal(str, str, str, str)
    engine_changed = Signal(str)
    settings_clicked = Signal()
    show_main_window = Signal()
    history_clicked = Signal()

    def __init__(self, config_manager, available_engines=None, icon=None):
        super().__init__()
        self.config = config_manager
        self.dragging = False
        self.drag_offset = QPoint()
        self.engines = available_engines or []
        self._icon = icon
        self._init_ui()
        self._apply_style()
        if icon:
            self.setWindowIcon(icon)

        self.debounce_timer = QTimer()
        self.debounce_timer.setSingleShot(True)
        self.debounce_timer.setInterval(500)
        self.debounce_timer.timeout.connect(self._do_translate)
        self.source_text.textChanged.connect(lambda: self.debounce_timer.start())

    def _init_ui(self):
        self.setWindowTitle("翻译小窗口")
        self.setWindowFlags(
            Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.Tool
        )
        self.setAttribute(Qt.WA_TranslucentBackground, False)
        self.setFixedSize(420, 400)
        self.setObjectName("miniWindow")

        layout = QVBoxLayout()
        layout.setContentsMargins(10, 5, 10, 10)
        layout.setSpacing(6)

        # ── 标题栏 ──
        title_bar = QHBoxLayout()
        if self._icon:
            icon_label = QLabel()
            icon_label.setPixmap(self._icon.pixmap(18, 18))
            title_bar.addWidget(icon_label)
        self.title_label = QLabel("翻译小窗口")
        self.title_label.setObjectName("miniTitleLabel")
        title_bar.addWidget(self.title_label)
        title_bar.addStretch()

        self.settings_btn = QPushButton("⚙")
        self.settings_btn.setObjectName("miniSettingsBtn")
        self.settings_btn.setToolTip("设置")
        self.settings_btn.setFixedSize(28, 28)
        self.settings_btn.clicked.connect(self.settings_clicked)
        title_bar.addWidget(self.settings_btn)

        self.pin_btn = QPushButton("📌")
        self.pin_btn.setObjectName("miniSettingsBtn")
        self.pin_btn.setToolTip("置顶 / 取消置顶")
        self.pin_btn.setFixedSize(28, 28)
        self.pin_btn.clicked.connect(self._toggle_pin)
        title_bar.addWidget(self.pin_btn)

        self.min_btn = QPushButton("─")
        self.min_btn.setObjectName("miniSettingsBtn")
        self.min_btn.setToolTip("最小化")
        self.min_btn.setFixedSize(28, 28)
        self.min_btn.clicked.connect(lambda: self.showMinimized())
        title_bar.addWidget(self.min_btn)

        self.close_btn = QPushButton("✕")
        self.close_btn.setObjectName("miniCloseBtn")
        self.close_btn.setFixedSize(28, 28)
        self.close_btn.clicked.connect(self.hide)
        title_bar.addWidget(self.close_btn)

        title_widget = QWidget()
        title_widget.setObjectName("miniTitleBar")
        title_widget.setLayout(title_bar)
        layout.addWidget(title_widget)

        # ── 引擎选择行 ──
        engine_row = QHBoxLayout()
        engine_label = QLabel("翻译引擎")
        engine_label.setMinimumWidth(56)
        engine_row.addWidget(engine_label)
        self.engine_combo = QComboBox()
        self.engine_combo.setMinimumWidth(150)
        for key, translator in self.engines:
            self.engine_combo.addItem(translator.name, key)
        default_engine = self.config.get("default_engine", "google")
        idx = self.engine_combo.findData(default_engine)
        if idx >= 0:
            self.engine_combo.setCurrentIndex(idx)
        self.engine_combo.currentIndexChanged.connect(self._on_engine_changed)
        engine_row.addWidget(self.engine_combo)
        engine_row.addStretch()
        layout.addLayout(engine_row)

        # ── 语言选择行 ──
        lang_row = QHBoxLayout()
        src_label = QLabel("原文语言")
        src_label.setMinimumWidth(56)
        lang_row.addWidget(src_label)
        self.source_lang = QComboBox()
        self.source_lang.setMinimumWidth(120)
        for code, name in LANGUAGES:
            self.source_lang.addItem(name, code)
        self.source_lang.setCurrentIndex(0)
        self.source_lang.currentIndexChanged.connect(self._on_lang_changed)
        lang_row.addWidget(self.source_lang)

        lang_row.addSpacing(8)

        tgt_label = QLabel("译文语言")
        tgt_label.setMinimumWidth(56)
        lang_row.addWidget(tgt_label)
        self.to_lang = QComboBox()
        self.to_lang.setMinimumWidth(120)
        for code, name in LANGUAGES:
            if code != "auto":
                self.to_lang.addItem(name, code)
        self.to_lang.setCurrentText("英语")
        self.to_lang.currentIndexChanged.connect(self._on_lang_changed)
        lang_row.addWidget(self.to_lang)
        lang_row.addStretch()
        layout.addLayout(lang_row)

        # ── 原文区域 ──
        src_header = QHBoxLayout()
        src_header.addWidget(QLabel("原文"))
        src_header.addStretch()
        layout.addLayout(src_header)

        self.source_text = QPlainTextEdit()
        self.source_text.setObjectName("miniSourceText")
        self.source_text.setPlaceholderText("在此输入或复制文字...")
        self.source_text.setMaximumHeight(65)
        layout.addWidget(self.source_text)

        # ── 译文区域 ──
        result_header = QHBoxLayout()
        result_header.addWidget(QLabel("译文"))
        result_header.addStretch()

        self.copy_btn = QPushButton("复制结果")
        self.copy_btn.setObjectName("textBtn")
        self.copy_btn.clicked.connect(self._copy_result)
        result_header.addWidget(self.copy_btn)

        self.clear_btn = QPushButton("清空")
        self.clear_btn.setObjectName("textBtn")
        self.clear_btn.clicked.connect(self._clear)
        result_header.addWidget(self.clear_btn)
        layout.addLayout(result_header)

        self.result_text = QPlainTextEdit()
        self.result_text.setObjectName("miniResultText")
        self.result_text.setReadOnly(True)
        self.result_text.setPlaceholderText("翻译结果...")
        layout.addWidget(self.result_text)

        # ── 底部状态 ──
        bottom_row = QHBoxLayout()
        self.status_label = QLabel("就绪")
        self.status_label.setObjectName("hintLabel")
        bottom_row.addWidget(self.status_label)
        bottom_row.addStretch()

        self.history_btn = QPushButton("历史")
        self.history_btn.setObjectName("textBtn")
        self.history_btn.clicked.connect(self.history_clicked)
        bottom_row.addWidget(self.history_btn)

        self.switch_btn = QPushButton("切换到大窗口 →")
        self.switch_btn.setObjectName("textBtn")
        self.switch_btn.clicked.connect(self._switch_to_main)
        bottom_row.addWidget(self.switch_btn)
        layout.addLayout(bottom_row)

        self.setLayout(layout)

    def _apply_style(self):
        from ui.styles import APP_STYLE
        self.setStyleSheet(APP_STYLE)

    def set_source_text(self, text):
        self.source_text.setPlainText(text)

    def set_result_text(self, text):
        self.result_text.setPlainText(text)

    def set_status(self, text):
        self.status_label.setText(text)

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
        self.engines = engines

    def set_engine_name(self, name):
        idx = self.engine_combo.findText(name)
        if idx >= 0:
            self.engine_combo.blockSignals(True)
            self.engine_combo.setCurrentIndex(idx)
            self.engine_combo.blockSignals(False)

    def _on_lang_changed(self):
        """语言切换时立即翻译"""
        if self.source_text.toPlainText().strip():
            self._do_translate()

    def _on_engine_changed(self):
        engine = self.engine_combo.currentData()
        if engine:
            self.engine_changed.emit(engine)
            if self.source_text.toPlainText().strip():
                self._do_translate()

    def _do_translate(self):
        text = self.source_text.toPlainText().strip()
        if not text:
            self.result_text.clear()
            return
        engine = self.engine_combo.currentData() or "google"
        self.translate_requested.emit(
            text, self.source_lang.currentData(), self.to_lang.currentData(), engine
        )

    def force_translate(self):
        self._do_translate()

    def get_translate_params(self):
        return (
            self.source_text.toPlainText().strip(),
            self.source_lang.currentData(),
            self.to_lang.currentData(),
            self.engine_combo.currentData() or "google",
        )

    def _copy_result(self):
        text = self.result_text.toPlainText()
        if text:
            QApplication.clipboard().setText(text)
            self.status_label.setText("已复制到剪贴板")

    def _clear(self):
        self.source_text.clear()
        self.result_text.clear()

    def _switch_to_main(self):
        self.show_main_window.emit()
        self.hide()

    def _toggle_pin(self):
        if self.windowFlags() & Qt.WindowStaysOnTopHint:
            self.setWindowFlags(self.windowFlags() & ~Qt.WindowStaysOnTopHint)
            self.pin_btn.setText("📌")
        else:
            self.setWindowFlags(self.windowFlags() | Qt.WindowStaysOnTopHint)
            self.pin_btn.setText("📍")
        self.show()

    # === 拖拽 ===
    def mousePressEvent(self, event: QMouseEvent):
        if event.button() == Qt.LeftButton:
            pos = event.position().toPoint()
            if pos.y() <= 36:
                self.dragging = True
                self.drag_offset = pos
                return
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event: QMouseEvent):
        if self.dragging:
            self.move(event.globalPosition().toPoint() - self.drag_offset)
            return
        super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event: QMouseEvent):
        self.dragging = False
        super().mouseReleaseEvent(event)
