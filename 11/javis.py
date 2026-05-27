# javis.py
import csv
import os
import msvcrt
import sounddevice as sd
import soundfile as sf
import speech_recognition as sr
import struct
import sys
import wave
from datetime import datetime

# ========================================================
# [1] 마이크 음성 녹음 기능
# ========================================================
def record_audio(duration = 5, sample_rate = 44100):
    current_dir = os.path.dirname(os.path.abspath(__file__))
    save_dir = os.path.join(current_dir, 'records')
    
    if not os.path.exists(save_dir):
        try:
            os.makedirs(save_dir)
            print(f"[시스템] 음성 저장용 '{save_dir}' 폴더가 생성되었습니다.")
        except Exception as e:
            print(f'[오류] 폴더 생성에 실패했습니다: {e}')
            return

    now = datetime.now()
    filename = now.strftime('%Y%m%d-%H%M%S') + '.wav'
    filepath = os.path.join(save_dir, filename)

    print('\n' + '=' * 50)
    print('[녹음 시스템] 마이크가 활성화되었습니다.')
    print(f'시작 - 지금부터 {duration}초 동안 음성을 녹음합니다. 말씀해 주세요...')
    print('=' * 50)
    sys.stdout.flush()
    
    try:
        recording = sd.rec(int(duration * sample_rate), samplerate = sample_rate, channels = 1)
        sd.wait() 

        print('\n[시스템] 녹음이 완료되었습니다. 디스크에 저장 중입니다...')
        sf.write(filepath, recording, sample_rate)
        
        print('[성공] 음성 파일이 성공적으로 저장되었습니다.')
        print(f'저장 경로: {filepath}')
        print('=' * 50)
        
    except Exception as e:
        print(f'\n[오류] 녹음 중 문제가 발생했습니다. 마이크 연결을 확인해 주세요.\n상세 에러: {e}')

# ========================================================
# [2] 전체 녹음 파일 목록 출력 기능
# ========================================================
def show_all_records():
    '''
    records 폴더에 저장된 모든 .wav 파일의 목록을 출력합니다.
    '''
    current_dir = os.path.dirname(os.path.abspath(__file__))
    save_dir = os.path.join(current_dir, 'records')
    
    print('\n' + '=' * 50)
    print('[목록 시스템] 전체 녹음 파일 목록을 불러옵니다.')
    print('=' * 50)
    sys.stdout.flush()
    
    if not os.path.exists(save_dir):
        print(f"[안내] '{save_dir}' 폴더가 존재하지 않습니다. 아직 녹음된 파일이 없습니다.")
        print('=' * 50)
        return
        
    try:
        file_list = os.listdir(save_dir)
        found_files = []
        
        # .wav 파일만 필터링하여 크기 정보와 함께 수집
        for filename in file_list:
            if filename.endswith('.wav'):
                full_path = os.path.join(save_dir, filename)
                file_size = os.path.getsize(full_path) / 1024
                found_files.append((filename, file_size))
                
        if found_files:
            found_files.sort() # 이름순(시간순) 정렬
            print(f'[안내] 총 {len(found_files)}개의 파일이 저장되어 있습니다:\n')
            for idx, (name, size) in enumerate(found_files, 1):
                print(f' [{idx}] {name} ({size:.1f} KB)')
        else:
            print('[안내] 폴더는 존재하지만 저장된 녹음(.wav) 파일이 없습니다.')
            
    except Exception as e:
        print(f'[오류] 파일 시스템을 읽어오는 중 예상치 못한 에러가 발생했습니다: {e}')
        
    print('=' * 50)

# ========================================================
# [3] 특정 범위 날짜의 녹음 파일 검색 기능
# ========================================================
def show_records_by_date(start_date_str, end_date_str):
    current_dir = os.path.dirname(os.path.abspath(__file__))
    save_dir = os.path.join(current_dir, 'records')
    
    print('\n' + '=' * 50)
    print('[검색 시스템] 범위 내의 녹음 파일을 탐색합니다.')
    print(f'검색 범위: {start_date_str} ~ {end_date_str}')
    print('=' * 50)
    sys.stdout.flush()
    
    if not os.path.exists(save_dir):
        print(f"[안내] '{save_dir}' 폴더가 존재하지 않아 검색할 파일이 없습니다.")
        print('=' * 50)
        return []
        
    try:
        start_date = int(start_date_str)
        end_date = int(end_date_str)
    except ValueError:
        print("[오류] 날짜 형식은 반드시 '20260501'과 같은 8자리 숫자 형태여야 합니다.")
        print('=' * 50)
        return []

    found_files = []
    
    try:
        file_list = os.listdir(save_dir)
        
        for filename in file_list:
            if filename.endswith('.wav') and '-' in filename:
                try:
                    file_date_part = filename.split('-')[0]
                    file_date = int(file_date_part)
                    
                    if start_date <= file_date <= end_date:
                        full_path = os.path.join(save_dir, filename)
                        file_size = os.path.getsize(full_path) / 1024
                        found_files.append((filename, file_size))
                except (ValueError, IndexError):
                    pass

        if found_files:
            found_files.sort()
            print(f'[일치 항목 발견] 총 {len(found_files)}개의 파일이 조건에 부합합니다:\n')
            for idx, (name, size) in enumerate(found_files, 1):
                print(f' [{idx}] {name} ({size:.1f} KB)')
        else:
            print('[안내] 지정된 범위 내에 일치하는 녹음 파일이 존재하지 않습니다.')
            
    except Exception as e:
        print(f'[오류] 파일 시스템을 읽어오는 중 예상치 못한 에러가 발생했습니다: {e}')
        
    print('=' * 50)
    return found_files

# ========================================================
# [4] STT 변환 및 CSV 저장 기능
# ========================================================
def convert_audio_to_text():
    '''
    records 폴더에 저장된 모든 .wav 파일에 대해 STT(Speech to Text)를 수행하고
    결과를 csv_results 폴더에 같은 이름의 .CSV 파일로 분리하여 저장합니다.
    이미 변환된 결과 파일이 있는 경우 변환 작업을 건너뜁니다.
    '''
    current_dir = os.path.dirname(os.path.abspath(__file__))
    save_dir = os.path.join(current_dir, 'records')
    csv_dir = os.path.join(current_dir, 'csv_results')

    print('\n' + '=' * 50)
    print('[STT 시스템] 음성 파일 분석 및 텍스트 변환을 시작합니다.')
    print('=' * 50)
    sys.stdout.flush()

    if not os.path.exists(save_dir):
        print(f"[안내] '{save_dir}' 폴더가 존재하지 않아 변환할 음성 파일이 없습니다.")
        print('=' * 50)
        return

    # CSV 저장용 디렉토리 자동 생성
    if not os.path.exists(csv_dir):
        try:
            os.makedirs(csv_dir)
            print(f"[시스템] CSV 저장용 '{csv_dir}' 폴더가 생성되었습니다.")
        except Exception as e:
            print(f'[오류] 폴더 생성에 실패했습니다: {e}')
            print('=' * 50)
            return

    try:
        file_list = os.listdir(save_dir)
        wav_files = [f for f in file_list if f.endswith('.wav')]

        if not wav_files:
            print('[안내] 변환할 .wav 음성 파일이 records 폴더 내에 존재하지 않습니다.')
            print('=' * 50)
            return

        recognizer = sr.Recognizer()
        success_count = 0
        skip_count = 0

        for wav_name in sorted(wav_files):
            wav_path = os.path.join(save_dir, wav_name)
            csv_name = wav_name.rsplit('.', 1)[0] + '.CSV'
            csv_path = os.path.join(csv_dir, csv_name)

            # 이미 변환이 완료된 파일인지 검증 (건너뛰기 로직)
            if os.path.exists(csv_path):
                print(f'건너뛰기: {wav_name} (이미 변환된 CSV 결과가 존재합니다)')
                skip_count = skip_count + 1
                continue

            print(f'분석 중: {wav_name}')
            sys.stdout.flush()

            # 음성 파일 총 재생 시간 및 실제 발화 시작 시점 계산 (wave 및 struct 모듈 사용)
            duration_sec = 0.0
            start_time_sec = 0.0
            try:
                with wave.open(wav_path, 'rb') as wave_file:
                    num_channels = wave_file.getnchannels()
                    sample_width = wave_file.getsampwidth()
                    sample_rate = wave_file.getframerate()
                    frames = wave_file.getnframes()
                    duration_sec = frames / float(sample_rate)

                    # 16-bit PCM 포맷인 경우에만 정밀 진폭 분석 수행
                    if sample_width == 2:
                        raw_data = wave_file.readframes(frames)
                        num_samples = frames * num_channels
                        fmt = f'{num_samples}h'
                        samples = struct.unpack(fmt, raw_data)

                        # 0.1초(100ms) 단위 청크로 분할하여 노이즈 임계값을 초과하는 최초 시점 스캔
                        chunk_size = int(sample_rate * 0.1)
                        threshold = 1000  # 음성 감지 임계값

                        for chunk_idx in range(0, frames, chunk_size):
                            start_frame = chunk_idx
                            end_frame = min(chunk_idx + chunk_size, frames)

                            max_val = 0
                            for f_idx in range(start_frame, end_frame):
                                sample_idx = f_idx * num_channels
                                if sample_idx < len(samples):
                                    val = abs(samples[sample_idx])
                                    if val > max_val:
                                        max_val = val

                            # 잡음 차단 레벨을 초과한 경우 최초 발화 시점으로 판정
                            if max_val > threshold:
                                start_time_sec = start_frame / float(sample_rate)
                                start_time_sec = round(start_time_sec, 1)
                                break
            except Exception as e:
                print(f'  [경고] 음성 파일 재생 시간 및 발화 시작 시간 분석 실패: {e}')

            # STT 변환 진행
            recognized_text = ''
            try:
                with sr.AudioFile(wav_path) as source:
                    audio_data = recognizer.record(source)
                
                # Google Web Speech API로 한국어 인식 수행
                recognized_text = recognizer.recognize_google(audio_data, language = 'ko-KR')
                print(f'  [인식 완료] {recognized_text}')
            except sr.UnknownValueError:
                recognized_text = '(인식 실패: 음성을 이해할 수 없음)'
                print('  [안내] 음성을 텍스트로 변환하는 데 실패했습니다. (알 수 없는 발음)')
            except sr.RequestError as e:
                recognized_text = f'(인식 실패: API 요청 오류 - {e})'
                print(f'  [오류] STT 서비스 요청 오류: {e}')
            except Exception as e:
                recognized_text = f'(인식 실패: {e})'
                print(f'  [오류] 변환 도중 예상치 못한 오류 발생: {e}')

            # CSV 파일로 저장
            try:
                # UTF-8 with BOM 인코딩을 사용하여 엑셀 등 한글 호환성 보장
                with open(csv_path, 'w', encoding = 'utf-8-sig', newline = '') as f:
                    # CSV 형식: 시간,인식된 텍스트
                    f.write('시간,인식된 텍스트\n')
                    f.write(f'{start_time_sec:.1f},{recognized_text}\n')
                
                print(f'  [저장 완료] CSV 저장 경로: {csv_path}')
                success_count = success_count + 1
            except Exception as e:
                print(f'  [오류] CSV 파일 저장 실패: {e}')

        total_processed = success_count + skip_count
        print(f'\n[안내] 총 {len(wav_files)}개 파일 분석 완료:')
        print(f'  - 신규 변환 완료: {success_count}개')
        print(f'  - 건너뜀 (이미 존재): {skip_count}개')

    except Exception as e:
        print(f'[오류] 변환 과정 중 치명적인 에러가 발생했습니다: {e}')

    print('=' * 50)

# ========================================================
# [5] 보너스 과제: 특정 키워드 검색 기능
# ========================================================
def search_keyword_in_csv():
    '''
    csv_results 폴더에 저장된 모든 .CSV 파일 안에서 사용자가 입력한 특정 키워드를 검색하여
    일치하는 파일 정보와 인식된 텍스트 내용을 출력합니다.
    '''
    current_dir = os.path.dirname(os.path.abspath(__file__))
    csv_dir = os.path.join(current_dir, 'csv_results')

    print('\n' + '=' * 50)
    print('[키워드 검색 시스템] CSV 결과 파일 내 키워드 탐색을 시작합니다.')
    print('=' * 50)
    sys.stdout.flush()

    if not os.path.exists(csv_dir):
        print(f"[안내] '{csv_dir}' 폴더가 존재하지 않아 검색할 CSV 파일이 없습니다. 먼저 STT 변환을 진행해 주세요.")
        print('=' * 50)
        return

    keyword = input('검색할 키워드를 입력하세요: ').strip()

    if not keyword:
        print('[경고] 키워드가 입력되지 않았습니다. 검색을 취소합니다.')
        print('=' * 50)
        return

    try:
        file_list = os.listdir(csv_dir)
        csv_files = [f for f in file_list if f.upper().endswith('.CSV')]

        if not csv_files:
            print('[안내] 검색 대상인 .CSV 결과 파일이 존재하지 않습니다. 먼저 STT 변환을 진행해 주세요.')
            print('=' * 50)
            return

        found_count = 0
        print(f"검색 결과 (키워드: '{keyword}'):\n")

        for csv_name in sorted(csv_files):
            csv_path = os.path.join(csv_dir, csv_name)
            
            try:
                with open(csv_path, 'r', encoding = 'utf-8-sig') as f:
                    csv_reader = csv.reader(f)
                    try:
                        header = next(csv_reader)
                    except StopIteration:
                        continue

                    for row in csv_reader:
                        if len(row) >= 2:
                            time_info = row[0]
                            text_content = row[1]

                            # 대소문자 구분 없이 키워드 매칭
                            if keyword.lower() in text_content.lower():
                                print(f' 파일명: {csv_name}')
                                print(f' 시간: {time_info}초')
                                print(f' 내용: {text_content}')
                                print('-' * 40)
                                found_count = found_count + 1
            except Exception as e:
                print(f' [오류] {csv_name} 파일을 읽는 중 에러 발생: {e}')

        if found_count > 0:
            print(f'[검색 완료] 총 {found_count}개의 일치하는 항목을 발견했습니다.')
        else:
            print(f"[안내] 키워드 '{keyword}'가 포함된 기록을 찾지 못했습니다.")

    except Exception as e:
        print(f'[오류] 검색 과정 중 예상치 못한 에러가 발생했습니다: {e}')

    print('=' * 50)

# ========================================================
# [6] 메인 메뉴 뒤로가기 대기 제어 기능 (신규 추가)
# ========================================================
def wait_for_back():
    '''
    사용자가 Enter 또는 ESC 키를 누를 때까지 화면을 대기시킵니다.
    입력이 완료되면 메인 메뉴로 돌아갑니다.
    '''
    print('\n' + '-' * 40)
    print('[안내] 메인 메뉴로 돌아가려면 Enter 또는 ESC 키를 누르세요...')
    sys.stdout.flush()

    while True:
        if msvcrt.kbhit():
            key = msvcrt.getch()
            # ESC 키 (b'\x1b') 또는 Enter 키 (b'\r' 또는 b'\n') 감지
            if key in (b'\x1b', b'\r', b'\n'):
                break

# ========================================================
# 메인 실행부 (인터랙티브 메뉴 무한 루프 구현)
# ========================================================
if __name__ == '__main__':
    try:
        while True:
            os.system('cls')
            print('\n' + '=' * 40)
            print('  J.A.V.I.S 제어 터미널  ')
            print('=' * 40)
            print(' 1. 새로운 음성 녹음 시작 (5초)')
            print(' 2. 전체 녹음 파일 목록 보기')
            print(' 3. 특정 날짜 범위 내 녹음 파일 검색')
            print(' 4. 음성 파일 STT 변환 및 CSV 저장 (분리 및 스킵 적용)')
            print(' 5. [보너스] CSV 내 키워드 검색 (csv_results 탐색)')
            print(' 0. 프로그램 제어 시스템 종료')
            print('=' * 40)
            sys.stdout.flush()
            
            user_choice = input('실행할 작업 번호를 입력하세요 (종료는 0): ').strip()
            
            if user_choice == '1':
                os.system('cls')
                record_audio(duration = 5)
                wait_for_back()
            elif user_choice == '2':
                os.system('cls')
                show_all_records()
                wait_for_back()
            elif user_choice == '3':
                os.system('cls')
                start_input = input('시작 날짜 입력 (예: 20260501): ').strip()
                end_input = input('종료 날짜 입력 (예: 20260522): ').strip()
                os.system('cls')
                show_records_by_date(start_input, end_input)
                wait_for_back()
            elif user_choice == '4':
                os.system('cls')
                convert_audio_to_text()
                wait_for_back()
            elif user_choice == '5':
                os.system('cls')
                search_keyword_in_csv()
                wait_for_back()
            elif user_choice == '0':
                print('\n[시스템] J.A.V.I.S 제어 시스템을 종료합니다.')
                print('=' * 40)
                break
            else:
                print('\n[경고] 메뉴에 없는 번호입니다. 다시 입력해 주세요.')
                
    except KeyboardInterrupt:
        print('\n\n[시스템] 사용자에 의해 제어 시스템이 강제 종료되었습니다. 프로그램을 마칩니다.')
        print('=' * 40)
