# main.py

def manage_mars_inventory(input_file, danger_file, binary_file):
    try:
        # 1. 파일 읽기 및 출력
        with open(input_file, 'r', encoding='utf-8') as file:
            lines = file.readlines()
            
        if not lines:
            print('경고: 인벤토리 파일이 비어있습니다.')
            return

        print('--- 화성 기지 전체 적재 화물 목록 ---')
        for line in lines:
            # 양끝 공백 및 줄바꿈 문자를 제거하여 깔끔하게 출력
            print(line.strip())
            
        # 2. Python 리스트(List) 객체로 변환
        header_line = lines[0].strip()
        headers = header_line.split(',')
        
        # 인화성 지수 컬럼의 인덱스 찾기 (키워드 매칭)
        # 만약 명확한 이름이 없다면 마지막 컬럼을 인화성 지수로 간주합니다.
        flammability_idx = -1
        for i, header_name in enumerate(headers):
            lower_header = header_name.lower()
            if 'flammability' in lower_header or '인화' in lower_header:
                flammability_idx = i
                break
                
        if flammability_idx == -1:
            flammability_idx = len(headers) - 1

        # 첫 번째 줄(헤더)을 제외한 나머지 데이터를 2차원 리스트로 변환
        data_list = []
        for line in lines[1:]:
            row = line.strip().split(',')
            # 데이터 개수가 헤더와 일치하는 정상적인 줄만 추가
            if len(row) == len(headers):
                data_list.append(row)

        # 3. 배열 내용을 인화성이 높은 순으로 정렬 (내림차순)
        def get_flammability(row):
            try:
                return float(row[flammability_idx])
            except ValueError:
                # 숫자로 변환할 수 없는 경우 가장 낮게 처리
                return 0.0

        data_list.sort(key=get_flammability, reverse=True)

        # 4. 인화성 지수가 0.7 이상인 목록 추출 및 별도 출력
        danger_list = []
        print('\n--- [경고] 인화성 지수 0.7 이상 위험 물질 목록 ---')
        print(header_line)
        
        for row in data_list:
            flammability_value = get_flammability(row)
            if flammability_value >= 0.7:
                danger_list.append(row)
                # 리스트를 다시 쉼표로 연결하여 출력
                print(','.join(row))

        # 5. 위험 물질 목록을 CSV 포맷으로 저장
        with open(danger_file, 'w', encoding='utf-8') as file:
            # 헤더 먼저 쓰기
            file.write(header_line + '\n')
            # 필터링된 데이터 쓰기
            for row in danger_list:
                file.write(','.join(row) + '\n')
                
        # 문자열 내부에 작은따옴표를 출력하기 위해 큰따옴표 사용
        print(f"\n[시스템 안내] 위험 물질 목록이 '{danger_file}' 파일로 격리 저장되었습니다.")

        # --- 보너스 과제 시작 ---
        
        # 6. 정렬된 배열을 이진 파일(Binary)로 저장
        # 파이썬 리스트 객체 자체를 문자열로 바꾼 뒤, 기계가 읽는 바이트(Bytes)로 인코딩합니다.
        with open(binary_file, 'wb') as bin_out:
            array_as_string = str(data_list)
            bin_out.write(array_as_string.encode('utf-8'))
            
        print(f"[안내] 정렬된 전체 배열이 이진 파일 '{binary_file}'에 저장되었습니다.")
        
        # 7. 이진 파일에서 다시 읽어 들여서 화면에 출력
        with open(binary_file, 'rb') as bin_in:
            byte_data = bin_in.read()
            # 바이트를 디코딩하고, 파이썬 내장 함수 eval을 사용해 완벽한 리스트 객체로 복원합니다.
            recovered_list = eval(byte_data.decode('utf-8'))
            
        print(f'\n--- {binary_file} (이진 파일)에서 복원된 배열 내용 ---')
        for item in recovered_list:
            print(item)
            

    # 파일 처리 관련 예외 처리
    except FileNotFoundError:
        print(f"[오류] '{input_file}' 파일을 찾을 수 없습니다. 화물 목록 데이터가 있는지 확인하십시오.")
    except PermissionError:
        print(f"[권한 오류] '{input_file}' 파일을 읽거나 쓸 권한이 없습니다.")
    except Exception as e:
        print(f'알 수 없는 시스템 오류가 발생했습니다: {e}')

if __name__ == '__main__':
    # 입력 파일과 출력 파일 이름 지정
    target_inventory = 'Mars_Base_Inventory_List.csv'
    danger_output = 'Mars_Base_Inventory_danger.csv'
    binary_out = 'Mars_Base_Inventory_List.bin'
    
    # 함수 호출
    manage_mars_inventory(target_inventory, danger_output, binary_out)
    