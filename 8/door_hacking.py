# door_hacking.py
import zipfile
import itertools
import string
import time
import zlib
from datetime import datetime

def unlock_zip(zip_filename="emergency_storage_key.zip"):
    # 탐색할 문자셋: 소문자 알파벳(a-z) + 숫자(0-9)
    charset = string.ascii_lowercase + string.digits
    password_length = 6
    
    start_time_real = datetime.now()
    start_time_tick = time.time()
    attempts = 0
    
    print("=" * 60)
    print(f"[시스템 안내] 보안 해제 프로토콜을 가동합니다.")
    print(f"▶ 대상 파일: {zip_filename}")
    print(f"▶ 탐색 조건: 소문자 및 숫자 조합 {password_length}자리")
    print(f"▶ 시작 시간: {start_time_real.strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60 + "\n")
    
    try:
        # ZIP 파일 객체 열기
        with zipfile.ZipFile(zip_filename, 'r') as zf:
            
            # itertools.product를 통해 36개 문자로 만들 수 있는 6자리 모든 중복 순열 생성
            for guess in itertools.product(charset, repeat=password_length):
                attempts += 1
                password = ''.join(guess)
                
                # 콘솔 과부하를 막기 위해 100만 번 단위로만 진행 상황 출력
                if attempts % 1000000 == 0:
                    elapsed = time.time() - start_time_tick
                    print(f"[-] 탐색 진행 중... | 시도 횟수: {attempts:,}회 | 현재 대입 암호: {password} | 경과 시간: {elapsed:.2f}초")
                
                try:
                    # 암호 대입하여 압축 해제 시도
                    zf.extractall(pwd=password.encode('utf-8'))
                    
                    # 성공 시 (에러가 발생하지 않고 여기까지 코드가 넘어오면 성공)
                    elapsed_final = time.time() - start_time_tick
                    print("\n" + "=" * 60)
                    print(f"[SUCCESS] 접근 권한 획득! 암호를 찾았습니다: {password}")
                    print(f"▶ 총 시도 횟수: {attempts:,}회")
                    print(f"▶ 총 소요 시간: {elapsed_final:.2f}초")
                    print("=" * 60)
                    
                    # 찾은 암호를 password.txt에 저장
                    with open("password.txt", "w", encoding="utf-8") as f:
                        f.write(password)
                    print("\n[안내] 확보한 암호가 'password.txt' 파일로 안전하게 저장되었습니다.")
                    
                    return password
                                        
                except (RuntimeError, zipfile.BadZipFile, zlib.error):
                    # zlib.error 발생 시 비밀번호 틀림으로 간주하고 무시 (Pass)
                    pass
                except (RuntimeError, zipfile.BadZipFile):
                    # 비밀번호가 틀려 런타임 에러가 발생한 경우 무시하고 다음 암호 시도
                    pass
                    
    except FileNotFoundError:
        print(f"\n[오류] 타겟 파일 '{zip_filename}'을 찾을 수 없습니다.")
        print("스크립트와 같은 경로에 ZIP 파일이 있는지 확인해 주십시오.")
        return None

    # 모든 경우의 수를 다 돌았는데도 실패한 경우
    print("\n[실패] 모든 경우의 수를 대입했으나 암호를 찾지 못했습니다.")
    return None

if __name__ == "__main__":
    unlock_zip("emergency_storage_key.zip")