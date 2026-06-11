import csv
import os
import pymysql


class MySQLHelper:
    '''MySQL 데이터베이스 연결 및 쿼리 실행을 편리하게 도와주는 헬퍼 클래스입니다.'''

    def __init__(self, host, user, password, db_name = None):
        '''연결을 위한 설정 정보를 초기화합니다.'''
        self.host = host
        self.user = user
        self.password = password
        self.db_name = db_name
        self.connection = None

    def connect(self):
        '''데이터베이스에 연결합니다. 데이터베이스명이 지정되어 있으면 해당 DB를 선택합니다.'''
        try:
            self.connection = pymysql.connect(
                host = self.host,
                user = self.user,
                password = self.password,
                database = self.db_name,
                charset = 'utf8mb4',
                cursorclass = pymysql.cursors.DictCursor
            )
            return True
        except Exception as error_msg:
            print(f'[오류] DB 연결 실패: {error_msg}')
            return False

    def select_db(self, db_name):
        '''연결된 세션에서 데이터베이스를 전환합니다.'''
        if self.connection:
            self.connection.select_db(db_name)
            self.db_name = db_name

    def execute(self, sql, params = None, commit = True):
        '''INSERT, UPDATE, DELETE, CREATE, DROP 등 데이터를 변경하는 쿼리를 실행합니다.'''
        if not self.connection:
            print('[오류] 연결이 없습니다.')
            return False
        try:
            with self.connection.cursor() as cursor:
                cursor.execute(sql, params)
            if commit:
                self.connection.commit()
            return True
        except Exception as error_msg:
            print(f'[오류] 쿼리 실행 에러: {error_msg}')
            self.connection.rollback()
            return False

    def commit(self):
        '''트랜잭션을 커밋합니다.'''
        if self.connection:
            self.connection.commit()

    def rollback(self):
        '''트랜잭션을 롤백합니다.'''
        if self.connection:
            self.connection.rollback()

    def fetch_all(self, sql, params = None):
        '''SELECT 쿼리를 실행하여 결과의 모든 행을 리스트(dict 형태)로 반환합니다.'''
        if not self.connection:
            return None
        try:
            with self.connection.cursor() as cursor:
                cursor.execute(sql, params)
                return cursor.fetchall()
        except Exception as error_msg:
            print(f'[오류] 데이터 조회 실패: {error_msg}')
            return None

    def fetch_one(self, sql, params = None):
        '''SELECT 쿼리를 실행하여 결과의 단일 행을 반환합니다.'''
        if not self.connection:
            return None
        try:
            with self.connection.cursor() as cursor:
                cursor.execute(sql, params)
                return cursor.fetchone()
        except Exception as error_msg:
            print(f'[오류] 데이터 단일 조회 실패: {error_msg}')
            return None

    def close(self):
        '''데이터베이스 연결을 닫습니다.'''
        if self.connection:
            self.connection.close()
            self.connection = None


def check_csv_data(file_path):
    '''CSV 파일을 읽어 내용 확인을 위해 콘솔에 상위 5행을 보기 좋게 출력합니다.'''
    print('\n' + '=' * 50)
    print('      [mars_weathers_data.CSV 파일 내용 확인]      ')
    print('=' * 50)
    
    data_list = []
    try:
        with open(file_path, 'r', encoding = 'utf-8-sig') as csv_file:
            reader = csv.DictReader(csv_file)
            
            # 헤더 정보 확인
            print(f' 헤더 정보: {reader.fieldnames}')
            print('-' * 50)
            
            # 데이터를 읽고 상위 5행만 미리 보여주기
            for index, row in enumerate(reader):
                data_list.append(row)
                if index < 5:
                    print(f" 행 {index + 1}: ID={row['weather_id']}, 날짜={row['mars_date']}, 기온={row['temp']}, 폭풍={row['stom']}")
            
            print(f'... (총 {len(data_list)}개의 데이터 행 읽기 완료)')
            print('=' * 50)
            return data_list
    except FileNotFoundError:
        print(f'[오류] CSV 파일을 찾을 수 없습니다. 경로를 확인해 주세요: {file_path}')
        return None
    except Exception as error_msg:
        print(f'[오류] CSV 파일 읽기 실패: {error_msg}')
        return None


def main():
    '''프로그램의 메인 실행 흐름을 제어합니다.'''
    # 현재 파일의 디렉토리를 기준으로 CSV 파일 경로 설정
    current_dir = os.path.dirname(os.path.abspath(__file__))
    csv_file_path = os.path.join(current_dir, 'mars_weathers_data.CSV')

    # 1. CSV 파일 읽기 및 데이터 확인
    weather_data = check_csv_data(csv_file_path)
    if not weather_data:
        print('[중단] CSV 데이터를 불러오지 못해 작업을 중단합니다.')
        return

    # 2. 사용자로부터 MySQL 접속 비밀번호 입력받기 (보안상 하드코딩 방지)
    print('\n[데이터베이스 접속 정보 입력]')
    mysql_password = input('MySQL root 계정 비밀번호를 입력하세요: ')

    # 3. MySQLHelper 인스턴스 생성 및 연결
    db_helper = MySQLHelper(
        host = 'localhost',
        user = 'root',
        password = mysql_password
    )

    if not db_helper.connect():
        print('[중단] 데이터베이스 연결에 실패하여 작업을 중단합니다.')
        return

    print('[성공] MySQL 서버 연결에 성공했습니다.')

    # 4. 데이터베이스 및 테이블 생성
    db_helper.execute('CREATE DATABASE IF NOT EXISTS mars_db')
    db_helper.select_db('mars_db')
    db_helper.execute('DROP TABLE IF EXISTS mars_weather')

    # mars_weather 테이블 생성
    create_table_sql = '''
    CREATE TABLE mars_weather (
        weather_id INT AUTO_INCREMENT PRIMARY KEY,
        mars_date DATETIME NOT NULL,
        temp INT,
        storm INT
    )
    '''
    db_helper.execute(create_table_sql)
    print("[성공] 'mars_db' 데이터베이스 및 'mars_weather' 테이블을 생성했습니다.")

    # 5. CSV 데이터를 DB 테이블에 삽입 (대량 입력을 위해 트랜잭션 단위 커밋 적용)
    print('[안내] 데이터 입력을 시작합니다...')
    inserted_count = 0
    insert_sql = '''
    INSERT INTO mars_weather (weather_id, mars_date, temp, storm)
    VALUES (%s, %s, %s, %s)
    '''
    
    success = True
    for row in weather_data:
        # 데이터 타입 변환 및 정제
        weather_id = int(row['weather_id'])
        mars_date = f"{row['mars_date']} 00:00:00"
        temp = int(round(float(row['temp'])))
        storm = int(row['stom'])  # CSV 'stom' -> DB 'storm' 매핑

        # 매 쿼리마다 커밋하지 않고 마지막에 일괄 커밋
        if db_helper.execute(insert_sql, (weather_id, mars_date, temp, storm), commit = False):
            inserted_count = inserted_count + 1
        else:
            success = False
            break

    if success:
        db_helper.commit()
        print(f'[성공] 총 {inserted_count}개의 데이터를 성공적으로 입력했습니다.')
    else:
        db_helper.rollback()
        print('[오류] 데이터 입력 중 오류가 발생하여 롤백했습니다.')
        db_helper.close()
        return

    # 6. 최종 데이터 확인 및 요약 출력
    summary_sql = '''
    SELECT COUNT(*) AS total_rows, 
           AVG(temp) AS avg_temp, 
           MAX(temp) AS max_temp, 
           MIN(temp) AS min_temp 
    FROM mars_weather
    '''
    summary = db_helper.fetch_one(summary_sql)
    if summary:
        print('\n' + '=' * 50)
        print('       [mars_weather 테이블 저장 데이터 요약]       ')
        print('=' * 50)
        print(f" 총 데이터 건수 : {summary['total_rows']} 건")
        print(f" 평균 기온      : {summary['avg_temp']:.2f} 도")
        print(f" 최고 기온      : {summary['max_temp']} 도")
        print(f" 최저 기온      : {summary['min_temp']} 도")
        print('=' * 50)

    # 7. 연결 해제
    db_helper.close()
    print('[안내] 데이터베이스 연결을 종료했습니다.')


if __name__ == '__main__':
    main()
