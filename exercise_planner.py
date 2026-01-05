import sys
from math import isfinite

try:
    from PyQt6.QtWidgets import (
        QApplication,
        QWidget,
        QLabel,
        QLineEdit,
        QPushButton,
        QTableWidget,
        QTableWidgetItem,
        QVBoxLayout,
        QHBoxLayout,
        QMessageBox,
        QHeaderView,
        QComboBox,
    )
except Exception:
    raise SystemExit("PyQt6 is required. Install with: pip install PyQt6")


METS = {
    "散步": 3.5,
    "慢跑": 7.0,
    "游泳": 8.0,
    "跳繩": 12.0,
}


def kcal_per_minute(met: float, weight_kg: float) -> float:
    return met * 3.5 * weight_kg / 200.0


class Planner(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("運動時間與補水建議計算器")

        # Inputs
        self.weight_input = QLineEdit()
        self.weight_input.setPlaceholderText("體重 (kg)")

        self.loss_input = QLineEdit()
        self.loss_input.setPlaceholderText("想要減重 (kg)")

        self.height_input = QLineEdit()
        self.height_input.setPlaceholderText("身高 (cm)")

        self.age_input = QLineEdit()
        self.age_input.setPlaceholderText("年齡 (歲)")

        # Gender input
        self.gender_input = QComboBox()
        self.gender_input.addItems(["男", "女", "其他"])
        self.gender_input.setCurrentIndex(0)

        self.days_input = QLineEdit()
        self.days_input.setPlaceholderText("想要達成天數 (天)，預設 30 天")

        calc_btn = QPushButton("計算")
        calc_btn.clicked.connect(self.calculate)

        form_layout = QHBoxLayout()
        form_layout.addWidget(self.weight_input)
        form_layout.addWidget(self.loss_input)
        form_layout.addWidget(self.height_input)
        form_layout.addWidget(self.age_input)
        form_layout.addWidget(self.gender_input)
        form_layout.addWidget(self.days_input)
        form_layout.addWidget(calc_btn)

        # Table
        self.table = QTableWidget(0, 5)
        self.table.setHorizontalHeaderLabels(["運動項目", "所需時間 (min)", "總時數 (hr)", "每天平均 (min/day)", "建議補水量 (ml)"])
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.ResizeMode.Stretch)

        # Footer label
        self.note_label = QLabel("說明：每消耗 1 kcal 建議補充 1 ml 水；1 kg 體脂約等於 7700 kcal。")

        layout = QVBoxLayout()
        layout.addLayout(form_layout)
        layout.addWidget(self.table)
        layout.addWidget(self.note_label)

        self.setLayout(layout)

    def calculate(self):
        try:
            weight = float(self.weight_input.text())
            loss_kg = float(self.loss_input.text())
        except Exception:
            QMessageBox.warning(self, "輸入錯誤", "請輸入有效的體重與想要減重公斤數。")
            return

        # parse optional height and age
        try:
            height = float(self.height_input.text()) if self.height_input.text().strip() else 0.0
        except Exception:
            height = 0.0

        try:
            age = int(self.age_input.text()) if self.age_input.text().strip() else 0
        except Exception:
            age = 0

        try:
            days = int(self.days_input.text()) if self.days_input.text().strip() else 30
            if days <= 0:
                days = 30
        except Exception:
            days = 30

        # Basic checks
        if weight <= 0 or loss_kg <= 0:
            QMessageBox.warning(self, "輸入錯誤", "體重與減重公斤數必須大於 0。")
            return

        total_kcal = loss_kg * 7700.0

        self.table.setRowCount(0)

        gender = self.gender_input.currentText()

        # compute BMR using Mifflin-St Jeor
        if gender == "男":
            bmr = 10.0 * weight + 6.25 * height - 5.0 * age + 5.0
        elif gender == "女":
            bmr = 10.0 * weight + 6.25 * height - 5.0 * age - 161.0
        else:
            bmr = 10.0 * weight + 6.25 * height - 5.0 * age

        for name, met in METS.items():
            kcal_min = kcal_per_minute(met, weight)
            if not isfinite(kcal_min) or kcal_min <= 0:
                minutes_needed = float('inf')
            else:
                minutes_needed = total_kcal / kcal_min

            hours_total = minutes_needed / 60.0
            daily_avg = minutes_needed / days

            water_ml = round(total_kcal)

            r = self.table.rowCount()
            self.table.insertRow(r)

            self.table.setItem(r, 0, QTableWidgetItem(name))
            self.table.setItem(r, 1, QTableWidgetItem(f"{minutes_needed:.1f}"))
            self.table.setItem(r, 2, QTableWidgetItem(f"{hours_total:.2f}"))
            self.table.setItem(r, 3, QTableWidgetItem(f"{daily_avg:.1f}"))
            self.table.setItem(r, 4, QTableWidgetItem(str(water_ml)))

        daily_deficit = total_kcal / days if days > 0 else total_kcal

        self.note_label.setText(
            f"總熱量目標：{total_kcal:.0f} kcal；每日需額外消耗：{daily_deficit:.0f} kcal/day；BMR：{bmr:.0f} kcal/day；補水建議總量：{round(total_kcal)} ml；性別：{gender}"
        )


def main():
    app = QApplication(sys.argv)
    w = Planner()
    w.resize(900, 400)
    w.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
