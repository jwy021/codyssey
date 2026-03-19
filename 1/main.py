# main.py

def analyze_and_extract_errors(log_path, error_path):
    try:
        with open(log_path, 'r', encoding='utf-8') as log_file:
            lines = log_file.readlines()
            
        if not lines:
            print('로그 파일이 비어있습니다.')
            return
        
        header = lines[0].strip()
        
        data_lines = [line.strip() for line in lines[1:] if line.strip()]
        
        # 시간순으로 출력
        print('로그 출력 시간 순서대로')
        print(header)
        for line in data_lines:
            print(line)
            
        print('\n' + '=' * 50 + '\n')
        
        # 보너스 과제 1: 시간 역순으로 정렬 및 출력
        data_lines.sort(reverse=True)
        
        print('--- 미션 컴퓨터 로그 출력 (시간 역순) ---')
        print(header)
        for line in data_lines:
            print(line)
            
        # 보너스 과제 2: 문제가 되는 부분만 필터링 및 파일 저장
        problem_keywords = ('unstable', 'explosion', 'powered down')
        
        with open(error_path, 'w', encoding='utf-8') as error_file:
            error_file.write(header + '\n')
            
            for line in data_lines:
                lower_line = line.lower()
                for keyword in problem_keywords:
                    if keyword in lower_line:
                        error_file.write(line + '\n')
                        break  # 중복 기록 방지
                        
        # 문자열 내에 작은따옴표를 출력하기 위해 큰따옴표 사용
        print(f"\n문제가 되는 로그 데이터만 '{error_path}' 저장")
        
    # 예외 처리
    except FileNotFoundError:
        print(f"[오류] '{log_path}' 파일을 찾을 수 없습니다. 경로를 확인하십시오.")
    except PermissionError:
        print(f"[권한 오류] '{log_path}' 파일을 읽거나 쓸 수 있는 권한이 없습니다.")
    except Exception as e:
        print(f'파일 처리 중 알 수 없는 예외 발생: {e}')

if __name__ == '__main__':
    # 입력 파일과 출력 파일 이름 지정
    target_log = 'mission_computer_main.log'
    error_output = 'error_logs.txt'
    
    # 함수 실행
    analyze_and_extract_errors(target_log, error_output)