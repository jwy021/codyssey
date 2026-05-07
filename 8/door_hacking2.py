# door_hacking.py
import pyzipper  # 기본 zipfile 대신 AES를 지원하는 pyzipper 사용
import itertools
import string
import time
import multiprocessing
from datetime import datetime

# ==========================================
# [Worker] 각 CPU 코어가 독립적으로 실행할 탐색 함수
# ==========================================
def check_password_chunk(args):
    prefix, zip_filename = args
    charset = string.ascii_lowercase + string.digits
    
    # 각 코어가 할당받은 첫 번째 글자(prefix)를 알림
    print(f"[진행] CPU 코어 할당 완료 -> 접두사 '{prefix}' 탐색 시작...")
    
    try:
        with pyzipper.AESZipFile(zip_filename, 'r') as zf:
            # 첫 글자는 prefix로 고정되었으므로, 나머지 5자리(repeat=5)만 순열을 돌림
            for guess in itertools.product(charset, repeat=5):
                password = prefix + ''.join(guess)
                try:
                    zf.extractall(pwd=password.encode('utf-8'))
                    return password  # 암호를 찾으면 즉시 반환
                except Exception:
                    pass
    except Exception:
        pass
    
    return None  # 이 접두사 대역에는 암호가 없음

# ==========================================
# [Master] 코어들을 통제하고 분배하는 메인 함수
# ==========================================
def unlock_zip(zip_filename="emergency_storage_key.zip"):
    charset = string.ascii_lowercase + string.digits
    start_time_real = datetime.now()
    start_time_tick = time.time()
    
    # 현재 컴퓨터의 가용 CPU 코어 개수 확인
    cores = multiprocessing.cpu_count()
    
    print("=" * 60)
    print(f"[시스템 안내] 멀티프로세싱 병렬 보안 해제 프로토콜을 가동합니다.")
    print(f"▶ 대상 파일: {zip_filename}")
    print(f"▶ 가용 CPU 코어: {cores}개 동시 가동")
    print(f"▶ 시작 시간: {start_time_real.strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60 + "\n")

    # 1. 36개의 작업(Task) 리스트 생성 (a부터 9까지)
    tasks = [(char, zip_filename) for char in charset]

    # 2. CPU 코어 개수만큼 프로세스 풀(Pool) 생성
    pool = multiprocessing.Pool(processes=cores)
    
    try:
        # 3. imap_unordered를 통해 비동기적으로 작업 분배 및 결과 수신
        for result in pool.imap_unordered(check_password_chunk, tasks):
            if result is not None:
                # [핵심] 누군가 암호를 찾았다면!
                elapsed_final = time.time() - start_time_tick
                
                # 나머지 진행 중인 모든 프로세스를 즉시 강제 종료 (자원 절약)
                pool.terminate() 
                pool.join()
                
                print("\n" + "=" * 60)
                print(f"[SUCCESS] 접근 권한 획득! 암호를 찾았습니다: {result}")
                print(f"▶ 총 소요 시간: {elapsed_final:.2f}초")
                print("=" * 60)
                
                with open("password.txt", "w", encoding="utf-8") as f:
                    f.write(result)
                print("\n[안내] 확보한 암호가 'password.txt' 파일로 안전하게 저장되었습니다.")
                return result
                
    except KeyboardInterrupt:
        print("\n[경고] 사용자에 의해 탐색이 강제 중단되었습니다.")
        pool.terminate()
        pool.join()
        return None

    # 모든 대역을 다 뒤졌으나 없는 경우
    print("\n[실패] 모든 경우의 수를 대입했으나 암호를 찾지 못했습니다.")
    pool.close()
    pool.join()
    return None

# 파이썬에서 멀티프로세싱을 윈도우 환경에서 안전하게 돌리기 위한 필수 구문
if __name__ == "__main__":
    unlock_zip("emergency_storage_key.zip")