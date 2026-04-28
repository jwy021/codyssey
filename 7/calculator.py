# calculator.py
import sys
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QGridLayout, QPushButton, QLineEdit
from PyQt5.QtCore import Qt

class Calculator(QWidget):
    def __init__(self):
        super().__init__()
        self.first_num = None
        self.operator = None
        self.wait_for_next_num = False
        self.formula = ""
        self.initUI()

    def initUI(self):
        self.setWindowTitle('Calculator')
        self.setFixedSize(350, 600) 
        self.setStyleSheet("background-color: black;") 

        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(15, 15, 15, 20)
        main_layout.setSpacing(5)

        self.display = QLineEdit('0')
        self.display.setReadOnly(True)
        self.display.setAlignment(Qt.AlignRight)
        self.display.setFixedHeight(100)
        self.display.textChanged.connect(self.adjust_font_size)
        self.adjust_font_size()
        main_layout.addWidget(self.display)

        self.history_display = QLineEdit('')
        self.history_display.setReadOnly(True)
        self.history_display.setAlignment(Qt.AlignRight)
        self.history_display.setStyleSheet("""
            QLineEdit {
                font-size: 20px;
                background-color: black;
                color: #888888;
                border: none;
                padding-right: 5px;
            }
        """)
        self.history_display.setFixedHeight(40)
        main_layout.addWidget(self.history_display)

        grid_layout = QGridLayout()
        grid_layout.setSpacing(12)

        buttons = [
            ('AC', 0, 0), ('+/-', 0, 1), ('%', 0, 2), ('÷', 0, 3),
            ('7', 1, 0), ('8', 1, 1), ('9', 1, 2), ('×', 1, 3),
            ('4', 2, 0), ('5', 2, 1), ('6', 2, 2), ('-', 2, 3),
            ('1', 3, 0), ('2', 3, 1), ('3', 3, 2), ('+', 3, 3),
            ('0', 4, 0, 1, 2), ('.', 4, 2), ('=', 4, 3)
        ]

        for btn in buttons:
            text = btn[0]
            button = QPushButton(text)
            button.setFixedSize(75, 75) if len(btn) == 3 else button.setFixedSize(162, 75)
            
            if text in ['÷', '×', '-', '+', '=']:
                style = "background-color: #f99f00; color: white; font-size: 30px; border-radius: 37px; font-weight: bold;"
            elif text in ['AC', '+/-', '%']:
                style = "background-color: #a5a5a5; color: black; font-size: 22px; border-radius: 37px; font-weight: 500;"
            else:
                style = "background-color: #333333; color: white; font-size: 28px; border-radius: 37px;"
            
            button.setStyleSheet(style)
            button.clicked.connect(self.button_clicked)

            if len(btn) == 3:
                grid_layout.addWidget(button, btn[1], btn[2])
            else:
                grid_layout.addWidget(button, btn[1], btn[2], btn[3], btn[4])

        main_layout.addLayout(grid_layout)
        self.setLayout(main_layout)

    def adjust_font_size(self):
        text_length = len(self.display.text())
        base_size = 70
        new_size = max(30, base_size - ((text_length - 7) * 5)) if text_length > 7 else base_size
        self.display.setStyleSheet(f"font-size: {new_size}px; background-color: black; color: white; border: none; font-weight: 300;")

    def button_clicked(self):
        button = self.sender()
        key = button.text()

        if key.isdigit(): self.input_number(key)
        elif key == '.': self.input_dot()
        elif key == 'AC': self.reset()
        elif key == '+/-': self.negative_positive()
        elif key == '%': self.percent()
        elif key in ['+', '-', '×', '÷']: self.set_operator(key)
        elif key == '=': self.equal()

    # --------------------------------------------------------
    # [로직 개선] 숫자 입력 제어
    # --------------------------------------------------------
    def input_number(self, num_str):
        if self.wait_for_next_num:
            self.display.setText(num_str)
            self.wait_for_next_num = False
            
            # [추가됨] '=' 버튼 이후 결과값이 있는 상태에서 연산자 대신 새 숫자를 누르면,
            # 이전 수식 기록을 완전히 지우고 아예 새로운 계산을 시작하도록 처리
            if self.first_num is None:
                self.history_display.setText("")
        else:
            current_text = self.display.text()
            if current_text == '0': self.display.setText(num_str)
            else: self.display.setText(current_text + num_str)

    def input_dot(self):
        if self.wait_for_next_num:
            self.display.setText('0.')
            self.wait_for_next_num = False
            if self.first_num is None:
                self.history_display.setText("")
        elif '.' not in self.display.text():
            self.display.setText(self.display.text() + '.')

    # --------------------------------------------------------
    # [로직 개선] 연산자 상태 머신(State Machine) 완벽 제어
    # --------------------------------------------------------
    def set_operator(self, op):
        current_val_str = self.display.text()

        # 1. 방금 '='을 눌러서 결과가 나온 상태에서 연산자를 누른 경우 (가장 원하시던 기능!)
        if self.wait_for_next_num and self.first_num is None:
            self.first_num = float(current_val_str)
            self.operator = op
            self.formula = f"{self.format_result(self.first_num)} {op} "
            self.history_display.setText(self.formula)
            return

        # 2. 연산자를 누른 직후 다른 연산자로 마음이 바뀐 경우 (예: + 누르고 바로 -)
        if self.wait_for_next_num and self.first_num is not None:
            self.operator = op
            if self.formula:
                parts = self.formula.split()
                if len(parts) >= 2:
                    parts[-1] = op
                    self.formula = " ".join(parts) + " "
            self.history_display.setText(self.formula)
            return

        # 3. 일반적인 연속 연산 처리 (예: 1 + 2 + ...)
        if self.first_num is not None and self.operator is not None:
            second_num = float(current_val_str)
            result = self.calculate(self.first_num, second_num, self.operator)
            
            if result == "Error":
                self.display.setText("Error")
                return
            
            self.formula += f"{self.format_result(second_num)} {op} "
            self.display.setText(self.format_result(result))
            self.first_num = result
        else:
            # 4. 아무것도 없는 0 상태에서 첫 숫자를 넣고 연산 시작
            self.first_num = float(current_val_str)
            self.formula = f"{self.format_result(self.first_num)} {op} "

        self.operator = op
        self.wait_for_next_num = True
        self.history_display.setText(self.formula)

    def calculate(self, n1, n2, op):
        if op == '+': return n1 + n2
        elif op == '-': return n1 - n2
        elif op == '×': return n1 * n2
        elif op == '÷': return n1 / n2 if n2 != 0 else "Error"
        return n2

    def equal(self):
        if self.first_num is not None and self.operator is not None:
            second_num = float(self.display.text())
            result = self.calculate(self.first_num, second_num, self.operator)
            full_formula = f"{self.formula}{self.format_result(second_num)} = {self.format_result(result)}"
            self.history_display.setText(full_formula)
            self.display.setText(self.format_result(result))

            # 계산 완료 후 상태를 초기화하되, 화면의 결과값은 그대로 유지
            self.first_num = None
            self.operator = None
            self.wait_for_next_num = True
            self.formula = "" 

    def reset(self):
        self.display.setText('0')
        self.history_display.setText('')
        self.formula = ""
        self.first_num = None
        self.operator = None
        self.wait_for_next_num = False

    def negative_positive(self):
        txt = self.display.text()
        if txt == '0' or txt == '0.': return
        self.display.setText(txt[1:] if txt.startswith('-') else '-' + txt)

    def percent(self):
        val = float(self.display.text()) / 100
        self.display.setText(self.format_result(val))

    def format_result(self, result):
        if isinstance(result, str): return result
        res = round(result, 6)
        return str(int(res)) if res.is_integer() else str(res)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    calc = Calculator()
    calc.show()
    sys.exit(app.exec_())