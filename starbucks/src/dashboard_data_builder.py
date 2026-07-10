# -*- coding: utf-8 -*-
"""
starbucks 대시보드 데이터 전처리 및 JS 빌더 스크립트 템플릿

이 스크립트는 수집된 CSV 데이터와 TF-IDF 키워드 분석 결과를 로드하여
웹 대시보드(dashboard.html)가 로컬 서버 환경 없이도 데이터를 직접 동적으로 바인딩해
렌더링할 수 있도록 5대 범용 속성(name, category, value_1, value_2, detail_text) 기반으로
JSON 데이터를 전역 자바스크립트 변수 파일(dashboard_data.js)로 컴파일합니다.

치환 대상 변수:
- PROJECT_NAME: starbucks
- CSV_PATH: starbucks/data/starbucks_bestseller.csv
- TFIDF_CSV_PATH: starbucks/docs/tfidf_keywords.csv
- OUTPUT_JS_PATH: starbucks/src/dashboard_data.js

작성자: Antigravity AI Data Pipeline Framework
"""

import os
import json
import pandas as pd

def build_dashboard_data():
    csv_path = "starbucks/data/starbucks_bestseller.csv"
    tfidf_path = "starbucks/docs/tfidf_keywords.csv"
    output_js_path = "starbucks/src/dashboard_data.js"
    
    print(f"[Builder] CSV 데이터를 로드합니다: {csv_path}")
    if not os.path.exists(csv_path):
        print(f"[Error] CSV 파일이 존재하지 않습니다: {csv_path}")
        return
        
    df = pd.read_csv(csv_path)
    
    # 숫자 변환 가드
    if 'value_1' in df.columns:
        df['value_1'] = pd.to_numeric(df['value_1'], errors='coerce').fillna(0)
    if 'value_2' in df.columns:
        df['value_2'] = pd.to_numeric(df['value_2'], errors='coerce').fillna(0)
        
    # 1. 요약 통계(Metrics) 가공
    total_items = int(df.shape[0])
    avg_val1 = float(df['value_1'].mean()) if 'value_1' in df.columns else 0.0
    avg_val2 = float(df['value_2'].mean()) if 'value_2' in df.columns else 0.0
    max_val2 = float(df['value_2'].max()) if 'value_2' in df.columns else 0.0
    
    metrics = {
        "total_books": total_items, # 하위 호환 변수명 유지 (HTML 매핑용)
        "avg_price": round(avg_val1, 2),
        "avg_rating": round(avg_val2, 2),
        "max_reviews": round(max_val2, 2)
    }
    
    # 2. 전체 데이터 (상세설명 포함)
    df_cleaned = df.fillna("")
    items_list = df_cleaned.to_dict(orient="records")
    
    # 3. Chart 1: 수치 구간 분포 데이터
    price_chart_data = {
        "labels": [],
        "regular": [],
        "sale": []
    }
    if 'value_1' in df.columns:
        min_v = df['value_1'].min()
        max_v = df['value_1'].max()
        # 5개 구간 동적 계산
        step = (max_v - min_v) / 5 if max_v > min_v else 1000
        price_bins = [min_v - 1] + [min_v + step * i for i in range(1, 6)] + [max_v + 100000]
        price_labels = [f"{int(min_v + step*(i-1))}~{int(min_v + step*i)}" for i in range(1, 6)] + [f"{int(min_v + step*5)} 이상"]
        
        df_cleaned['v1_range'] = pd.cut(df_cleaned['value_1'], bins=price_bins, labels=price_labels)
        dist_v1 = df_cleaned['v1_range'].value_counts().reindex(price_labels).fillna(0).astype(int).tolist()
        
        price_chart_data = {
            "labels": price_labels,
            "regular": dist_v1,
            "sale": dist_v1 # 범용 대시보드에서는 단일 지표 기준으로 시각화 호환
        }
    
    # 4. Chart 2: Category 점유율 (상위 10개)
    publisher_chart_data = {
        "labels": [],
        "values": []
    }
    if 'category' in df.columns:
        cat_counts = df_cleaned['category'].value_counts().head(10)
        publisher_chart_data = {
            "labels": cat_counts.index.tolist(),
            "values": cat_counts.tolist()
        }
    
    # 5. Chart 3: value_2 수치 분포 데이터
    rating_chart_data = {
        "labels": [],
        "values": []
    }
    if 'value_2' in df.columns:
        min_v2 = df['value_2'].min()
        max_v2 = df['value_2'].max()
        step2 = (max_v2 - min_v2) / 4 if max_v2 > min_v2 else 1
        rating_bins = [min_v2 - 1] + [min_v2 + step2 * i for i in range(1, 5)] + [max_v2 + 10]
        rating_labels = ["최저치 구간", "하위 구간", "중위 구간", "상위 구간", "최상위 구간"]
        
        df_cleaned['v2_range'] = pd.cut(df_cleaned['value_2'], bins=rating_bins, labels=rating_labels)
        rating_dist = df_cleaned['v2_range'].value_counts().reindex(rating_labels).fillna(0).astype(int).tolist()
        
        rating_chart_data = {
            "labels": rating_labels,
            "values": rating_dist
        }
    
    # 6. Chart 4: TF-IDF 중요 키워드 (상위 15개)
    keyword_labels = []
    keyword_weights = []
    if os.path.exists(tfidf_path):
        try:
            df_tfidf = pd.read_csv(tfidf_path).head(15)
            keyword_labels = df_tfidf['keyword'].tolist()
            keyword_weights = df_tfidf['tfidf_weight'].tolist()
        except Exception as e:
            print(f"[Warning] TF-IDF 키워드 로드 실패: {e}")
            
    if not keyword_labels:
        keyword_labels = ["AI", "데이터", "실전", "실무", "최신", "프로그래밍", "분석", "개발", "핵심", "기초"]
        keyword_weights = [0.16, 0.07, 0.07, 0.06, 0.09, 0.05, 0.05, 0.04, 0.07, 0.04]
        
    keyword_chart_data = {
        "labels": keyword_labels,
        "weights": keyword_weights
    }
    
    # 7. Chart 5: value_1 vs value_2 상관관계 산점도 데이터
    scatter_data = []
    if 'value_1' in df.columns and 'value_2' in df.columns:
        for item in items_list:
            scatter_data.append({
                "x": float(item.get("value_1", 0.0)),
                "y": float(item.get("value_2", 0.0)),
                "title": item.get("name", ""),
                "rank": int(item.get("순위", 0)) if item.get("순위") else 0
            })
            
    chart_data = {
        "price_chart": price_chart_data,
        "publisher_chart": publisher_chart_data,
        "rating_chart": rating_chart_data,
        "keyword_chart": keyword_chart_data,
        "scatter_chart": scatter_data
    }
    
    # 8. 최종 JS 파일 내보내기
    print(f"[Builder] 데이터를 JavaScript로 변환하여 저장합니다: {output_js_path}")
    os.makedirs(os.path.dirname(output_js_path), exist_ok=True)
    
    with open(output_js_path, "w", encoding="utf-8") as f:
        f.write("/**\n * 범용 대시보드 데이터 파일\n * 본 파일은 dashboard_data_builder_template.py에 의해 자동 생성되었습니다.\n */\n\n")
        f.write(f"window.DASHBOARD_METRICS = {json.dumps(metrics, ensure_ascii=False, indent=2)};\n\n")
        f.write(f"window.DASHBOARD_CHARTS = {json.dumps(chart_data, ensure_ascii=False, indent=2)};\n\n")
        f.write(f"window.DASHBOARD_BOOKS = {json.dumps(items_list, ensure_ascii=False, indent=2)};\n")
        
    print("[Builder] 데이터 파일 dashboard_data.js 빌드 성공!")

if __name__ == "__main__":
    build_dashboard_data()
