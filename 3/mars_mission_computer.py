# mars_mission_computer.py
import random
import datetime

class DummySensor:
    def __init__(self):
        # 센서 데이터를 담을 사전(Dictionary) 객체 초기화
        self.env_values = {
            'mars_base_internal_temperature': 0.0,
            'mars_base_external_temperature': 0.0,
            'mars_base_internal_humidity': 0.0,
            'mars_base_external_illuminance': 0.0,
            'mars_base_internal_co2': 0.0,
            'mars_base_internal_oxygen': 0.0
        }

    def set_env(self):
        # random.uniform()을 사용하여 범위 안의 랜덤한 실수 값을 생성 및 소수점 반올림
        self.env_values['mars_base_internal_temperature'] = round(random.uniform(18.0, 30.0), 2)
        self.env_values['mars_base_external_temperature'] = round(random.uniform(0.0, 21.0), 2)
        self.env_values['mars_base_internal_humidity'] = round(random.uniform(50.0, 60.0), 2)
        self.env_values['mars_base_external_illuminance'] = round(random.uniform(500.0, 715.0), 2)
        self.env_values['mars_base_internal_co2'] = round(random.uniform(0.02, 0.1), 4)
        self.env_values['mars_base_internal_oxygen'] = round(random.uniform(4.0, 7.0), 2)

    def get_env(self):
        # 1. 현재 날짜와 시간 구하기
        now = datetime.datetime.now()
        current_time = now.strftime('%Y-%m-%d %H:%M:%S')

        # 2. 작은따옴표 규칙을 깔끔하게 유지하기 위해 값을 변수에 할당
        in_temp = self.env_values['mars_base_internal_temperature']
        out_temp = self.env_values['mars_base_external_temperature']
        in_hum = self.env_values['mars_base_internal_humidity']
        out_ill = self.env_values['mars_base_external_illuminance']
        in_co2 = self.env_values['mars_base_internal_co2']
        in_oxy = self.env_values['mars_base_internal_oxygen']

        # 3. 보너스 과제 요구사항에 맞춘 로그 문자열 생성 (쉼표로 구분)
        log_line = f'{current_time},{in_temp},{out_temp},{in_hum},{out_ill},{in_co2},{in_oxy}\n'
        log_file_name = 'mars_env_sensor.log'
        header = 'datetime,internal_temperature,external_temperature,internal_humidity,external_illuminance,internal_co2,internal_oxygen\n'

        # 4. 파일에 로그 남기기 (예외 처리 필수)
        is_new_file = False
        try:
            # 일단 읽기 모드('r')로 열어봅니다.
            with open(log_file_name, 'r', encoding='utf-8') as check_file:
                pass
        except FileNotFoundError:
            # 파일이 없어서 에러가 발생하면, 이번이 처음 만드는 파일임을 알 수 있습니다.
            is_new_file = True

        try:
            # 기존 데이터를 지우지 않고 누적하기 위해 추가 모드('a') 사용
            with open(log_file_name, 'a', encoding='utf-8') as log_file:
                # 처음 만드는 파일(새 파일)일 경우에만 헤더를 먼저 씁니다.
                if is_new_file:
                    log_file.write(header)

                log_file.write(log_line)
                
        except PermissionError:
            print(f"[권한 오류] '{log_file_name}' 파일에 로그를 기록할 권한이 없습니다.")
        except Exception as e:
            print(f'로그 파일 저장 중 알 수 없는 예외 발생: {e}')

        # 기존 기능 유지: env_values 반환
        return self.env_values

if __name__ == '__main__':
    # 1. 인스턴스화
    ds = DummySensor()
    
    # 2. 값 세팅
    ds.set_env()
    
    # 3. 값 가져오기 (동시에 로그 파일에 자동 기록됨)
    current_environment = ds.get_env()
    
    # 4. 화면 출력 확인
    print('--- 화성 기지 더미 센서 측정 데이터 ---')
    for sensor_name, sensor_value in current_environment.items():
        print(f'{sensor_name}: {sensor_value}')
        
    print('\n[시스템 안내] 위 측정 데이터가 환경 로그 파일에 안전하게 기록되었습니다.')