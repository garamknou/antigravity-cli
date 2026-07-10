# -*- coding: utf-8 -*-
"""
스타벅스 코리아 전국 매장 정보 수집 스크립트
"""

import os
import time
import random
import requests
import pandas as pd

# 스타벅스 내부 API 엔드포인트 정의
SIDO_LIST_URL = "https://www.starbucks.co.kr/store/getSidoList.do"
STORE_LIST_URL = "https://www.starbucks.co.kr/store/getStore.do"


def safe_post_request(url, data=None, retries=5, base_delay=2.0):
    """
    네트워크 예외 및 429/503 오류 발생 시 지수 백오프 재시도를 지원하는 안전한 POST 요청 함수
    """
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Content-Type": "application/x-www-form-urlencoded"
    }

    for attempt in range(retries):
        try:
            # 10초 타임아웃 설정
            response = requests.post(url, data=data, headers=headers, timeout=10)
            
            # HTTP 상태 코드가 200이 아닐 경우 예외 발생 (429, 503 등 대응)
            response.raise_for_status()
            
            # JSON 응답 반환
            return response.json()
        except (requests.RequestException, ValueError) as e:
            if attempt == retries - 1:
                print(f"[오류] {url} 요청 실패 (최대 재시도 {retries}회 초과): {e}")
                raise e
            
            # 지수 백오프 공식 적용: base_delay * (2 ^ attempt) + 미세한 랜덤 지터(jitter)
            delay = base_delay * (2 ** attempt) + random.uniform(0, 1.0)
            print(f"[경고] 요청 중 에러 발생 ({e}). {delay:.2f}초 후 재시도합니다... (재시도 {attempt + 1}/{retries})")
            time.sleep(delay)


def get_sido_list():
    """
    스타벅스 전국 시도 코드 목록을 조회합니다.
    """
    print("[정보] 시도 목록 조회 시작...")
    try:
        response_data = safe_post_request(SIDO_LIST_URL)
        sido_list = response_data.get('list', [])
        print(f"[정보] 총 {len(sido_list)}개의 시도 코드를 조회했습니다.")
        return [(item.get('sido_cd'), item.get('sido_nm')) for item in sido_list]
    except Exception as e:
        print(f"[오류] 시도 목록 조회 실패: {e}")
        return []


def get_stores_by_sido(sido_code, sido_name):
    """
    특정 시도 코드에 속한 모든 매장 정보를 조회합니다.
    """
    print(f"[정보] '{sido_name}' ({sido_code}) 매장 정보 수집 중...")
    
    payload = {
        'ins_lat': '37.56682',
        'ins_lng': '126.97865',
        'p_sido_cd': sido_code,
        'p_gugun_cd': '',
        'in_biz_cd': '',
        'set_date': '',
        'iend': '2000'  # 넉넉하게 설정하여 한 시도의 전체 데이터를 일괄 조회
    }
    
    try:
        response_data = safe_post_request(STORE_LIST_URL, data=payload)
        stores = response_data.get('list', [])
        print(f"[정보] '{sido_name}' 매장 수: {len(stores)}")
        return stores
    except Exception as e:
        print(f"[오류] '{sido_name}' 매장 조회 실패: {e}")
        return []


def main():
    start_time = time.time()
    print("[정보] 스타벅스 전국 매장 정보 수집 파이프라인을 시작합니다.")

    # 1. 전국 시도 목록 조회
    sido_list = get_sido_list()
    if not sido_list:
        print("[오류] 시도 코드가 존재하지 않아 수집을 중단합니다.")
        return

    all_stores = []

    # 2. 각 시도별 매장 순회 수집
    for sido_code, sido_name in sido_list:
        stores = get_stores_by_sido(sido_code, sido_name)
        all_stores.extend(stores)
        
        # 서버 부하 방지를 위해 요청 간 랜덤 딜레이 적용 (0.3 ~ 0.8초)
        delay = random.uniform(0.3, 0.8)
        time.sleep(delay)

    if not all_stores:
        print("[경고] 수집된 매장 데이터가 없습니다.")
        return

    # 3. 데이터프레임 변환 및 컬럼 정제
    df = pd.DataFrame(all_stores)

    # 분석 시 사용하기 편하도록 유용한 컬럼들을 한글 컬럼명으로 매핑하여 추출
    rename_cols = {
        's_name': '매장명',
        'sido_name': '시도명',
        'gugun_name': '구군명',
        'doro_address': '도로명주소',
        'tel': '전화번호',
        'lat': '위도',
        'lng': '경도',
        'store_type_nm': '매장타입',
        'open_dt': '오픈일자'
    }

    # API 응답에 있는 유효한 필드만 선별하여 저장
    available_cols = [col for col in rename_cols.keys() if col in df.columns]
    df_result = df[available_cols].rename(columns=rename_cols)

    # 중복 제거 (매장이 중복 수집되었을 가능성 방지)
    df_result = df_result.drop_duplicates(subset=['매장명', '도로명주소'])

    # 4. 결과 저장
    # 상대경로 기반으로 저장 디렉토리 및 파일 경로 구성
    script_dir = os.path.dirname(os.path.abspath(__file__))
    data_dir = os.path.join(script_dir, '..', 'data')
    os.makedirs(data_dir, exist_ok=True)
    
    output_path = os.path.join(data_dir, 'starbucks_stores.csv')
    
    # 엑셀 깨짐 방지를 위해 'utf-8-sig' 인코딩 지정
    df_result.to_csv(output_path, index=False, encoding='utf-8-sig')
    
    elapsed_time = time.time() - start_time
    
    # 출력 경로를 워크스페이스 기준 상대 경로로 변환
    workspace_root = os.path.abspath(os.path.join(script_dir, '..', '..'))
    rel_output_path = os.path.relpath(output_path, workspace_root).replace('\\', '/')
    print(f"[완료] 총 {len(df_result)}개의 매장 정보를 {rel_output_path}에 저장했습니다. (소요시간: {elapsed_time:.2f}초)")


if __name__ == '__main__':
    main()
