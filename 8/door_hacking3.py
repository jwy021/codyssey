# door_hacking.py
import pyzipper
import itertools
import string
import time
import multiprocessing
import io
import os
import sys  # 터미널 출력 즉시 동기화를 위해 추가
from datetime import datetime

# ==========================================
# [Worker] 각 CPU 코어 (Memory IO 최적화 및 Ctrl+C 감지)
# ==========================================
def check_password_chunk(args):
    prefix, zip_filename, start_time_tick = args
    charset = string.ascii_lowercase + string.digits
    
    try:
        # 단 한 번만 파일을 읽어 메모리(RAM)에 올림
        with open(zip_filename, 'rb') as f:
            memory_zip_data = io.BytesIO(f.read())
    except Exception:
        return None
        
    try:
        with pyzipper.AESZipFile(memory_zip_data, 'r') as zf:
            file_list = zf.namelist()
            if not file_list:
                return None
            target_file = file_list[0]
            
            for count, guess in enumerate(itertools.product(charset, repeat=5), 1):
                password = prefix + ''.join(guess)
                
                # [수정 1] 출력 주기를 100만에서 2만으로 대폭 줄여서 즉각적인 피드백 제공
                if count % 20000 == 0:
                    elapsed = time.time() - start_time_tick
                    print(f"[{prefix}* 대역] 시간: {elapsed:.2f}초 | 반복: {count:,}회 | 현재 암호: {password}")
                    sys.stdout.flush() # [수정 2] 터미널에 즉시 출력되도록 강제 밀어내기
                
                try:
                    # 메모리상에서 비밀번호 테스트
                    zf.read(target_file, pwd=password.encode('utf-8'))
                    return password
                except Exception:
                    # 비밀번호 틀림 에러 무시 (KeyboardInterrupt는 BaseException이므로 여기서 걸리지 않고 밖으로 나감)
                    pass
                    
    except KeyboardInterrupt:
        # [수정 3] 백그라운드 코어에서 Ctrl+C를 감지하면 즉시 메인으로 "STOP" 신호 전송
        return "STOP"
    except Exception:
        pass
    
    return None

# ==========================================
# [Master] 메인 해킹 통제 함수
# ==========================================
def unlock_zip(zip_filename="emergency_storage_key.zip"):
    if not os.path.exists(zip_filename):
        print(f"[오류] 타겟 파일 '{zip_filename}'을 찾을 수 없습니다.")
        return
        
    charset = string.ascii_lowercase + string.digits
    start_time_real = datetime.now()
    start_time_tick = time.time()
    
    cores = multiprocessing.cpu_count()
    
    print("=" * 60)
    print(f"[시스템 안내] 초고속 Memory IO 멀티프로세싱 가동")
    print(f"▶ 대상 파일: {zip_filename}")
    print(f"▶ 가용 CPU 코어: {cores}개 동시성 작업 시작")
    print(f"▶ 출력 주기: 20,000 단위 (Ctrl+C 즉시 종료 지원)")
    print(f"▶ 시작 시간: {start_time_real.strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60 + "\n")

    tasks = [(char, zip_filename, start_time_tick) for char in charset]
    pool = multiprocessing.Pool(processes=cores)
    
    try:
        for result in pool.imap_unordered(check_password_chunk, tasks):
            if result == "STOP":
                # [수정 3] 자식 프로세스 중 하나라도 Ctrl+C를 감지했다면 전체 종료
                print("\n[경고] 사용자에 의해 탐색이 강제 중단되었습니다. (워커 종료 감지)")
                pool.terminate()
                pool.join()
                return None
                
            elif result is not None:
                # 암호 발견 시
                elapsed_final = time.time() - start_time_tick
                pool.terminate() 
                pool.join()
                
                print("\n" + "=" * 60)
                print(f"[SUCCESS] 접근 권한 획득! 암호를 찾았습니다: {result}")
                print(f"▶ 총 소요 시간: {elapsed_final:.2f}초")
                print("=" * 60)
                
                try:
                    with open("password.txt", "w", encoding="utf-8") as f:
                        f.write(result)
                    print("\n[안내] 확보한 암호가 'password.txt'에 안전하게 저장되었습니다.")
                except IOError as e:
                    print(f"\n[경고] 암호는 찾았으나 파일 저장 중 오류 발생: {e}")
                
                return result
                
    except KeyboardInterrupt:
        print("\n[경고] 사용자에 의해 탐색이 강제 중단되었습니다. (메인 종료 감지)")
        pool.terminate()
        pool.join()
        return None

    print("\n[실패] 모든 경우의 수를 대입했으나 암호를 찾지 못했습니다.")
    pool.close()
    pool.join()
    return None

if __name__ == "__main__":
    unlock_zip()