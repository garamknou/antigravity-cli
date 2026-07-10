# -*- coding: utf-8 -*-
"""
starbucks 데이터 탐색적 데이터 분석(EDA) 및 시각화 스크립트 템플릿

이 스크립트는 수집된 CSV 데이터를 로드하여 데이터 무결성을 검증하고 결측치/기술통계를 분석하며,
5대 공통 범용 속성(name, category, value_1, value_2, detail_text) 기준으로
11가지 시각화 차트 이미지(일변량, 이변량, 다변량)를 생성하여 저장합니다.
또한 scikit-learn TF-IDF Vectorizer를 통해 detail_text 텍스트의 중요 키워드를 추출합니다.

치환 대상 변수:
- PROJECT_NAME: starbucks
- CSV_PATH: starbucks/data/starbucks_bestseller.csv
- IMAGE_DIR: starbucks/images
- TXT_REPORT_PATH: starbucks/docs/basic_statistics.txt
- TFIDF_CSV_PATH: starbucks/docs/tfidf_keywords.csv

작성자: Antigravity AI Data Pipeline Framework
"""

import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.feature_extraction.text import TfidfVectorizer
import koreanize_matplotlib

def run_eda():
    csv_path = "starbucks/data/starbucks_bestseller.csv"
    image_dir = "starbucks/images"
    txt_report_path = "starbucks/docs/basic_statistics.txt"
    tfidf_csv_path = "starbucks/docs/tfidf_keywords.csv"
    
    os.makedirs(image_dir, exist_ok=True)
    os.makedirs(os.path.dirname(txt_report_path), exist_ok=True)
    os.makedirs(os.path.dirname(tfidf_csv_path), exist_ok=True)
    
    print(f"[EDA] 데이터를 로드합니다: {csv_path}")
    if not os.path.exists(csv_path):
        print(f"[Error] CSV 파일이 존재하지 않습니다: {csv_path}")
        return
        
    df = pd.read_csv(csv_path)
    
    # 2. 기초 정보 출력 및 임시 로그 저장
    print("\n=== 데이터 기본 구조 ===")
    print(f"행 수: {df.shape[0]}, 열 수: {df.shape[1]}")
    print(f"중복 행 수: {df.duplicated().sum()}")
    
    # 결측치 확인
    print("\n=== 결측치 정보 ===")
    missing_info = df.isnull().sum()
    print(missing_info)
    
    # 수치형 변수 통계
    print("\n=== 수치형 기술통계 ===")
    desc_num = df.describe()
    print(desc_num)
    
    # 범주형 변수 통계
    print("\n=== 범주형 기술통계 ===")
    desc_cat = df.describe(include=['object']) if df.select_dtypes(include=['object']).shape[1] > 0 else pd.DataFrame()
    print(desc_cat)
    
    # 텍스트 파일로 기초 통계정보 저장
    with open(txt_report_path, "w", encoding="utf-8") as f:
        f.write("=== 기초 데이터 정보 ===\n")
        f.write(f"전체 데이터 행 수: {df.shape[0]}\n")
        f.write(f"전체 데이터 열 수: {df.shape[1]}\n")
        f.write(f"중복 행 수: {df.duplicated().sum()}\n\n")
        f.write("=== 결측치 수 ===\n")
        f.write(missing_info.to_string())
        f.write("\n\n=== 수치형 기술통계 ===\n")
        f.write(desc_num.to_string())
        if not desc_cat.empty:
            f.write("\n\n=== 범주형 기술통계 ===\n")
            f.write(desc_cat.to_string())
        
    print(f"[EDA] 기초 통계 로그가 저장되었습니다: {txt_report_path}")
    
    # ==================== 시각화 파트 ====================
    # 1. value_1 분포 (일변량 1)
    if 'value_1' in df.columns:
        plt.figure(figsize=(8, 5))
        # 숫자형 변환 가드
        val1_numeric = pd.to_numeric(df['value_1'], errors='coerce').dropna()
        if not val1_numeric.empty:
            plt.hist(val1_numeric, bins=20, color='skyblue', edgecolor='black', alpha=0.7)
            plt.title('value_1(수치 1) 분포 히스토그램')
            plt.xlabel('value_1')
            plt.ylabel('수량')
            plt.grid(axis='y', linestyle='--', alpha=0.7)
            plt.tight_layout()
            plt.savefig(f"{image_dir}/01_price_histogram.png")
            plt.close()
        
    # 2. value_2 분포 (일변량 2)
    if 'value_2' in df.columns:
        plt.figure(figsize=(8, 5))
        val2_numeric = pd.to_numeric(df['value_2'], errors='coerce').dropna()
        if not val2_numeric.empty:
            plt.hist(val2_numeric, bins=20, color='salmon', edgecolor='black', alpha=0.7)
            plt.title('value_2(수치 2) 분포 히스토그램')
            plt.xlabel('value_2')
            plt.ylabel('수량')
            plt.grid(axis='y', linestyle='--', alpha=0.7)
            plt.tight_layout()
            plt.savefig(f"{image_dir}/02_sale_price_histogram.png")
            plt.close()
    
    # 3. 순위 또는 인덱스 평점 분포 (일변량 3)
    if 'value_2' in df.columns:
        plt.figure(figsize=(8, 5))
        val2_numeric = pd.to_numeric(df['value_2'], errors='coerce').dropna()
        if not val2_numeric.empty:
            plt.hist(val2_numeric, bins=15, color='gold', edgecolor='black', alpha=0.7)
            plt.title('만족도 지표(value_2) 상세 분포')
            plt.xlabel('value_2')
            plt.ylabel('수량')
            plt.grid(axis='y', linestyle='--', alpha=0.7)
            plt.tight_layout()
            plt.savefig(f"{image_dir}/03_rating_distribution.png")
            plt.close()
        
    # 4. 수치 2 상자그림 (일변량 4)
    if 'value_2' in df.columns:
        val2_numeric = pd.to_numeric(df['value_2'], errors='coerce').dropna()
        if not val2_numeric.empty:
            plt.figure(figsize=(8, 5))
            plt.boxplot(val2_numeric, vert=False, patch_artist=True, 
                        boxprops=dict(facecolor='lightgreen', color='black'),
                        medianprops=dict(color='red'))
            plt.title('value_2 상자그림(Boxplot)')
            plt.xlabel('value_2 값')
            plt.grid(axis='x', linestyle='--', alpha=0.7)
            plt.tight_layout()
            plt.savefig(f"{image_dir}/04_review_count_boxplot.png")
            plt.close()
        
    # 5. 상위 10개 category 빈도 (일변량 5)
    if 'category' in df.columns:
        cat_counts = df['category'].value_counts().head(10)
        plt.figure(figsize=(10, 6))
        cat_counts.plot(kind='barh', color='orchid', edgecolor='black', alpha=0.8)
        plt.title('상위 10개 category(그룹) 점유 빈도')
        plt.xlabel('수량')
        plt.ylabel('카테고리명')
        plt.gca().invert_yaxis()
        plt.grid(axis='x', linestyle='--', alpha=0.7)
        plt.tight_layout()
        plt.savefig(f"{image_dir}/05_top_publishers.png")
        plt.close()
    
    # 6. 상위 10개 name 빈도 또는 고유값 점유율 (일변량 6)
    if 'name' in df.columns:
        name_counts = df['name'].value_counts().head(10)
        plt.figure(figsize=(10, 6))
        name_counts.plot(kind='barh', color='teal', edgecolor='black', alpha=0.8)
        plt.title('상위 10개 고유 name 빈도')
        plt.xlabel('노출 수')
        plt.ylabel('이름')
        plt.gca().invert_yaxis()
        plt.grid(axis='x', linestyle='--', alpha=0.7)
        plt.tight_layout()
        plt.savefig(f"{image_dir}/06_top_authors.png")
        plt.close()
        
    # 7. value_1 vs value_2 산점도 (이변량 1)
    if 'value_1' in df.columns and 'value_2' in df.columns:
        v1 = pd.to_numeric(df['value_1'], errors='coerce')
        v2 = pd.to_numeric(df['value_2'], errors='coerce')
        valid_idx = v1.notnull() & v2.notnull()
        if valid_idx.any():
            plt.figure(figsize=(8, 6))
            plt.scatter(v1[valid_idx], v2[valid_idx], color='blue', alpha=0.5, edgecolor='none')
            plt.title('value_1 대비 value_2 상관 산점도')
            plt.xlabel('value_1')
            plt.ylabel('value_2')
            plt.grid(True, linestyle='--', alpha=0.5)
            plt.tight_layout()
            plt.savefig(f"{image_dir}/07_price_vs_sale_price.png")
            plt.close()
        
    # 8. value_2 상세관계 산점도 (이변량 2)
    if 'value_2' in df.columns:
        v2 = pd.to_numeric(df['value_2'], errors='coerce').dropna()
        if not v2.empty:
            plt.figure(figsize=(8, 6))
            plt.scatter(df.index, df['value_2'], color='darkorange', alpha=0.6, edgecolor='black')
            plt.title('데이터 인덱스 대비 value_2 산포도')
            plt.xlabel('Index')
            plt.ylabel('value_2')
            plt.grid(True, linestyle='--', alpha=0.5)
            plt.tight_layout()
            plt.savefig(f"{image_dir}/08_rating_vs_reviews.png")
            plt.close()
        
    # 9. 상위 10개 category별 평균 value_2 분포 (이변량 3)
    if 'category' in df.columns and 'value_2' in df.columns:
        top_cats = df['category'].value_counts().head(10).index
        df_top_cats = df[df['category'].isin(top_cats)].copy()
        df_top_cats['value_2'] = pd.to_numeric(df_top_cats['value_2'], errors='coerce')
        df_top_cats = df_top_cats.dropna(subset=['value_2'])
        if not df_top_cats.empty:
            plt.figure(figsize=(12, 6))
            sns.boxplot(x='category', y='value_2', data=df_top_cats, hue='category', legend=False, palette='Set3')
            plt.title('상위 10개 category별 value_2 수치 분포')
            plt.xticks(rotation=45)
            plt.xlabel('Category')
            plt.ylabel('value_2')
            plt.grid(axis='y', linestyle='--', alpha=0.7)
            plt.tight_layout()
            plt.savefig(f"{image_dir}/09_publisher_rating_boxplot.png")
            plt.close()
            
    # 10. 상관관계 히트맵 (다변량 1)
    numeric_cols = []
    for col in ['순위', 'value_1', 'value_2']:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce')
            numeric_cols.append(col)
    
    if len(numeric_cols) >= 2:
        corr_matrix = df[numeric_cols].corr()
        plt.figure(figsize=(8, 6))
        sns.heatmap(corr_matrix, annot=True, cmap='coolwarm', fmt=".3f", linewidths=.5, cbar=True)
        plt.title('수치형 변수 간 상관계수 히트맵')
        plt.tight_layout()
        plt.savefig(f"{image_dir}/10_correlation_heatmap.png")
        plt.close()
        
    # 11. detail_text 텍스트 중요 키워드 TF-IDF 분석
    if 'detail_text' in df.columns:
        descriptions = df['detail_text'].dropna().tolist()
        if descriptions:
            stop_words_korean = ['이', '그', '저', '것', '수', '등', '및', '를', '을', '에', '의', '은', '는', '도', '으로', '로', '한다', '있다', '대한', '위한', '통해', '에서', '하여', '따라', '책은', '가장', '다양한', '제시하며', '제공하며']
            
            try:
                vectorizer = TfidfVectorizer(max_features=30, stop_words=stop_words_korean, min_df=1)
                tfidf_matrix = vectorizer.fit_transform(descriptions)
                mean_tfidf = np.asarray(tfidf_matrix.mean(axis=0)).ravel()
                features = vectorizer.get_feature_names_out()
                
                tfidf_df = pd.DataFrame({'keyword': features, 'tfidf_weight': mean_tfidf})
                tfidf_df = tfidf_df.sort_values(by='tfidf_weight', ascending=False)
                tfidf_df.to_csv(tfidf_csv_path, index=False, encoding="utf-8-sig")
                
                plt.figure(figsize=(10, 8))
                plt.barh(tfidf_df['keyword'].head(15), tfidf_df['tfidf_weight'].head(15), color='darkgrey', edgecolor='black', alpha=0.8)
                plt.title('detail_text 본문 핵심 키워드 중요도 (TF-IDF 상위 15개)')
                plt.xlabel('평균 TF-IDF 가중치')
                plt.ylabel('핵심 키워드')
                plt.gca().invert_yaxis()
                plt.grid(axis='x', linestyle='--', alpha=0.7)
                plt.tight_layout()
                plt.savefig(f"{image_dir}/11_tfidf_keywords_bar.png")
                plt.close()
            except Exception as e:
                print(f"[Warning] TF-IDF 키워드 분석 중 오류 발생: {e}")
                
    print("[EDA] 모든 시각화 분석 및 시각화 이미지 생성이 완료되었습니다.")

if __name__ == "__main__":
    run_eda()
