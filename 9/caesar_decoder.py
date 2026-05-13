# caesar_decoder.py
import string
import urllib.request

# ==========================================
# [텍스트 사전] 외부 서버에서 자동으로 불러오기
# ==========================================
def load_dictionary_from_web():
    print("\n[시스템] 외부 서버에서 1만 개의 영단어 사전을 다운로드합니다...")
    # 구글에서 분석한 가장 많이 쓰이는 영단어 10,000개 리스트 (깃허브 공개용)
    url = "https://raw.githubusercontent.com/first20hours/google-10000-english/master/google-10000-english-no-swears.txt"
    
    try:
        # URL에 접속해서 데이터를 가져옴
        response = urllib.request.urlopen(url)
        # 데이터를 문자열로 디코딩하고, 줄바꿈 기준으로 쪼개서 리스트로 만듦
        words = response.read().decode('utf-8').splitlines()
        print(f"[SUCCESS] {len(words):,}개의 단어를 성공적으로 메모리에 적재했습니다!")
        
        # 1글자, 2글자짜리 단어(a, is 등)는 카이사르 암호에서 우연히 일치할 확률이 높아 
        # 오탐(False Positive)을 일으키기 쉬우므로, 3글자 이상인 단어만 필터링!
        filtered_words = [word for word in words if len(word) >= 3]
        return filtered_words
        
    except Exception as e:
        print(f"[오류] 인터넷에서 사전을 다운로드하지 못했습니다: {e}")
        # 다운로드 실패 시 비상용 기본 사전 제공
        return ["password", "secret", "key", "admin", "system", "emergency", "storage", "cyphertext", "good", "hello"]

# 코드가 실행될 때 인터넷에서 1만 개의 단어 사전을 알아서 세팅합니다.
DICTIONARY = load_dictionary_from_web()

def caesar_cipher_decode_auto(target_text):
    """
    카이사르 암호를 해독하고, 웹 사전과 '정확히 일치'할 때만 멈춥니다.
    """
    print("\n" + "=" * 55)
    print("[시스템] 카이사르 암호 자동 해독 (웹 사전 + 정밀 탐색) 가동")
    print("=" * 55)

    output_filename = "result.txt"

    # 1부터 26자리까지 밀어가며 모든 경우의 수 해독
    for shift in range(1, 27):
        decoded_chars = []
        
        for char in target_text:
            if char.isalpha():
                if char.islower():
                    shifted = chr((ord(char) - ord('a') - shift) % 26 + ord('a'))
                else:
                    shifted = chr((ord(char) - ord('A') - shift) % 26 + ord('A'))
                decoded_chars.append(shifted)
            else:
                decoded_chars.append(char)

        decoded_str = "".join(decoded_chars)

        # [요구사항] 반복 할 때마다 결과를 눈으로 확인 할 수 있어야 한다.
        print(f"[자리수 {shift:2d}] 해독 시도: {decoded_str}")

        # ==========================================
        # [핵심 로직] 정확한 단어 매칭 (오탐 방지)
        # ==========================================
        decoded_lower = decoded_str.lower()
        
        # 마침표, 쉼표 등 구두점을 모두 제거하여 순수 알파벳만 남김
        cleaned_text = decoded_lower.translate(str.maketrans('', '', string.punctuation))
        
        # 띄어쓰기를 기준으로 문장을 개별 단어 리스트로 쪼갬
        decoded_words = cleaned_text.split()
        
        found_keyword = None
        
        # 쪼개진 단어가 1만 개짜리 사전에 '정확히' 존재하는지 검사
        for word in decoded_words:
            if word in DICTIONARY:
                found_keyword = word
                break  # 정확한 단어를 찾았으므로 탐색 중단

        # 사전에 일치하는 단어를 찾았을 경우
        if found_keyword:
            print("\n" + "=" * 55)
            print(f"[SUCCESS] 사전에 등록된 키워드 '{found_keyword}'(이)가 발견되었습니다!")
            print(f"▶ 정답 자리수: {shift}")
            print(f"▶ 최종 해독 암호: {decoded_str}")
            print("=" * 55)

            # [요구사항] 파일 저장 및 예외 처리
            try:
                with open(output_filename, "w", encoding="utf-8") as f:
                    f.write(decoded_str)
                print(f"\n[안내] 해독된 암호가 '{output_filename}'에 안전하게 자동 저장되었습니다.")
            except IOError as e:
                print(f"\n[오류] 결과를 파일로 저장하는 중 디스크 문제가 발생했습니다: {e}")

            # 완전 종료
            return

    print("\n[실패] 사전에 정확히 일치하는 단어를 찾지 못했습니다. 수동 확인이 필요합니다.")


def main():
    input_filename = "password.txt"

    # 파일 읽기 및 예외 처리
    try:
        with open(input_filename, "r", encoding="utf-8") as f:
            target_text = f.read().strip()
            
        if not target_text:
            print(f"[오류] '{input_filename}' 파일에 내용이 없습니다.")
            return
            
    except FileNotFoundError:
        print(f"[오류] '{input_filename}' 파일을 찾을 수 없습니다.")
        return
    except Exception as e:
        print(f"[오류] 파일을 읽는 중 예기치 못한 에러가 발생했습니다: {e}")
        return

    print(f"\n[안내] 로드된 원본 암호문: {target_text}")
    
    # 해독 엔진 가동
    caesar_cipher_decode_auto(target_text)

if __name__ == "__main__":
    main()