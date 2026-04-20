# calculator.py
import sys
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QGridLayout, QPushButton, QLineEdit, QSizePolicy
from PyQt5.QtCore import Qt

class Calculator(QWidget):
    def __init__(self):
        super().__init__()
        # 계산을 위한 상태 변수들
        self.first_num = None
        self.operator = None
        self.wait_for_next_num = False
        self.initUI()

    def initUI(self):
        # 윈도우 기본 설정
        self.setWindowTitle('Calculator')
        self.resize(350, 500)
        self.setStyleSheet("background-color: #1c1c1e;") # 다크 테마 배경

        # 전체 수직 레이아웃 (디스플레이 영역 + 버튼 영역)
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(20, 20, 20, 20)

        # 1. 디스플레이 화면 (출력 형태)
        self.display = QLineEdit('0') # 예시 데이터
        self.display.setReadOnly(True) # 읽기 전용 (버튼으로만 입력 가능)
        self.display.setAlignment(Qt.AlignRight) # 우측 정렬
        # 아이폰 스타일의 큰 폰트와 테두리 없는 디자인
        self.display.setStyleSheet("""
            QLineEdit {
                font-size: 60px;
                background-color: #1c1c1e;
                color: white;
                border: none;
            }
        """)
        self.display.setFixedHeight(100)
        main_layout.addWidget(self.display)

        # 2. 버튼 영역 (그리드 레이아웃)
        grid_layout = QGridLayout()
        grid_layout.setSpacing(10) # 버튼 사이의 간격

        # 아이폰 계산기와 동일한 버튼 배치도
        # 튜플 형태: (버튼 텍스트, 행(row), 열(col), [row_span], [col_span])
        buttons = [
            ('AC', 0, 0), ('+/-', 0, 1), ('%', 0, 2), ('÷', 0, 3),
            ('7', 1, 0), ('8', 1, 1), ('9', 1, 2), ('×', 1, 3),
            ('4', 2, 0), ('5', 2, 1), ('6', 2, 2), ('-', 2, 3),
            ('1', 3, 0), ('2', 3, 1), ('3', 3, 2), ('+', 3, 3),
            ('0', 4, 0, 1, 2), ('.', 4, 2), ('=', 4, 3) # '0' 버튼은 2칸을 차지함 (col_span=2)
        ]

        # 반복문을 통한 버튼 생성 및 레이아웃 배치
        for btn in buttons:
            text = btn[0]
            button = QPushButton(text)
            
            # 창 크기에 맞춰 버튼 크기가 유동적으로 변하도록 설정
            button.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
            
            # 버튼 스타일링 (기본 숫자 버튼과 우측 연산자 버튼 색상 구분)
            if text in ['÷', '×', '-', '+', '=']:
                button.setStyleSheet("font-size: 24px; background-color: #f99f00; color: white; border-radius: 30px;")
            elif text in ['AC', '+/-', '%']:
                button.setStyleSheet("font-size: 20px; background-color: #a5a5a5; color: black; border-radius: 30px;")
            else:
                button.setStyleSheet("font-size: 28px; background-color: #333333; color: white; border-radius: 30px;")

            # 버튼 클릭 이벤트 연결
            button.clicked.connect(self.button_clicked)

            # 그리드 레이아웃에 추가 ('0' 버튼처럼 span이 있는 경우와 없는 경우 분기)
            if len(btn) == 3:
                grid_layout.addWidget(button, btn[1], btn[2])
            else:
                grid_layout.addWidget(button, btn[1], btn[2], btn[3], btn[4])

        main_layout.addLayout(grid_layout)
        self.setLayout(main_layout)

    # 3. 이벤트 처리 (버튼을 누를 때마다 숫자가 입력되는 기능)
    def button_clicked(self):
        button = self.sender()
        key = button.text()
        current_text = self.display.text()

        # 숫자 버튼 처리
        if key.isdigit() or key == '.':
            if self.wait_for_next_num:
                self.display.setText(key)
                self.wait_for_next_num = False
            else:
                if key == '.' and '.' in current_text:
                    return
                if current_text == '0' and key != '.':
                    self.display.setText(key)
                else:
                    self.display.setText(current_text + key)

        # 초기화 버튼
        elif key == 'AC':
            self.display.setText('0')
            self.first_num = None
            self.operator = None
            self.wait_for_next_num = False

        # 부호 변경
        elif key == '+/-':
            val = float(current_text)
            self.display.setText(str(int(-val) if val.is_integer() else -val))

        # 퍼센트
        elif key == '%':
            val = float(current_text) / 100
            self.display.setText(str(val))

        # 연산자 버튼 (+, -, ×, ÷)
        elif key in ['+', '-', '×', '÷']:
            self.first_num = float(current_text)
            self.operator = key
            self.wait_for_next_num = True

        # 결과 버튼 (=)
        elif key == '=':
            if self.first_num is not None and self.operator is not None:
                second_num = float(current_text)
                if self.operator == '+':
                    result = self.first_num + second_num
                elif self.operator == '-':
                    result = self.first_num - second_num
                elif self.operator == '×':
                    result = self.first_num * second_num
                elif self.operator == '÷':
                    if second_num == 0:
                        self.display.setText('Error')
                        return
                    result = self.first_num / second_num
                
                # 결과값이 정수면 .0 제거
                self.display.setText(str(int(result) if result.is_integer() else round(result, 8)))
                self.first_num = None
                self.operator = None

if __name__ == '__main__':
    app = QApplication(sys.argv)
    calc = Calculator()
    calc.show()
    sys.exit(app.exec_())