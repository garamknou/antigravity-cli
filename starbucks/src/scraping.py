# -*- coding: utf-8 -*-
"""
스타벅스 코리아 전국 매장 정보 수집 스크립트 (프레임워크 스크래퍼)
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
            response = requests.post(url, data=data, headers=headers, timeout=10)
            response.raise_for_status()
            return response.json()
        except (requests.RequestException, ValueError) as e:
            if attempt == retries - 1:
                print(f"[오류] {url} 요청 실패 (최대 재시도 {retries}회 초과): {e}")
                raise e
            
            delay = base_delay * (2 ** attempt) + random.uniform(0, 1.0)
            print(f"[경고] 요청 중 에러 발생 ({e}). {delay:.2f}초 후 재시도합니다... (재시도 {attempt + 1}/{retries})")
            time.sleep(delay)


def get_sido_list():
    """
    스타벅스 전국 시도 코드 목록을 조회합니다.
    """
    print("[Scraper] 시도 목록 조회 시작...")
    try:
        response_data = safe_post_request(SIDO_LIST_URL)
        sido_list = response_data.get('list', [])
        print(f"[Scraper] 총 {len(sido_list)}개의 시도 코드를 조회했습니다.")
        return [(item.get('sido_cd'), item.get('sido_nm')) for item in sido_list]
    except Exception as e:
        print(f"[Scraper] [Error] 시도 목록 조회 실패: {e}")
        return []


def get_stores_by_sido(sido_code, sido_name):
    """
    특정 시도 코드에 속한 모든 매장 정보를 조회합니다.
    """
    print(f"[Scraper] '{sido_name}' ({sido_code}) 매장 정보 수집 중...")
    
    payload = {
        'ins_lat': '37.56682',
        'ins_lng': '126.97865',
        'p_sido_cd': sido_code,
        'p_gugun_cd': '',
        'in_biz_cd': '',
        'set_date': '',
        'iend': '2000'
    }
    
    try:
        response_data = safe_post_request(STORE_LIST_URL, data=payload)
        stores = response_data.get('list', [])
        print(f"[Scraper] '{sido_name}' 매장 수: {len(stores)}")
        return stores
    except Exception as e:
        print(f"[Scraper] [Error] '{sido_name}' 매장 조회 실패: {e}")
        return []


def main_scraper():
    print("[Scraper] 스타벅스 전국 매장 정보 수집 파이프라인을 시작합니다.")

    # 1. 전국 시도 목록 조회
    sido_list = get_sido_list()
    if not sido_list:
        print("[Scraper] [Error] 시도 코드가 존재하지 않아 수집을 중단합니다.")
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
        print("[Scraper] [Warning] 수집된 매장 데이터가 없습니다.")
        return

    # 3. 데이터프레임 변환 및 컬럼 정제 (범용 5대 속성 매핑)
    # name: 매장명, category: 시도명, value_1: 위도, value_2: 경도, detail_text: 도로명주소
    collected_data = []
    for idx, store in enumerate(all_stores, start=1):
        try:
            lat_val = float(store.get('lat', 0.0))
            lng_val = float(store.get('lng', 0.0))
        except ValueError:
            lat_val = 0.0
            lng_val = 0.0

        collected_data.append({
            "순위": idx,
            "name": store.get('s_name', '').strip(),
            "category": store.get('sido_name', '').strip(),
            "value_1": lat_val,
            "value_2": lng_val,
            "detail_text": store.get('doro_address', '').strip()
        })

    df = pd.DataFrame(collected_data)
    df = df.drop_duplicates(subset=['name', 'detail_text'])

    # 4. 결과 저장
    script_dir = os.path.dirname(os.path.abspath(__file__))
    output_path = os.path.join(script_dir, '..', 'data', 'starbucks_bestseller.csv')
    
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    # 엑셀 깨짐 방지를 위해 'utf-8-sig' 인코딩 지정
    df.to_csv(output_path, index=False, encoding='utf-8-sig')
    
    # 출력 경로를 워크스페이스 기준 상대 경로로 변환
    workspace_root = os.path.abspath(os.path.join(script_dir, '..', '..'))
    rel_output_path = os.path.relpath(output_path, workspace_root).replace('\\', '/')
    print(f"[Scraper] [Success] 총 {len(df)}건 데이터가 {rel_output_path} 에 성공적으로 적재 완료되었습니다.")


if __name__ == '__main__':
    main_scraper()
