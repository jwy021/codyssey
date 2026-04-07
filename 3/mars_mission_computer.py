# mars_mission_computer.py
import random
import datetime
import time
import json

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
        # sensor_key 미사용 경고를 없애기 위해 .values()를 사용하여 값(meta)만 바로 꺼냄
        for meta in self.env_data.values():
            random_val = random.uniform(meta['min'], meta['max'])
            meta['value'] = round(random_val, meta['round'])

    def get_env(self):
        now = datetime.datetime.now()
        current_time = now.strftime('%Y-%m-%d %H:%M:%S')

        # CSV 로깅을 위해 순수 값(value)만 뽑아내기
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


class MissionComputer:
    def __init__(self):
        # 1. DummySensor 인스턴스화
        self.ds = DummySensor()
        self.env_values = {}
        # 5분 평균 계산을 위한 데이터 저장용 리스트 (History)
        self.history = {key: [] for key in self.ds.env_data.keys()}
        # 마지막 평균 출력 시간 기록
        self.last_average_time = time.time()

    def get_sensor_data(self):
        print('[시스템 안내] 화성 기지 미션 컴퓨터 가동을 시작합니다. (종료: Ctrl+C)\n')
        
        # 3. 5초에 한 번씩 반복하는 루프
        while True:
            try:
                # 3-1. 센서의 값을 갱신하고 가져오기
                self.ds.set_env()
                sensor_data = self.ds.get_env()
                
                # 센서에서 가져온 중첩 딕셔너리에서 순수 숫자('value')만 추출하여 미션 컴퓨터에 복사
                self.env_values = {key: meta['value'] for key, meta in sensor_data.items()}
                for key, value in self.env_values.items():
                    self.history[key].append(value)

                # 3-2. env_values의 값을 JSON 형태로 화면에 출력 (들여쓰기 4칸 적용)
                json_output = json.dumps(self.env_values, indent=4)
                
                current_time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                print(f'--- 측정 시간: {current_time} ---')
                print(json_output)
                print('-' * 45)

                # 3. 5분(300초) 마다 평균값 계산 및 출력
                elapsed_time = time.time() - self.last_average_time
                if elapsed_time >= 300:
                    print('\n' + '=' * 20 + ' 5분 평균 리포트 ' + '=' * 20)
                    avg_results = {}
                    for key, values in self.history.items():
                        if values:
                            average = sum(values) / len(values)
                            # 원본 데이터의 반올림 설정을 참고하여 평균값 정리
                            round_digit = self.ds.env_data[key]['round']
                            avg_results[key] = round(average, round_digit)
                            # 평균 출력 후 다음 주기를 위해 히스토리 초기화
                            self.history[key] = []
                    
                    print(json.dumps(avg_results, indent=4))
                    print('=' * 54 + '\n')
                    self.last_average_time = time.time()

                # 3-3. 5초 대기
                time.sleep(5)

            # 사용자가 강제 종료(Ctrl+C) 시 안전하게 빠져나가는 예외 처리
            except KeyboardInterrupt:
                print('\n' + '-' * 30)
                print('System stopped....')
                print('-' * 30)
                break
            except Exception as e:
                print(f'\n[오류] 데이터 수집 중 시스템 에러 발생: {e}')
                time.sleep(5)


if __name__ == '__main__':
    # MissionComputer 클래스를 RunComputer 라는 이름으로 인스턴스화
    RunComputer = MissionComputer()
    
    # get_sensor_data() 메소드를 호출해서 지속적으로 환경 값 출력
    RunComputer.get_sensor_data()