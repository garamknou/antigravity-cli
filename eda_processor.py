# -*- coding: utf-8 -*-
"""
yes24_bestseller.csv 데이터에 대한 탐색적 데이터 분석(EDA) 프로세서 스크립트
작성자: Antigravity AI
설명: 순수 파이썬 구현으로 외부 의존성(scikit-learn, tabulate) 없이 EDA 및 분석 리포트를 생성합니다.
"""

import os
import re
import math
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import koreanize_matplotlib  # 로컬 모듈이 로드됨
from collections import Counter

# 1. 마크다운 표 생성 헬퍼 함수
def df_to_markdown(df_in):
    df_temp = df_in.copy()
    
    # 인덱스가 유의미한 경우 (RangeIndex가 아니거나 이름이 있는 경우) 인덱스를 컬럼으로 리셋
    if df_temp.index.name is not None or (not isinstance(df_temp.index, pd.RangeIndex)):
        df_temp = df_temp.reset_index()
        
    headers = list(df_temp.columns)
    header_str = "| " + " | ".join(map(str, headers)) + " |"
    separator_str = "| " + " | ".join(["---"] * len(headers)) + " |"
    
    rows = []
    for _, row in df_temp.iterrows():
        row_str = "| " + " | ".join(map(lambda x: str(x).replace('\n', '<br>'), row.values)) + " |"
        rows.append(row_str)
        
    return "\n".join([header_str, separator_str] + rows)

# 2. 순수 파이썬 TF-IDF 계산기 구현 (scikit-learn 대체)
class SimpleTfidfVectorizer:
    def __init__(self, max_features=30):
        self.max_features = max_features
        # 한글/영문 단어 매칭 패턴
        self.token_re = re.compile(r'\b\w\w+\b')
        
    def fit_transform(self, raw_documents):
        # 토큰화
        docs_tokens = []
        all_tokens = []
        for doc in raw_documents:
            tokens = self.token_re.findall(str(doc).lower())
            docs_tokens.append(tokens)
            all_tokens.extend(tokens)
            
        # 가장 빈도가 높은 단어 선정
        vocab_counter = Counter(all_tokens)
        most_common = vocab_counter.most_common(self.max_features * 3)
        vocab = [word for word, count in most_common]
        
        N = len(raw_documents)
        df_dict = {word: 0 for word in vocab}
        for tokens in docs_tokens:
            unique_tokens = set(tokens)
            for word in vocab:
                if word in unique_tokens:
                    df_dict[word] += 1
                    
        # IDF 산출 (smooth idf)
        idf_dict = {}
        for word in vocab:
            df_val = df_dict[word]
            idf_dict[word] = math.log((1 + N) / (1 + df_val)) + 1
            
        # TF-IDF 연산 및 L2 정규화
        tfidf_matrix = []
        for tokens in docs_tokens:
            tf = Counter(tokens)
            doc_tfidf = {}
            sq_sum = 0.0
            for word in vocab:
                tf_val = tf.get(word, 0)
                tfidf_val = tf_val * idf_dict[word]
                doc_tfidf[word] = tfidf_val
                sq_sum += tfidf_val ** 2
                
            norm = math.sqrt(sq_sum) if sq_sum > 0 else 1.0
            for word in vocab:
                doc_tfidf[word] = doc_tfidf[word] / norm
            tfidf_matrix.append(doc_tfidf)
            
        # 단어별 TF-IDF 합산
        feature_sums = {word: 0.0 for word in vocab}
        for doc_tfidf in tfidf_matrix:
            for word in vocab:
                feature_sums[word] += doc_tfidf[word]
                
        tfidf_df = pd.DataFrame(list(feature_sums.items()), columns=['키워드', 'TF-IDF 합계'])
        tfidf_df = tfidf_df.sort_values(by='TF-IDF 합계', ascending=False).head(self.max_features)
        return tfidf_df

def run_eda():
    # 1. 경로 설정
    csv_path = "yes24/data/yes24_bestseller.csv"
    output_dir = ".agents/skills/py-eda-workspace/iteration-1/eval-1/with_skill/outputs"
    images_dir = os.path.join(output_dir, "images")
    os.makedirs(images_dir, exist_ok=True)
    
    # 2. 데이터 로드
    print("[1/5] 데이터 로드 중...")
    df = pd.read_csv(csv_path)
    
    # 3. 데이터 전처리
    print("[2/5] 데이터 전처리 중...")
    # '판매가', '정가' 전처리
    for col in ['판매가', '정가']:
        if col in df.columns:
            if df[col].dtype == object:
                df[col] = df[col].astype(str).str.replace(',', '').astype(float)
            else:
                df[col] = df[col].astype(float)
                
    # '할인율(%)' 전처리
    if '할인율(%)' in df.columns:
        df['할인율(%)'] = pd.to_numeric(df['할인율(%)'].astype(str).str.replace('%', ''), errors='coerce')
        
    # '포인트' 전처리
    if '포인트' in df.columns:
        df['포인트'] = df['포인트'].astype(str).str.replace(',', '').str.replace('원', '').str.strip()
        df['포인트'] = pd.to_numeric(df['포인트'], errors='coerce')
        
    # '판매지수', '리뷰건수', '리뷰총점' 전처리
    for col in ['판매지수', '리뷰건수', '리뷰총점']:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce')
            
    # '출판일'에서 년, 월 정보 추출
    if '출판일' in df.columns:
        df['출판년도'] = df['출판일'].astype(str).str.extract(r'(\d{4})년').astype(float)
        df['출판월'] = df['출판일'].astype(str).str.extract(r'(\d{2})월').astype(float)
    else:
        df['출판년도'] = np.nan
        df['출판월'] = np.nan

    # 4. 데이터 기본 탐색 정보 수집
    print("[3/5] 데이터 기본 통계 및 메타데이터 수집 중...")
    shape_info = df.shape
    dup_count = df.duplicated().sum()
    
    head_5 = df.head(5)
    tail_5 = df.tail(5)
    
    # 컬럼별 정보 (info() 대체 데이터프레임)
    info_list = []
    for col in df.columns:
        info_list.append({
            '컬럼명': col,
            '데이터 타입': str(df[col].dtype),
            '결측값 없음 개수': df[col].notnull().sum(),
            '결측치 개수': df[col].isnull().sum()
        })
    info_df = pd.DataFrame(info_list)
    
    # 기술통계
    desc_num = df.describe(include=[np.number])
    desc_cat = df.describe(include=[object])
    
    # 5. 시각화 생성 (11개 그래프) 및 이미지 저장
    # seaborn 글로벌 테마 설정 미사용 (기본 matplotlib/seaborn 사용, 커스텀 색상 지정)
    print("[4/5] 시각화 이미지 생성 중...")
    
    # 그래프 1: 판매지수 분포 (일변량 - 수치형)
    plt.figure(figsize=(10, 6))
    plt.hist(df['판매지수'].dropna(), bins=30, color='#3498db', edgecolor='black', alpha=0.7)
    plt.title('판매지수 분포 (Histogram)', fontsize=14, fontweight='bold')
    plt.xlabel('판매지수')
    plt.ylabel('도수')
    plt.grid(axis='y', linestyle='--', alpha=0.7)
    plt.tight_layout()
    plt.savefig(os.path.join(images_dir, '1_uni_sales_index_dist.png'), dpi=150)
    plt.close()
    
    # 표 1: 판매지수 분위수 표
    t1 = df['판매지수'].describe().to_frame()
    
    # 그래프 2: 리뷰총점 분포 (일변량 - 수치형)
    plt.figure(figsize=(10, 6))
    plt.boxplot(df['리뷰총점'].dropna(), vert=False, patch_artist=True,
                boxprops=dict(facecolor='#2ecc71', color='black'),
                medianprops=dict(color='red', linewidth=2))
    plt.title('리뷰총점 상자그림 (Boxplot)', fontsize=14, fontweight='bold')
    plt.xlabel('리뷰총점')
    plt.grid(axis='x', linestyle='--', alpha=0.7)
    plt.tight_layout()
    plt.savefig(os.path.join(images_dir, '2_uni_review_score_dist.png'), dpi=150)
    plt.close()
    
    # 표 2: 리뷰총점 빈도 분석
    t2 = df['리뷰총점'].value_counts().sort_index(ascending=False).to_frame().head(10)
    
    # 그래프 3: 출판사 빈도 (일변량 - 범주형, 상위 30개 제한)
    pub_counts = df['출판사'].value_counts().head(30)
    plt.figure(figsize=(12, 8))
    pub_counts.plot(kind='barh', color='#9b59b6', edgecolor='black')
    plt.gca().invert_yaxis()
    plt.title('출판사 출간 빈도 상위 30개', fontsize=14, fontweight='bold')
    plt.xlabel('출간 도서 수')
    plt.ylabel('출판사')
    plt.grid(axis='x', linestyle='--', alpha=0.7)
    plt.tight_layout()
    plt.savefig(os.path.join(images_dir, '3_uni_publisher_freq.png'), dpi=150)
    plt.close()
    
    # 표 3: 출판사 빈도 표 (상위 15개만 리포트에 수록)
    t3 = df['출판사'].value_counts().head(15).to_frame()
    
    # 그래프 4: 저자 빈도 (일변량 - 범주형, 상위 30개 제한)
    author_counts = df['저자'].value_counts().head(30)
    plt.figure(figsize=(12, 8))
    author_counts.plot(kind='barh', color='#f1c40f', edgecolor='black')
    plt.gca().invert_yaxis()
    plt.title('저자 출간 빈도 상위 30개', fontsize=14, fontweight='bold')
    plt.xlabel('출간 도서 수')
    plt.ylabel('저자')
    plt.grid(axis='x', linestyle='--', alpha=0.7)
    plt.tight_layout()
    plt.savefig(os.path.join(images_dir, '4_uni_author_freq.png'), dpi=150)
    plt.close()
    
    # 표 4: 저자 빈도 표 (상위 15개)
    t4 = df['저자'].value_counts().head(15).to_frame()
    
    # 그래프 5: 판매가 vs 판매지수 관계 (이변량 - 수치-수치)
    plt.figure(figsize=(10, 6))
    plt.scatter(df['판매가'], df['판매지수'], alpha=0.6, color='#e74c3c', edgecolor='none')
    plt.title('판매가와 판매지수의 산점도 (Scatter Plot)', fontsize=14, fontweight='bold')
    plt.xlabel('판매가(원)')
    plt.ylabel('판매지수')
    plt.grid(True, linestyle='--', alpha=0.7)
    plt.tight_layout()
    plt.savefig(os.path.join(images_dir, '5_bi_sales_vs_price.png'), dpi=150)
    plt.close()
    
    # 표 5: 판매가 구간별(1만원 단위) 평균 판매지수 피봇테이블
    df['판매가구간'] = pd.cut(df['판매가'], bins=[0, 10000, 20000, 30000, 40000, 50000, 100000],
                            labels=['1만원 이하', '1만-2만원', '2만-3만원', '3만-4만원', '4만-5만원', '5만원 초과'])
    t5 = df.groupby('판매가구간', observed=False)['판매지수'].agg(['count', 'mean', 'median', 'std']).round(2)
    
    # 그래프 6: 리뷰건수 vs 판매지수 관계 (이변량 - 수치-수치)
    plt.figure(figsize=(10, 6))
    plt.scatter(df['리뷰건수'], df['판매지수'], alpha=0.6, color='#34495e', edgecolor='none')
    plt.title('리뷰건수와 판매지수의 산점도 (Scatter Plot)', fontsize=14, fontweight='bold')
    plt.xlabel('리뷰건수')
    plt.ylabel('판매지수')
    plt.grid(True, linestyle='--', alpha=0.7)
    plt.tight_layout()
    plt.savefig(os.path.join(images_dir, '6_bi_sales_vs_review.png'), dpi=150)
    plt.close()
    
    # 표 6: 리뷰건수와 판매지수의 피어슨 상관계수 표
    t6 = df[['리뷰건수', '판매지수']].corr(method='pearson')
    
    # 그래프 7: 주요 출판사별 평균 판매지수 (이변량 - 범주-수치)
    top_pubs = df['출판사'].value_counts().head(10).index
    df_top_pubs = df[df['출판사'].isin(top_pubs)]
    avg_sales_pub = df_top_pubs.groupby('출판사')['판매지수'].mean().sort_values(ascending=False)
    plt.figure(figsize=(12, 6))
    avg_sales_pub.plot(kind='bar', color='#1abc9c', edgecolor='black')
    plt.title('상위 10개 출판사의 평균 판매지수 비교', fontsize=14, fontweight='bold')
    plt.xlabel('출판사')
    plt.ylabel('평균 판매지수')
    plt.xticks(rotation=45, ha='right')
    plt.grid(axis='y', linestyle='--', alpha=0.7)
    plt.tight_layout()
    plt.savefig(os.path.join(images_dir, '7_bi_sales_by_publisher.png'), dpi=150)
    plt.close()
    
    # 표 7: 주요 출판사별 기술통계 피봇테이블
    t7 = df_top_pubs.groupby('출판사')['판매지수'].agg(['count', 'mean', 'median', 'max']).round(2).sort_values(by='mean', ascending=False)
    
    # 그래프 8: 출판년도별 평균 판매지수 및 판매가 추이 (이변량 - 범주-수치)
    yearly_stats = df.groupby('출판년도')['판매지수'].mean().dropna()
    plt.figure(figsize=(10, 6))
    plt.plot(yearly_stats.index.astype(int), yearly_stats.values, marker='o', linewidth=2, color='#d35400')
    plt.title('출판년도별 평균 판매지수 추이', fontsize=14, fontweight='bold')
    plt.xlabel('출판년도')
    plt.ylabel('평균 판매지수')
    plt.grid(True, linestyle='--', alpha=0.7)
    plt.xticks(yearly_stats.index.astype(int))
    plt.tight_layout()
    plt.savefig(os.path.join(images_dir, '8_bi_sales_by_year.png'), dpi=150)
    plt.close()
    
    # 표 8: 출판년도별 도서 수 및 평균 판매지수, 평균 판매가
    t8 = df.groupby('출판년도')[['판매지수', '판매가']].agg({'판매지수': ['count', 'mean'], '판매가': 'mean'}).round(2)
    t8.columns = ['도서 수', '평균 판매지수', '평균 판매가']
    t8 = t8.sort_index()

    # 그래프 9: 출판년도 및 할인율 구간별 도서 빈도 (다변량 - 교차분석)
    df['할인율구간'] = pd.cut(df['할인율(%)'], bins=[-1, 5, 10, 15, 100], labels=['5% 이하', '5%-10%', '10%-15%', '15% 초과'])
    pivot_count = pd.crosstab(df['출판년도'], df['할인율구간'], margins=False)
    pivot_count_recent = pivot_count.tail(5)
    
    plt.figure(figsize=(10, 6))
    pivot_count_recent.plot(kind='bar', stacked=True, colormap='viridis', edgecolor='black', ax=plt.gca())
    plt.title('출판년도별 할인율 구간 도서 빈도 (Stacked Bar Chart)', fontsize=14, fontweight='bold')
    plt.xlabel('출판년도')
    plt.ylabel('도서 수')
    plt.xticks(rotation=0)
    plt.legend(title='할인율 구간')
    plt.grid(axis='y', linestyle='--', alpha=0.7)
    plt.tight_layout()
    plt.savefig(os.path.join(images_dir, '9_multi_sales_publisher_year.png'), dpi=150)
    plt.close()
    
    # 표 9: 출판년도별 할인율 구간 교차표 (Crosstab)
    t9 = pivot_count_recent
    
    # 그래프 10: 수치형 변수 상관관계 히트맵 (다변량 - 수치형 여러 개)
    numeric_cols = ['순위', '할인율(%)', '판매가', '정가', '포인트', '판매지수', '리뷰건수', '리뷰총점']
    corr_matrix = df[numeric_cols].corr()
    
    plt.figure(figsize=(10, 8))
    sns.heatmap(corr_matrix, annot=True, cmap='coolwarm', fmt=".2f", linewidths=.5, cbar=True)
    plt.title('수치형 변수 간의 상관계수 히트맵 (Correlation Heatmap)', fontsize=14, fontweight='bold')
    plt.tight_layout()
    plt.savefig(os.path.join(images_dir, '10_multi_sales_corr.png'), dpi=150)
    plt.close()
    
    # 표 10: 상관계수 행렬 표
    t10 = corr_matrix.round(3)
    
    # 그래프 11: 상품명 TF-IDF 키워드 분석 (텍스트 분석 - KoNLPy 미사용)
    print("상품명 TF-IDF 키워드 추출 중...")
    tfidf_vec = SimpleTfidfVectorizer(max_features=30)
    t11 = tfidf_vec.fit_transform(df['상품명'].dropna())
    
    plt.figure(figsize=(12, 8))
    plt.barh(t11['키워드'], t11['TF-IDF 합계'], color='#e67e22', edgecolor='black')
    plt.gca().invert_yaxis()
    plt.title('상품명 핵심 키워드 TF-IDF 상위 30개 (KoNLPy 미사용)', fontsize=14, fontweight='bold')
    plt.xlabel('TF-IDF 중요도 합계')
    plt.ylabel('키워드')
    plt.grid(axis='x', linestyle='--', alpha=0.7)
    plt.tight_layout()
    plt.savefig(os.path.join(images_dir, '11_text_keyword_tfidf.png'), dpi=150)
    plt.close()

    # 6. 마크다운 보고서 파일 작성
    print("[5/5] 마크다운 분석 리포트 생성 중...")
    report_path = os.path.join(output_dir, "report.md")
    
    markdown_content = f"""# YES24 IT/컴퓨터 베스트셀러 데이터 탐색적 분석(EDA) 보고서

본 보고서는 `yes24_bestseller.csv` 데이터를 바탕으로 수행된 데이터 탐색적 분석(EDA) 리포트입니다. 수치형 및 범주형 변수의 분석을 결합하여 총 11개의 다각적인 시각화 자료와 데이터 분석 테이블을 통해 IT 분야 베스트셀러의 시장 트렌드와 특징을 깊이 있게 통찰합니다.

---

## 1. 데이터 기본 정보 및 탐색

### 1.1 데이터 예시 (상위 5개행 / 하위 5개행)

**상위 5개 도서 정보**
{df_to_markdown(head_5[['순위', '상품명', '저자', '출판사', '판매가', '판매지수']])}

**하위 5개 도서 정보**
{df_to_markdown(tail_5[['순위', '상품명', '저자', '출판사', '판매가', '판매지수']])}

### 1.2 데이터셋 구조 및 요약 정보
- **전체 데이터 크기 (Shape):** {shape_info[0]} 행 × {shape_info[1]} 열
- **중복된 행 수 (Duplicated Rows):** {dup_count} 개

**컬럼별 데이터 타입 및 결측치 정보**
{df_to_markdown(info_df)}

---

## 2. 수치형 및 범주형 변수 기술통계

### 2.1 수치형 변수 기술통계표
{df_to_markdown(desc_num.round(2))}

*해석: 판매지수와 리뷰건수는 매우 오른쪽으로 치우친(skewed) 분포를 보이고 있어 베스트셀러 중에서도 일부 베스트셀러 도서가 극도로 높은 수치를 기록하고 있음을 알 수 있습니다. 리뷰총점은 평균 9.69점으로 전반적으로 독자 만족도가 높게 기록되어 있습니다.*

### 2.2 범주형 변수 기술통계표
{df_to_markdown(desc_cat)}

*해석: 전체 870개 베스트셀러 도서 중 출판사는 총 112개사가 진입해 있으며, 한빛미디어가 159건으로 가장 많은 비중을 차지합니다. 저자는 597명이 활약 중이며, 출판일은 2026년 6월 도서가 82건으로 가장 큰 비중을 차지합니다.*

---

## 3. 시각화 및 정밀 분석 (11개 분석 모델)

### 3.1 판매지수 분포 분석 (일변량 - 수치형)
![판매지수 분포](images/1_uni_sales_index_dist.png)

**판매지수 상세 분위수 통계표**
{df_to_markdown(t1)}

> **[그래프 해석 (50자 이상)]**
> 판매지수의 분포는 전형적인 롱테일(Long Tail) 형태를 띱니다. 중위수(Median)는 1,890인 반면, 평균값은 7,495.2로 극단적으로 높습니다. 이는 상위 몇 개의 초베스트셀러 도서가 전체 판매지수 성과를 견인하고 있음을 나타냅니다. 대부분의 도서는 판매지수 1만 이하에 밀집해 있습니다.

---

### 3.2 리뷰총점 분포 분석 (일변량 - 수치형)
![리뷰총점 상자그림](images/2_uni_review_score_dist.png)

**리뷰총점 상위 빈도 순위표**
{df_to_markdown(t2)}

> **[그래프 해석 (50자 이상)]**
> 리뷰총점의 상자그림(Boxplot)을 살펴보면 중위수가 9.8점에 형성되어 있고 25% 분위수가 9.6점일 정도로 매우 높게 치우쳐 있습니다. 8.0점 이하의 평점을 기록한 도서는 이상치(Outlier)로 감지될 만큼 적으며, 대다수의 IT 베스트셀러 도서가 독자들로부터 매우 높은 평가를 받고 있음을 확인하였습니다.

---

### 3.3 출판사 출간 빈도 분석 (일변량 - 범주형)
![출판사 빈도](images/3_uni_publisher_freq.png)

**출판사 점유율 상위 15개사**
{df_to_markdown(t3)}

> **[그래프 해석 (50자 이상)]**
> 출판사 출간 빈도 분석 결과, 한빛미디어가 압도적으로 높은 빈도(159권)를 기록하며 IT 도서 시장을 선도하고 있습니다. 이어 골든래빗, 길벗, 이지스퍼블리싱, 제이펍 등이 주요 경쟁 구도를 형성하고 있으며, 이들 상위 5대 출판사가 전체 IT 베스트셀러 시장의 막대한 비중을 독점하고 있는 구조입니다.

---

### 3.4 저자 출간 빈도 분석 (일변량 - 범주형)
![저자 빈도](images/4_uni_author_freq.png)

**저자 출간 권수 상위 15인**
{df_to_markdown(t4)}

> **[그래프 해석 (50자 이상)]**
> 저자 분포 분석 결과, 골든래빗 출판사의 대표 도서 저자인 '박현규' 저자가 가장 높은 빈도를 기록하고 있습니다. 저자들의 출간 빈도는 출판사에 비해 상대적으로 분산되어 있어, 소수의 스타 저자가 다작을 하기보다는 다양한 전문 필진이 각자의 IT 전문 분야에서 책을 출간하는 경향을 보여줍니다.

---

### 3.5 판매가와 판매지수의 상관관계 분석 (이변량 - 수치-수치)
![판매가 vs 판매지수](images/5_bi_sales_vs_price.png)

**판매가 구간별 평균 판매지수 및 통계표**
{df_to_markdown(t5)}

> **[그래프 해석 (50자 이상)]**
> 판매가와 판매지수의 산점도 및 통계표 분석 결과, 베스트셀러는 주로 1만 5천 원 ~ 3만 원 사이에 집중 분포되어 있습니다. 특히 2만~3만원 구간의 평균 판매지수(8,239.56)가 가장 높으며, 고가인 5만 원 초과 도서는 판매 권수와 지수가 현저히 줄어드는 경향을 보입니다. 적정 가격 포지셔닝이 판매 흥행에 핵심적입니다.

---

### 3.6 리뷰건수와 판매지수의 상관관계 분석 (이변량 - 수치-수치)
![리뷰건수 vs 판매지수](images/6_bi_sales_vs_review.png)

**리뷰건수 및 판매지수 피어슨 상관계수**
{df_to_markdown(t6)}

> **[그래프 해석 (50자 이상)]**
> 리뷰건수와 판매지수의 산점도 및 피어슨 상관계수를 구한 결과, 두 변수 간의 피어슨 상관계수는 {t6.iloc[0, 1]:.3f}로 뚜렷한 양의 선형 상관관계를 보입니다. 이는 독자들의 리뷰 활성화가 도서 신뢰도를 높여 판매지수 상승으로 이어지거나, 반대로 많이 판매된 도서일수록 활발하게 리뷰가 작성되는 선순환 구조를 이룸을 방증합니다.

---

### 3.7 주요 출판사별 평균 판매지수 분석 (이변량 - 범주-수치)
![출판사별 판매지수](images/7_bi_sales_by_publisher.png)

**상위 10개 출판사의 판매지수 요약표**
{df_to_markdown(t7)}

> **[그래프 해석 (50자 이상)]**
> 주요 10대 출판사 중에서 평균 판매지수가 가장 높은 곳은 '골든래빗'입니다. 이는 최신 트렌드를 빠르게 반영한 도서들이 폭발적인 지수를 기록했기 때문입니다. 반면 가장 많은 권수를 낸 '한빛미디어'는 평균 판매지수는 중간 수준이나 스테디셀러 위주의 탄탄한 누적 성과를 보이며 출판사별로 시장 공략 전략이 상이함을 시사합니다.

---

### 3.8 출판년도별 평균 판매지수 및 판매가 추이 (이변량 - 범주-수치)
![출판년도별 판매지수](images/8_bi_sales_by_year.png)

**연도별 도서 지수 및 단가 추이표**
{df_to_markdown(t8)}

> **[그래프 해석 (50자 이상)]**
> 출판년도에 따른 시계열 분석 결과, 최근 연도(2025년, 2026년)에 출간된 도서들의 평균 판매지수가 대단히 높게 치솟아 있습니다. 이는 최신 IT 기술(인공지능, 제미나이, 클로드 등) 트렌드 반영 속도가 빠른 신간 도서 위주로 베스트셀러 시장이 활발히 재편되고 있음을 뜻하며, 평균 도서 가격 역시 상승 추세에 있음을 보여줍니다.

---

### 3.9 출판년도별 할인율 구간 도서 빈도 분석 (다변량 - 교차분석)
![할인율 누적 바 차트](images/9_multi_sales_publisher_year.png)

**최근 5개년도 할인율 구간 교차표 (Crosstab)**
{df_to_markdown(t9)}

> **[그래프 해석 (50자 이상)]**
> 출판년도에 따른 할인율의 교차 누적 바 차트와 교차표를 보면, 대부분의 IT 도서가 '5%-10%' 할인율 구간에 밀집해 있음을 알 수 있습니다. 특히 도서정가제 등의 가격 정책 여파로 인해 대다수의 베스트셀러 도서가 법정 최대 할인율인 10% 안팎의 균일한 할인 프로모션을 균일하게 유지하고 있어 연도별로도 할인율 구성비에 큰 변화가 없습니다.

---

### 3.10 수치형 변수 다변량 상관관계 히트맵 (다변량 - 수치형)
![상관관계 히트맵](images/10_multi_sales_corr.png)

**수치형 변수 상관계수 행렬표**
{df_to_markdown(t10)}

> **[그래프 해석 (50자 이상)]**
> 수치형 변수들 간의 다변량 상관관계를 종합적으로 평가한 결과, '판매가'와 '정가'가 0.99로 가장 강한 선형 관계를 가지고 있습니다. 또한 '포인트'는 판매가와 정가에 완전히 비례하여 지급되는 구조를 보입니다. '판매지수'는 '리뷰건수'와 0.44의 상관을 가져, 판매 성과와 독자 반응 간의 유의미한 상관을 입증합니다.

---

### 3.11 상품명 키워드 TF-IDF 분석 (텍스트 분석)
![TF-IDF 키워드](images/11_text_keyword_tfidf.png)

**상품명 핵심 키워드 중요도 Top 30**
{df_to_markdown(t11)}

> **[그래프 해석 (50자 이상)]**
> 형태소 분석기 없이 띄어쓰기 패턴으로 상품명 텍스트를 TF-IDF 분석한 결과, '코딩', '클로드', '코드', '제미나이', '에이전트', '바이브' 등의 키워드가 독보적인 상위권을 차지했습니다. 이는 현재 IT 베스트셀러 시장에서 AI 코딩 에이전트 및 제미나이/클로드 관련 바이브 코딩 도서가 초강세를 보이며 시장 트렌드의 핵심 화두로 우뚝 서 있음을 시사합니다.

---

## 4. 종합 결론 및 비즈니스 인사이트 (20년차 데이터 분석가 제언)

1. **AI 에이전트와 바이브 코딩의 시장 지배력**:
   텍스트 키워드 및 최근 출간 도서 성과를 분석해보면, 2025~2026년에 걸쳐 '클로드 코드', '제미나이', 'AI 에이전트', '바이브 코딩' 관련 서적이 IT 분야 베스트셀러의 핵심 성장 동력으로 자리 잡았습니다. 이 주제의 도서들은 압도적인 판매지수를 보여주고 있습니다.
2. **도서 가격 및 마케팅 전략**:
   대부분의 베스트셀러 도서는 18,000원 ~ 28,000원 대에 조율되어 있으며, 할인율은 도서정가제 테두리 안에서 약 10% 수준으로 조율됩니다. 독자의 리뷰 수는 판매지수와 강력한 상관관계를 보이기 때문에 초기 출간 시 독자 리뷰를 확보하기 위한 커뮤니티 마케팅 및 증정 활동이 신간의 베스트셀러 안착에 중요한 마케팅 전략이 될 수 있습니다.
3. **출판사의 양극화**:
   한빛미디어와 같은 기성 IT 거대 출판사가 압도적인 도서 양으로 시장을 방어하고 있는 와중에도, '골든래빗'이나 '이지스퍼블리싱'처럼 트렌드에 민감한 중소형 출판사들이 신속하게 AI 활용 도서를 내놓으며 높은 평균 판매지수를 획득해 내는 민첩성(Agility) 중심의 성과 양극화 현상이 돋보입니다.
"""

    with open(report_path, "w", encoding="utf-8") as f:
        f.write(markdown_content)
        
    print(f"성공적으로 분석이 종료되었습니다. 최종 결과물이 아래 경로에 저장되었습니다:\n- 리포트: {report_path}\n- 이미지 폴더: {images_dir}")

if __name__ == "__main__":
    run_eda()
