# -*- coding: utf-8 -*-
"""翻译历史记录管理器 — JSON 文件存储，超过 3 天自动清理"""
import json
import time
import uuid
from datetime import datetime, timedelta
from pathlib import Path


MAX_ENTRIES = 500
KEEP_DAYS = 3


class HistoryManager:
    def __init__(self, data_dir):
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.history_file = self.data_dir / "history.json"
        self.entries = self._load()

    def set_data_dir(self, new_dir):
        """切换数据目录：先保存当前数据，再加载新目录数据"""
        new_dir = Path(new_dir)
        if new_dir == self.data_dir:
            return
        new_dir.mkdir(parents=True, exist_ok=True)
        # 将当前数据写入旧目录
        self._save()
        # 切换到新目录
        self.data_dir = new_dir
        self.history_file = new_dir / "history.json"
        # 从新目录加载（可能为空，可能是已有数据）
        self.entries = self._load()

    def _clean_old(self, entries):
        cutoff = datetime.now() - timedelta(days=KEEP_DAYS)
        return [
            e for e in entries
            if datetime.strptime(e["timestamp"], "%Y-%m-%d %H:%M:%S") > cutoff
        ]

    def _load(self):
        if self.history_file.exists():
            try:
                with open(self.history_file, "r", encoding="utf-8") as f:
                    entries = json.load(f)
                cleaned = self._clean_old(entries)
                if len(cleaned) != len(entries):
                    self._save(cleaned)
                return cleaned
            except (json.JSONDecodeError, IOError):
                return []
        return []

    def _save(self, entries=None):
        if entries is None:
            entries = self.entries
        with open(self.history_file, "w", encoding="utf-8") as f:
            json.dump(entries, f, indent=2, ensure_ascii=False)

    def add(self, source_text, translated_text, engine, source_lang="auto", target_lang="zh"):
        # 与最新一条记录相同则跳过
        if self.entries:
            last = self.entries[0]
            if last["source_text"] == source_text and last["translated_text"] == translated_text:
                return None

        entry = {
            "id": uuid.uuid4().hex[:8],
            "source_text": source_text,
            "translated_text": translated_text,
            "engine": engine,
            "source_lang": source_lang,
            "target_lang": target_lang,
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
        }
        self.entries.insert(0, entry)
        # 清理过期和超量
        self.entries = self._clean_old(self.entries)[:MAX_ENTRIES]
        self._save()
        return entry

    def get_all(self):
        return list(self.entries)

    def delete(self, entry_id):
        self.entries = [e for e in self.entries if e["id"] != entry_id]
        self._save()

    def clear_all(self):
        self.entries = []
        self._save()

    def search(self, keyword):
        kw = keyword.lower()
        return [
            e for e in self.entries
            if kw in e["source_text"].lower() or kw in e["translated_text"].lower()
        ]
