# mars_mission_computer.py
import random
import datetime
import time
import json
import platform
import os
import subprocess
import re

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

        # 설정 파일을 불러오는 초기화 작업
        self.display_settings = {}
        self.load_settings()

    # setting.txt 파일을 읽고 관리하는 메서드
    def load_settings(self):
        setting_file = 'setting.txt'
        
        # 파일이 없으면 모든 항목을 True로 설정한 기본 파일을 자동 생성
        if not os.path.exists(setting_file):
            try:
                with open(setting_file, 'w', encoding='utf-8') as f:
                    # 환경 센서 항목
                    for key in self.ds.env_data.keys():
                        f.write(f'{key}=True\n')
                    # 시스템 사양(Info) 항목
                    f.write('info_os_system=True\n')
                    f.write('info_os_version=True\n')
                    f.write('info_cpu_type=True\n')
                    f.write('info_cpu_cores=True\n')
                    f.write('info_memory_total=True\n')
                    # 실시간 부하(Load) 항목
                    f.write('load_cpu_usage=True\n')
                    f.write('load_mem_usage=True\n')
                print(f'[시스템 안내] 기본 설정 파일({setting_file})이 생성되었습니다.')
            except Exception as e:
                print(f'[경고] 설정 파일 생성 실패: {e}')
                
        # 파일에서 설정을 읽어 딕셔너리에 저장
        try:
            with open(setting_file, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    if line and '=' in line:
                        key, val = line.split('=')
                        # 'True' 문자열이면 파이썬의 True 불리언(Boolean) 값으로 변환
                        self.display_settings[key.strip()] = (val.strip().lower() == 'true')
        except Exception as e:
            print(f'[경고] 설정 파일 읽기 실패. 기본값으로 동작합니다: {e}')
            for key in self.ds.env_data.keys():
                self.display_settings[key] = True

    def get_sensor_data(self):
        print('[시스템 안내] 화성 기지 미션 컴퓨터 가동을 시작합니다. (종료: Ctrl+C)\n')
        
        # 5초에 한 번씩 반복하는 루프
        while True:
            try:
                # 센서의 값을 갱신하고 가져오기
                self.ds.set_env()
                sensor_data = self.ds.get_env()
                
                # 센서에서 가져온 중첩 딕셔너리에서 순수 숫자('value')만 추출하여 미션 컴퓨터에 복사
                self.env_values = {key: meta['value'] for key, meta in sensor_data.items()}
                for key, value in self.env_values.items():
                    self.history[key].append(value)

                # 설정(setting.txt)에서 True로 되어있는 항목만 골라서 화면에 출력할 딕셔너리 생성
                filtered_realtime = {
                    key: value 
                    for key, value in self.env_values.items() 
                    if self.display_settings.get(key, True)
                }


                if filtered_realtime:
                    # filtered_realtime의 값을 JSON 형태로 화면에 출력 (들여쓰기 4칸 적용)
                    json_output = json.dumps(filtered_realtime, indent=4)
                    
                    current_time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                    print(f'--- 측정 시간: {current_time} ---')
                    print(json_output)
                    print('-' * 45)

                # 5분(300초) 마다 평균값 계산 및 출력
                elapsed_time = time.time() - self.last_average_time
                if elapsed_time >= 300:
                    print('\n' + '=' * 20 + ' 5분 평균 리포트 ' + '=' * 20)
                    avg_results = {
                        key: round(sum(vals)/len(vals), self.ds.env_data[key]['round'])
                        for key, vals in self.history.items() 
                        if vals and self.display_settings.get(key, True)
                    }
                    if avg_results:
                        print(json.dumps(avg_results, indent=4))
                    
                    for key in self.history: self.history[key] = []
                    print('=' * 54 + '\n')
                    self.last_average_time = time.time()

                # 5초 대기
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

    def get_mission_computer_info(self):
        try:
            sys_os = platform.system()
            mem_bytes = 0
            
            # 외부 라이브러리 없이 운영체제별 터미널 명령어로 직접 물리 메모리 접근
            try:
                if sys_os == 'Windows':
                    # 윈도우: powershell 명령어로 메모리 총량 추출
                    out = subprocess.check_output(['powershell', '-Command', '(Get-CimInstance Win32_ComputerSystem).TotalPhysicalMemory']).decode()
                    mem_bytes = int(out.strip())
                            
                elif sys_os == 'Linux':
                    # 리눅스: POSIX 표준인 페이지 크기 * 페이지 개수로 계산
                    mem_bytes = os.sysconf('SC_PAGE_SIZE') * os.sysconf('SC_PHYS_PAGES')
                    
                elif sys_os == 'Darwin':
                    # 맥(Mac): sysctl 명령어로 추출
                    out = subprocess.check_output(['sysctl', '-n', 'hw.memsize']).decode()
                    mem_bytes = int(out.strip())
            except Exception:
                mem_bytes = 0

            # 바이트(Bytes)를 기가바이트(GB)로 환산하여 소수점 2자리까지 표시
            if mem_bytes > 0:
                mem_gb = f'{round(mem_bytes / (1024 ** 3), 2)} GB'
            else:
                mem_gb = '측정 불가'

            # 설정에 따라 필터링된 시스템 정보 생성
            full_info = {
                '운영체계': (sys_os, 'info_os_system'),
                '운영체계_버전': (platform.version(), 'info_os_version'),
                'CPU_타입': (platform.processor(), 'info_cpu_type'),
                'CPU_코어수': (os.cpu_count(), 'info_cpu_cores'),
                '메모리_크기': (mem_gb, 'info_memory_total')
            }
            
            filtered_info = {
                label: val 
                for label, (val, config_key) in full_info.items() 
                if self.display_settings.get(config_key, True)
            }
            
            if filtered_info:
                print('\n[미션 컴퓨터 하드웨어 정보]')
                print(json.dumps(filtered_info, indent=4, ensure_ascii=False))
            return full_info
            
        except Exception as e:
            print(f'[오류] 시스템 정보 수집 실패: {e}')

    def get_mission_computer_load(self):
        sys_os = platform.system()
        cpu_usage = 0.0
        mem_usage = 0.0

        try:
            # Windows 환경
            if sys_os == 'Windows':
                # CPU 부하율 
                cpu_out = subprocess.check_output(['powershell', '-Command', '(Get-CimInstance Win32_Processor | Measure-Object -Property LoadPercentage -Average).Average']).decode()
                if cpu_out.strip():
                    cpu_usage = round(float(cpu_out.strip()), 1)

                # 메모리 사용량 
                mem_out = subprocess.check_output(['powershell', '-Command', '$cs=Get-CimInstance Win32_OperatingSystem; ($cs.TotalVisibleMemorySize - $cs.FreePhysicalMemory) / $cs.TotalVisibleMemorySize * 100']).decode()
                if mem_out.strip():
                    mem_usage = round(float(mem_out.strip()), 1)

            # Linux 환경 (라즈베리파이 등)
            elif sys_os == 'Linux':
                # CPU 부하율 (1분 평균 부하를 코어 수로 나누어 백분율 계산)
                load_avg = os.getloadavg()[0]
                cores = os.cpu_count()
                cpu_usage = round((load_avg / cores) * 100, 1) if cores else 0.0

                # 메모리 사용량 (free 명령어 결과 파싱)
                mem_out = subprocess.check_output("free -m | grep Mem", shell=True).decode()
                parts = mem_out.split()
                if len(parts) >= 3:
                    total_mem = float(parts[1])
                    used_mem = float(parts[2])
                    mem_usage = round((used_mem / total_mem) * 100, 1)

            # Mac(Darwin) 환경
            elif sys_os == 'Darwin':
                # CPU 부하율 (top 명령어에서 idle 값을 찾아 100에서 뺌)
                cpu_out = subprocess.check_output("top -l 1 | grep -E '^CPU'", shell=True).decode()
                idle_match = re.search(r'([0-9.]+)%\s*idle', cpu_out)
                if idle_match:
                    cpu_usage = round(100.0 - float(idle_match.group(1)), 1)
                
                # 메모리 사용량 (vm_stat 결과에서 빈 페이지 수 계산)
                mem_out = subprocess.check_output("vm_stat", shell=True).decode()
                pages_free = 0
                for line in mem_out.splitlines():
                    if 'Pages free' in line:
                        pages_free = int(re.search(r'\d+', line).group())
                
                tot_mem_out = subprocess.check_output(['sysctl', '-n', 'hw.memsize']).decode()
                total_mem_bytes = int(tot_mem_out.strip())
                free_mem_bytes = pages_free * 4096 # Mac 기본 메모리 페이지 사이즈
                mem_usage = round(((total_mem_bytes - free_mem_bytes) / total_mem_bytes) * 100, 1)

        except Exception as e:
            # 명령어 실행 실패 등 만약의 사태를 대비한 최후의 안전장치
            print(f"[경고] 시스템 부하 통신 오류: {e}")
            cpu_usage = 0.0
            mem_usage = 0.0

        # 설정에 따른 실시간 부하 필터링
        sys_load = {}
        if self.display_settings.get('load_cpu_usage', True):
            sys_load['CPU_실시간_사용량(%)'] = cpu_usage
        if self.display_settings.get('load_mem_usage', True):
            sys_load['메모리_실시간_사용량(%)'] = mem_usage
        
        if sys_load:
            print('\n[미션 컴퓨터 실시간 부하 상태]')
            print(json.dumps(sys_load, indent=4, ensure_ascii=False))
        return sys_load
        

if __name__ == '__main__':
    # 1. 요구사항에 맞춰 runComputer 라는 이름으로 인스턴스화
    runComputer = MissionComputer()
    
    print("=" * 50)
    print(" 화성 기지 미션 컴퓨터 부팅을 시작합니다...")
    print("=" * 50)

    # 2. 시스템 하드웨어 스펙 출력
    runComputer.get_mission_computer_info()
    
    # 3. 시스템 현재 부하량 출력
    runComputer.get_mission_computer_load()
    
    print('\n[시스템 안내] 하드웨어 진단 완료. 3초 후 환경 모니터링 루프로 진입합니다.')
    time.sleep(3)
    
    # 4. 무한 모니터링 루프 가동
    runComputer.get_sensor_data()