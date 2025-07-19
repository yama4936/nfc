#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
交通系IC（Suica / manaca など）履歴ビューア  PyQt6 + nfcpy

実行前に:
    pip install pyqt6 nfcpy
"""

from __future__ import annotations

import csv
import struct
import binascii
import sys
import os
from pathlib import Path

import nfc  # nfcpy
from PyQt6.QtCore import QThread, pyqtSignal, Qt
from PyQt6.QtWidgets import (
    QApplication,
    QMainWindow,
    QLabel,
    QWidget,
    QVBoxLayout,
    QTableWidget,
    QTableWidgetItem,
    QHeaderView,
)

# ---------- 解析ロジック ---------- #

NUM_BLOCKS = 20
SERVICE_CODE = 0x090F  # 履歴サービスコード


class StationRecord:
    _db: list[StationRecord] | None = None

    def __init__(self, row: list[str]):
        self.area_key = int(row[0])
        self.line_key = int(row[1])
        self.station_key = int(row[2])
        self.company_value = row[3]
        self.line_value = row[4]
        self.station_value = row[5]

    @classmethod
    def _load_db(cls) -> None:
        csv_path = Path(__file__).with_name("StationCode.csv")
        with csv_path.open(encoding="utf-8") as f:
            reader = csv.reader(f)
            cls._db = [cls(r) for r in reader]

    @classmethod
    def get_station(cls, line_key: int, station_key: int) -> "StationRecord":
        if cls._db is None:
            cls._load_db()
        for st in cls._db:  # type: ignore[operator]
            if st.line_key == line_key and st.station_key == station_key:
                return st
        # 見つからなければダミー
        return cls(["0", "0", "0", "—", "—", "—"])

    # 文字列表現を一括で返すユーティリティ
    def pretty(self) -> str:
        return f"{self.company_value}{self.station_value}"


class HistoryRecord:
    def __init__(self, data: bytes):
        be = struct.unpack(">2B2H4BH4B", data)
        le = struct.unpack("<2B2H4BH4B", data)

        self.console = self._console(be[0])
        self.process = self._process(be[1])
        self.year = (be[3] >> 9) & 0x7F
        self.month = (be[3] >> 5) & 0x0F
        self.day = be[3] & 0x1F
        self.balance = le[8]

        self.in_station = StationRecord.get_station(be[4], be[5])
        self.out_station = StationRecord.get_station(be[6], be[7])
        self.raw = data

    @staticmethod
    def _console(k: int) -> str:
        return {
            0x03: "精算機",
            0x04: "携帯端末",
            0x05: "車載端末",
            0x12: "券売機",
            0x16: "改札機",
            0x1C: "乗継精算機",
            0xC8: "自販機",
        }.get(k, f"0x{k:02X}")

    @staticmethod
    def _process(k: int) -> str:
        return {
            0x01: "運賃支払",
            0x02: "チャージ",
            0x0F: "バス",
            0x46: "物販",
        }.get(k, f"0x{k:02X}")


# ---------- NFC 読取スレッド ---------- #


class NFCWorker(QThread):
    record_read = pyqtSignal(int, HistoryRecord)
    status = pyqtSignal(str)

    def run(self) -> None:
        try:
            clf = nfc.ContactlessFrontend("usb")
        except IOError:
            self.status.emit("USB リーダーが見つかりません")
            return

        self.status.emit("カードをタッチしてください…")

        while True:
            try:
                clf.connect(rdwr={"on-connect": self.on_connect})
            except Exception as e:
                self.status.emit(f"NFC 例外: {e}")
                break

    def on_connect(self, tag) -> bool:  # noqa: ANN001
        if not isinstance(tag, nfc.tag.tt3.Type3Tag):
            self.status.emit("Type 3 Tag ではありません")
            return True

        sc = nfc.tag.tt3.ServiceCode(SERVICE_CODE >> 6, SERVICE_CODE & 0x3F)
        for i in range(NUM_BLOCKS):
            bc = nfc.tag.tt3.BlockCode(i, service=0)
            data = tag.read_without_encryption([sc], [bc])
            rec = HistoryRecord(bytes(data))
            self.record_read.emit(i, rec)

        self.status.emit("読み取り完了！再タッチで更新")
        return True


# ---------- GUI ---------- #


class MainWindow(QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("IC 履歴ビューア")
        self.resize(950, 500)

        self.status_label = QLabel(alignment=Qt.AlignmentFlag.AlignCenter)
        self.table = QTableWidget(NUM_BLOCKS, 8)
        self.table.setHorizontalHeaderLabels(
            ["No.", "日付", "端末", "処理", "入駅", "出駅", "残高 (円)", "RAW"]
        )
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table.verticalHeader().setVisible(False)
        self.table.setAlternatingRowColors(True)

        lay = QVBoxLayout()
        lay.addWidget(self.status_label)
        lay.addWidget(self.table)
        central = QWidget()
        central.setLayout(lay)
        self.setCentralWidget(central)

        # スレッド起動
        self.worker = NFCWorker()
        self.worker.record_read.connect(self.add_row)
        self.worker.status.connect(self.set_status)
        self.worker.start()

    # ------- スロット ------- #
    def set_status(self, txt: str) -> None:
        self.status_label.setText(txt)

    def add_row(self, i: int, h: HistoryRecord) -> None:
        self.table.setItem(i, 0, QTableWidgetItem(str(i + 1)))
        date_str = f"{2000 + h.year:04d}-{h.month:02d}-{h.day:02d}"
        self.table.setItem(i, 1, QTableWidgetItem(date_str))
        self.table.setItem(i, 2, QTableWidgetItem(h.console))
        self.table.setItem(i, 3, QTableWidgetItem(h.process))
        self.table.setItem(i, 4, QTableWidgetItem(h.in_station.pretty()))
        self.table.setItem(i, 5, QTableWidgetItem(h.out_station.pretty()))
        self.table.setItem(i, 6, QTableWidgetItem(str(h.balance)))
        self.table.setItem(i, 7, QTableWidgetItem(binascii.hexlify(h.raw).decode()))


# ---------- エントリポイント ---------- #


def main() -> None:
    app = QApplication(sys.argv)
    win = MainWindow()
    win.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
