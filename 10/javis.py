# javis.py
import os
import sounddevice as sd
import soundfile as sf
import sys
from datetime import datetime

# ========================================================
# [1] 마이크 음성 녹음 기능
# ========================================================
def record_audio(duration=5, sample_rate=44100):
    save_dir = "records"
    if not os.path.exists(save_dir):
        try:
            os.makedirs(save_dir)
            print(f"[시스템] 음성 저장용 '{save_dir}' 폴더가 생성되었습니다.")
        except Exception as e:
            print(f"[오류] 폴더 생성에 실패했습니다: {e}")
            return

    now = datetime.now()
    filename = now.strftime("%Y%m%d-%H%M%S") + ".wav"
    filepath = os.path.join(save_dir, filename)

    print("\n" + "=" * 50)
    print(f"[🎙️ 자비스 시스템] 마이크가 활성화되었습니다.")
    print(f"▶ 지금부터 {duration}초 동안 음성을 녹음합니다. 말씀해 주세요...")
    print("=" * 50)
    sys.stdout.flush()
    
    try:
        recording = sd.rec(int(duration * sample_rate), samplerate=sample_rate, channels=1)
        sd.wait() 

        print("\n[시스템] 녹음이 완료되었습니다. 디스크에 저장 중입니다...")
        sf.write(filepath, recording, sample_rate)
        
        print(f"[SUCCESS] 음성 파일이 성공적으로 저장되었습니다.")
        print(f"▶ 저장 경로: {filepath}")
        print("=" * 50)
        
    except Exception as e:
        print(f"\n[오류] 녹음 중 문제가 발생했습니다. 마이크 연결을 확인해 주세요.\n상세 에러: {e}")

# ========================================================
# [2] 전체 녹음 파일 목록 출력 기능 (신규 추가)
# ========================================================
def show_all_records():
    """
    records 폴더에 저장된 모든 .wav 파일의 목록을 출력합니다.
    """
    save_dir = "records"
    
    print("\n" + "=" * 50)
    print(f"[📋 자비스 시스템] 전체 녹음 파일 목록을 불러옵니다.")
    print("=" * 50)
    sys.stdout.flush()
    
    if not os.path.exists(save_dir):
        print(f"[안내] '{save_dir}' 폴더가 존재하지 않습니다. 아직 녹음된 파일이 없습니다.")
        print("=" * 50)
        return
        
    try:
        file_list = os.listdir(save_dir)
        found_files = []
        
        # .wav 파일만 필터링하여 크기 정보와 함께 수집
        for filename in file_list:
            if filename.endswith(".wav"):
                full_path = os.path.join(save_dir, filename)
                file_size = os.path.getsize(full_path) / 1024
                found_files.append((filename, file_size))
                
        if found_files:
            found_files.sort() # 이름순(시간순) 정렬
            print(f"[안내] 총 {len(found_files)}개의 파일이 저장되어 있습니다:\n")
            for idx, (name, size) in enumerate(found_files, 1):
                print(f" [{idx}] {name} ({size:.1f} KB)")
        else:
            print("[안내] 폴더는 존재하지만 저장된 녹음(.wav) 파일이 없습니다.")
            
    except Exception as e:
        print(f"[오류] 파일 시스템을 읽어오는 중 예상치 못한 에러가 발생했습니다: {e}")
        
    print("=" * 50)

# ========================================================
# [3] 특정 범위 날짜의 녹음 파일 검색 기능
# ========================================================
def show_records_by_date(start_date_str, end_date_str):
    save_dir = "records"
    
    print("\n" + "=" * 50)
    print(f"[🔍 자비스 검색 시스템] 범위 내의 녹음 파일을 탐색합니다.")
    print(f"▶ 검색 범위: {start_date_str} ~ {end_date_str}")
    print("=" * 50)
    sys.stdout.flush()
    
    if not os.path.exists(save_dir):
        print(f"[안내] '{save_dir}' 폴더가 존재하지 않아 검색할 파일이 없습니다.")
        print("=" * 50)
        return []
        
    try:
        start_date = int(start_date_str)
        end_date = int(end_date_str)
    except ValueError:
        print("[오류] 날짜 형식은 반드시 '20260501'과 같은 8자리 숫자 형태여야 합니다.")
        print("=" * 50)
        return []

    found_files = []
    
    try:
        file_list = os.listdir(save_dir)
        
        for filename in file_list:
            if filename.endswith(".wav") and "-" in filename:
                try:
                    file_date_part = filename.split("-")[0]
                    file_date = int(file_date_part)
                    
                    if start_date <= file_date <= end_date:
                        full_path = os.path.join(save_dir, filename)
                        file_size = os.path.getsize(full_path) / 1024
                        found_files.append((filename, file_size))
                except (ValueError, IndexError):
                    pass

        if found_files:
            found_files.sort()
            print(f"[일치 항목 발견] 총 {len(found_files)}개의 파일이 조건에 부합합니다:\n")
            for idx, (name, size) in enumerate(found_files, 1):
                print(f" [{idx}] {name} ({size:.1f} KB)")
        else:
            print("[안내] 지정된 범위 내에 일치하는 녹음 파일이 존재하지 않습니다.")
            
    except Exception as e:
        print(f"[오류] 파일 시스템을 읽어오는 중 예상치 못한 에러가 발생했습니다: {e}")
        
    print("=" * 50)
    return found_files


# ========================================================
# 메인 실행부 (인터랙티브 메뉴)
# ========================================================
if __name__ == "__main__":
    print("=" * 40)
    print("  J.A.R.V.I.S 제어 터미널")
    print("=" * 40)
    print(" 1. 새로운 음성 녹음 시작 (5초)")
    print(" 2. 전체 녹음 파일 목록 보기")
    print(" 3. 특정 날짜 범위 내 녹음 파일 검색")
    print("=" * 40)
    
    try:
        user_choice = input("실행할 작업 번호를 입력하세요: ").strip()
        
        if user_choice == "1":
            record_audio(duration=5)
        elif user_choice == "2":
            show_all_records()
        elif user_choice == "3":
            start_input = input("시작 날짜 입력 (예: 20260501): ").strip()
            end_input = input("종료 날짜 입력 (예: 20260522): ").strip()
            show_records_by_date(start_input, end_input)
        else:
            print("\n[경고] 메뉴에 없는 번호입니다. 프로그램을 종료합니다.")
            
    except KeyboardInterrupt:
        print("\n\n[시스템] 사용자에 의해 제어 시스템이 강제 종료되었습니다.")