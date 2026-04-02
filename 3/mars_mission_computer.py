# mars_mission_computer.py
import random
import datetime

class DummySensor:
    def __init__(self):
        # 각 센서의 현재 값(value), 최소/최대 범위, 반올림 자릿수, 단위를 하나의 딕셔너리로 묶음
        self.env_data = {
            'mars_base_internal_temperature': {'value': 0.0, 'min': 18.0, 'max': 30.0, 'round': 2, 'unit': '°C'},
            'mars_base_external_temperature': {'value': 0.0, 'min': 0.0,  'max': 21.0, 'round': 2, 'unit': '°C'},
            'mars_base_internal_humidity':    {'value': 0.0, 'min': 50.0, 'max': 60.0, 'round': 2, 'unit': '%'},
            'mars_base_external_illuminance': {'value': 0.0, 'min': 500.0,'max': 715.0,'round': 2, 'unit': 'W/m²'},
            'mars_base_internal_co2':         {'value': 0.0, 'min': 0.02, 'max': 0.1,  'round': 4, 'unit': '%'},
            'mars_base_internal_oxygen':      {'value': 0.0, 'min': 4.0,  'max': 7.0,  'round': 2, 'unit': '%'}
        }

    def set_env(self):
        # 딕셔너리를 순회하면서 설정된 min, max 값을 읽어 자동으로 랜덤 값을 생성 및 할당
        for sensor_key, meta in self.env_data.items():
            random_val = random.uniform(meta['min'], meta['max'])
            meta['value'] = round(random_val, meta['round'])

    def get_env(self):
        now = datetime.datetime.now()
        current_time = now.strftime('%Y-%m-%d %H:%M:%S')

        # CSV 로깅을 위해 순수 값(value)만 뽑아내기
        # 딕셔너리에서 'value' 키의 값만 순서대로 리스트에 담습니다.
        values_only = [str(meta['value']) for meta in self.env_data.values()]
        
        # 리스트의 값들을 쉼표로 연결하고 맨 앞에 시간을 붙임
        log_line = current_time + ',' + ','.join(values_only) + '\n'
        log_file_name = 'mars_env_sensor.log'
        
        # 헤더 자동 생성 (딕셔너리의 키 값들을 활용)
        headers = ['datetime'] + list(self.env_data.keys())
        header_line = ','.join(headers) + '\n'

        # 파일에 로그 남기기
        is_new_file = False
        try:
            with open(log_file_name, 'r', encoding='utf-8') as check_file:
                pass
        except FileNotFoundError:
            is_new_file = True

        try:
            with open(log_file_name, 'a', encoding='utf-8') as log_file:
                if is_new_file:
                    log_file.write(header_line)
                log_file.write(log_line)
        except Exception as e:
            print(f'로그 파일 저장 중 예외 발생: {e}')

        # 반환할 때 외부에서 쓰기 편하도록 전체 메타데이터 딕셔너리를 그대로 반환
        return self.env_data

if __name__ == '__main__':
    ds = DummySensor()
    ds.set_env()
    current_environment = ds.get_env()
    
    print('--- 화성 기지 더미 센서 측정 데이터 ---')
    for sensor_name, meta in current_environment.items():
        print(f"{sensor_name}: {meta['value']} {meta['unit']}")
        
    print('\n[시스템 안내] 위 측정 데이터가 환경 로그 파일에 안전하게 기록되었습니다.')