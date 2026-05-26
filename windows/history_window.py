# -*- coding: utf-8 -*-
"""翻译历史记录窗口"""
from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QLineEdit, QScrollArea, QFrame, QApplication,
    QMessageBox, QSizePolicy,
)
from PySide6.QtCore import Qt, Signal, QTimer, QEvent
from ui.utils import shake_widget, show_modal


class HistoryWindow(QMainWindow):
    show_translation_requested = Signal(str, str)  # source_text, translated_text

    def __init__(self, history_manager, icon=None):
        super().__init__()
        self.history = history_manager
        self._icon = icon
        self._all_entries = []
        self._init_ui()
        self._apply_style()
        if icon:
            self.setWindowIcon(icon)
        self._refresh()

    def _init_ui(self):
        self.setWindowTitle("翻译历史记录")
        self.resize(580, 620)
        self.setMinimumSize(420, 400)
        self.setWindowFlags(
            Qt.Window
            | Qt.WindowMinimizeButtonHint
            | Qt.WindowMaximizeButtonHint
            | Qt.WindowCloseButtonHint
        )
        self.setObjectName("historyWindow")

        central = QWidget()
        self.setCentralWidget(central)
        layout = QVBoxLayout()
        layout.setContentsMargins(16, 14, 16, 14)
        layout.setSpacing(10)

        # ── 顶部：搜索 + 清空 ──
        top_row = QHBoxLayout()
        top_row.setSpacing(10)

        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("搜索原文或译文...")
        self.search_input.textChanged.connect(self._on_search)
        top_row.addWidget(self.search_input, stretch=1)

        clear_btn = QPushButton("清空全部")
        clear_btn.setObjectName("dangerBtn")
        clear_btn.clicked.connect(self._clear_all)
        top_row.addWidget(clear_btn)

        layout.addLayout(top_row)

        # ── 记录数提示 ──
        self.count_label = QLabel("")
        self.count_label.setObjectName("hintLabel")
        layout.addWidget(self.count_label)

        # ── 滚动区域 ──
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.scroll_area.setObjectName("historyScroll")

        self.card_container = QWidget()
        self.card_layout = QVBoxLayout()
        self.card_layout.setContentsMargins(0, 0, 0, 0)
        self.card_layout.setSpacing(8)
        self.card_layout.addStretch()
        self.card_container.setLayout(self.card_layout)

        self.scroll_area.setWidget(self.card_container)
        layout.addWidget(self.scroll_area, stretch=1)

        central.setLayout(layout)

    def _apply_style(self):
        from ui.styles import APP_STYLE
        self.setStyleSheet(APP_STYLE + _HISTORY_STYLE)

    def _refresh(self):
        self._all_entries = self.history.get_all()
        self._render_cards(self._all_entries)

    def _on_search(self, keyword):
        if not keyword.strip():
            filtered = self._all_entries
        else:
            filtered = self.history.search(keyword.strip())
        self._render_cards(filtered)

    def _render_cards(self, entries):
        # 清除旧卡片
        while self.card_layout.count() > 1:  # 保留末尾的 stretch
            item = self.card_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        self.count_label.setText(f"共 {len(entries)} 条记录")

        for entry in entries:
            card = self._make_card(entry)
            self.card_layout.insertWidget(self.card_layout.count() - 1, card)

    def _make_card(self, entry):
        card = QFrame()
        card.setObjectName("historyCard")
        card_layout = QVBoxLayout()
        card_layout.setContentsMargins(12, 10, 12, 10)
        card_layout.setSpacing(4)

        # 原文
        src_label = QLabel(entry["source_text"])
        src_label.setObjectName("historySrc")
        src_label.setWordWrap(True)
        src_label.setMaximumHeight(40)
        src_label.setToolTip(entry["source_text"])
        card_layout.addWidget(src_label)

        # 译文
        tgt_label = QLabel(entry["translated_text"])
        tgt_label.setObjectName("historyTgt")
        tgt_label.setWordWrap(True)
        tgt_label.setMaximumHeight(40)
        tgt_label.setToolTip(entry["translated_text"])
        card_layout.addWidget(tgt_label)

        # 底部信息行
        info_row = QHBoxLayout()
        info_row.setSpacing(12)

        meta = f"{entry['timestamp']}  ·  {entry['engine']}"
        meta_label = QLabel(meta)
        meta_label.setObjectName("hintLabel")
        info_row.addWidget(meta_label)
        info_row.addStretch()

        copy_src_btn = QPushButton("复制原文")
        copy_src_btn.setObjectName("textBtn")
        copy_src_btn.clicked.connect(lambda checked=False, t=entry["source_text"], b=copy_src_btn: self._copy_text(t, b))
        info_row.addWidget(copy_src_btn)

        copy_tgt_btn = QPushButton("复制译文")
        copy_tgt_btn.setObjectName("textBtn")
        copy_tgt_btn.clicked.connect(lambda checked=False, t=entry["translated_text"], b=copy_tgt_btn: self._copy_text(t, b))
        info_row.addWidget(copy_tgt_btn)

        del_btn = QPushButton("删除")
        del_btn.setObjectName("textBtn")
        del_btn.clicked.connect(lambda checked=False, eid=entry["id"], b=del_btn: self._delete_entry(eid, b))
        info_row.addWidget(del_btn)

        card_layout.addLayout(info_row)
        card.setLayout(card_layout)
        return card

    def _copy_text(self, text, btn):
        QApplication.clipboard().setText(text)
        original = btn.text()
        btn.setText("已复制")
        QTimer.singleShot(1500, lambda b=btn, o=original: b.setText(o))

    def _delete_entry(self, entry_id, btn):
        self.history.delete(entry_id)
        # 从当前列表中移除该卡片
        btn.setText("已删除")
        QTimer.singleShot(300, lambda: self._do_refresh())

    def _clear_all(self):
        if not self._all_entries:
            return
        reply = show_modal(
            self, QMessageBox.Question, "确认清空",
            f"确定要清空全部 {len(self._all_entries)} 条翻译历史记录吗？",
            QMessageBox.Yes | QMessageBox.No,
        )
        if reply == QMessageBox.Yes:
            self.history.clear_all()
            self._refresh()

    def showEvent(self, event):
        super().showEvent(event)
        self._refresh()

    def changeEvent(self, event):
        if event.type() == QEvent.ActivationChange and not self.isActiveWindow():
            modal = QApplication.activeModalWidget()
            if modal is not None:
                shake_widget(self)
                shake_widget(modal)
            else:
                self.showMinimized()
        super().changeEvent(event)

    def _do_refresh(self):
        self._refresh()
        keyword = self.search_input.text().strip()
        if keyword:
            self._on_search(keyword)


_HISTORY_STYLE = """
#historyWindow {
    background-color: #ffffff;
}

#historyScroll {
    border: none;
    background-color: transparent;
}

#historyCard {
    background-color: #f8f9fb;
    border: 1px solid #e8ecf0;
    border-radius: 8px;
}

#historySrc {
    font-size: 13px;
    color: #1f2933;
}

#historyTgt {
    font-size: 13px;
    color: #1a73e8;
    font-weight: bold;
}

QPushButton#dangerBtn {
    background-color: transparent;
    color: #ef4444;
    border: 1px solid #ef444450;
    border-radius: 5px;
    padding: 6px 14px;
    font-size: 12px;
}

QPushButton#dangerBtn:hover {
    background-color: #fef2f2;
    border-color: #ef4444;
}
"""
