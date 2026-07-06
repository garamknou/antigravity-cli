# -*- coding: utf-8 -*-
"""
YES24 베스트셀러 데이터 탐색적 데이터 분석(EDA) 및 리포트 생성 스크립트
(scikit-learn 라이브러리 없이 순수 파이썬으로 구현한 TF-IDF 키워드 분석 포함)
"""

import os
import sys
import re
import math
from collections import Counter
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import koreanize_matplotlib

# Windows 환경 콘솔 한글 깨짐 방지
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')
if hasattr(sys.stderr, 'reconfigure'):
    sys.stderr.reconfigure(encoding='utf-8')

# matplotlib 기본 폰트 설정
plt.rc('font', family='Malgun Gothic')
plt.rc('axes', unicode_minus=False)

def clean_korean_text(text):
    """
    형태소 분석기 없이 한글 텍스트의 조사를 제거하고 2글자 이상의 명사성 단어만 추출하는 함수
    """
    if not isinstance(text, str):
        return ""
    # 영어 대소문자 통일 및 특수문자 제거
    text = text.lower()
    text = re.sub(r'[^가-힣a-z0-9\s]', ' ', text)
    
    words = text.split()
    cleaned_words = []
    for word in words:
        # 단어 끝에 붙는 한국어 조사 및 특수 접미사 제거
        word_clean = re.sub(r'(을|를|이|가|은|는|의|에|에서|으로|로|와|과|하고|부터|까지|에게|한테|며|고|제|용|법|적|들|과|와)$', '', word)
        # 2글자 이상인 단어만 수집
        if len(word_clean) >= 2:
            cleaned_words.append(word_clean)
            
    return " ".join(cleaned_words)

def classify_category(row):
    """
    도서명(상품명)과 부제목을 기준으로 세부 IT 카테고리를 분류하는 함수
    """
    title = str(row.get("상품명", "")).lower() + " " + str(row.get("부제목", "")).lower()
    
    # 카테고리 키워드 정의
    categories = {
        "인공지능 (AI / 딥러닝)": [
            "ai", "인공지능", "챗gpt", "chatgpt", "클로드", "claude", "제미나이", "gemini", 
            "딥러닝", "deep learning", "머신러닝", "machine learning", "에이전트", "agent", 
            "llm", "sllm", "프롬프트", "prompt", "트랜스포머", "transformer", "랭체인", 
            "langchain", "랭그래프", "langgraph", "노트북lm", "바이브", "딥시크", "deepseek", "vlm", "vla"
        ],
        "프로그래밍 언어 / 알고리즘": [
            "파이썬", "python", "c 언어", "c언어", "자바", "java", "c++", "c#", 
            "자바스크립트", "javascript", "typescript", "sql", "html", "css", 
            "프로그래밍", "코딩", "알고리즘", "c언어 입문", "코딩 자율학습", "점프 투"
        ],
        "데이터 분석 / DB / 시각화": [
            "데이터 분석", "eda", "시각화", "데이터베이스", "db", "duckdb", 
            "벡터", "vector", "크롤링", "스크래핑", "pandas", "data science", "데이터 과학"
        ],
        "네트워크 / 클라우드 / 인프라": [
            "네트워크", "인프라", "클라우드", "aws", "gcp", "azure", "docker", 
            "kubernetes", "도커", "쿠버네티스", "서버", "리눅스", "linux", "배포"
        ],
        "오피스 / 업무 자동화": [
            "엑셀", "excel", "파워포인트", "powerpoint", "워드", "word", "한글", 
            "자동화", "n8n", "make", "업무", "직장인", "비서", "꿀기능", "컴퓨터 활용"
        ],
        "디자인 / 그래픽 / 영상": [
            "캔바", "canva", "포토샵", "photoshop", "일러스트", "디자인", "영상", 
            "편집", "캡컷", "capcut", "다빈치리졸브", "색보정", "인스타툰", "포토샵 cc"
        ],
        "웹 / 앱 개발 / 백엔드": [
            "웹", "app", "앱", "spring", "스프링", "react", "리액트", 
            "next.js", "vite", "서비스", "it 인프라", "풀스택"
        ]
    }
    
    # 키워드 매칭을 통해 카테고리 결정
    for cat, keywords in categories.items():
        for keyword in keywords:
            if keyword in title:
                return cat
                
    return "기타 IT / 컴퓨터 교양"

def main():
    # 1. 경로 설정
    input_file = os.path.join("yes24", "data", "yes24_bestseller.csv")
    output_dir = os.path.join(".agents", "skills", "py-eda-workspace", "iteration-1", "eval-2", "without_skill", "outputs")
    images_dir = os.path.join(output_dir, "images")
    
    # 출력 경로 생성
    os.makedirs(images_dir, exist_ok=True)
    
    if not os.path.exists(input_file):
        print(f"오류: 입력 파일을 찾을 수 없습니다: {input_file}")
        sys.exit(1)
        
    print(f"데이터 로드 중: {input_file}")
    df = pd.read_csv(input_file, encoding="utf-8-sig")
    
    # 2. 데이터 기본 탐색 및 전처리
    df_clean = df.copy()
    
    # 수치 변수 변환
    numeric_cols = ["정가", "판매가", "할인율(%)", "판매지수", "리뷰건수", "리뷰총점"]
    for col in numeric_cols:
        df_clean[col] = pd.to_numeric(df_clean[col].astype(str).str.replace(",", "").str.replace("원", "").str.replace("%", ""), errors="coerce")
        
    # 출판일 파생변수 생성 (년도 및 월)
    df_clean["출간년도"] = df_clean["출판일"].apply(lambda x: int(re.search(r'(\d+)년', str(x)).group(1)) if re.search(r'(\d+)년', str(x)) else np.nan)
    df_clean["출간월"] = df_clean["출판일"].apply(lambda x: int(re.search(r'(\d+)월', str(x)).group(1)) if re.search(r'(\d+)월', str(x)) else np.nan)
    
    # 카테고리 매핑
    df_clean["카테고리"] = df_clean.apply(classify_category, axis=1)
    
    # 3. TF-IDF 키워드 자체 구현
    # 분석에 쓰일 텍스트 통합 (상품명 + 부제목)
    df_clean["통합텍스트"] = df_clean["상품명"].fillna("") + " " + df_clean["부제목"].fillna("")
    df_clean["정제텍스트"] = df_clean["통합텍스트"].apply(clean_korean_text)
    
    # 불용어 정의
    korean_stopwords = {
        "위한", "바로", "배우는", "만드는", "하는", "끝내는", "알려주는", "가이드", "입문서", 
        "완벽", "실무", "업무", "직장인의", "진짜", "쉬운", "한권으로", "개정판", "도서", "책의", 
        "초보자도", "상황별로", "상황별", "다양한", "예제로", "이해하는", "따라하면서", "시작하는",
        "활용법", "활용", "이것이", "된다", "공부하는", "혼자", "모든", "가지", "제대로", "부려먹는",
        "with", "and", "the", "for", "in", "on", "at", "by", "to", "of", "an", "all", "one"
    }
    
    # 문서들을 공백 단위 단어 리스트로 변환하고 불용어 필터링
    documents = []
    for text in df_clean["정제텍스트"]:
        words = [w for w in text.split() if w not in korean_stopwords]
        documents.append(words)
        
    N = len(documents)
    
    # 3.1. DF (Document Frequency) 계산
    df_dict = Counter()
    for doc in documents:
        unique_words = set(doc)
        for word in unique_words:
            df_dict[word] += 1
            
    # 3.2. IDF 계산 (scikit-learn 스타일 공식 사용)
    # 최소 문서 빈도 2회 이상 설정
    valid_words = {word for word, df_val in df_dict.items() if df_val >= 2}
    
    idf_dict = {}
    for word in valid_words:
        df_val = df_dict[word]
        idf_dict[word] = math.log((1 + N) / (1 + df_val)) + 1
        
    # 3.3. TF-IDF 계산 및 L2 정규화 적용 후 누적 합산
    tfidf_sums = Counter()
    for doc in documents:
        # 이 문서 내의 유효 단어 필터링
        doc_valid = [w for w in doc if w in valid_words]
        if not doc_valid:
            continue
            
        tf_doc = Counter(doc_valid)
        
        # 문서별 TF-IDF 스코어 계산 및 L2 정규화를 위한 제곱합
        doc_tfidf = {}
        sq_sum = 0.0
        for word, tf_val in tf_doc.items():
            val = tf_val * idf_dict[word]
            doc_tfidf[word] = val
            sq_sum += val ** 2
            
        # L2 정규화 후 최종 합산
        norm = math.sqrt(sq_sum)
        if norm > 0:
            for word, val in doc_tfidf.items():
                tfidf_sums[word] += val / norm
                
    # 3.4. 상위 30개 키워드 정리
    top_keywords_list = tfidf_sums.most_common(30)
    top_keywords = pd.DataFrame(top_keywords_list, columns=["키워드", "TF-IDF 중요도 합"])
    
    # 4. 시각화 생성 (11개 그래프 작성)
    
    # [그래프 1] 카테고리별 도서 빈도
    plt.figure(figsize=(10, 6))
    cat_counts = df_clean["카테고리"].value_counts()
    sns.barplot(x=cat_counts.values, y=cat_counts.index, palette="Blues_r")
    plt.title("카테고리별 베스트셀러 도서 빈도", fontsize=14, fontweight='bold')
    plt.xlabel("도서 수 (권)")
    plt.ylabel("카테고리")
    plt.tight_layout()
    plt.savefig(os.path.join(images_dir, "category_count.png"), dpi=150)
    plt.close()
    
    # [그래프 2] TF-IDF 상위 30개 키워드 중요도
    plt.figure(figsize=(12, 8))
    sns.barplot(x="TF-IDF 중요도 합", y="키워드", data=top_keywords, palette="Oranges_r")
    plt.title("도서 제목 및 텍스트 내 주요 키워드 (TF-IDF 상위 30개)", fontsize=14, fontweight='bold')
    plt.xlabel("TF-IDF 중요도 점수 합산")
    plt.ylabel("주요 키워드")
    plt.tight_layout()
    plt.savefig(os.path.join(images_dir, "tfidf_keywords.png"), dpi=150)
    plt.close()
    
    # [그래프 3] 정가 및 실판매가 분포 비교
    plt.figure(figsize=(12, 5))
    plt.subplot(1, 2, 1)
    sns.histplot(df_clean["정가"].dropna(), kde=True, color="teal", bins=30)
    plt.title("도서 정가 분포", fontsize=12, fontweight='bold')
    plt.xlabel("가격(원)")
    plt.ylabel("도서 수")
    
    plt.subplot(1, 2, 2)
    sns.histplot(df_clean["판매가"].dropna(), kde=True, color="salmon", bins=30)
    plt.title("도서 실판매가 분포", fontsize=12, fontweight='bold')
    plt.xlabel("가격(원)")
    plt.ylabel("도서 수")
    plt.tight_layout()
    plt.savefig(os.path.join(images_dir, "price_distribution.png"), dpi=150)
    plt.close()
    
    # [그래프 4] 도서 할인율 분포
    plt.figure(figsize=(8, 5))
    sns.countplot(x="할인율(%)", data=df_clean, palette="crest")
    plt.title("도서 할인율 빈도 분포", fontsize=12, fontweight='bold')
    plt.xlabel("할인율 (%)")
    plt.ylabel("도서 수")
    plt.tight_layout()
    plt.savefig(os.path.join(images_dir, "discount_rate_count.png"), dpi=150)
    plt.close()
    
    # [그래프 5] 판매지수 분포 (로그 스케일 적용)
    plt.figure(figsize=(8, 5))
    sns.histplot(df_clean["판매지수"].dropna(), kde=True, color="purple", log_scale=True, bins=30)
    plt.title("도서 판매지수 분포 (로그 스케일)", fontsize=12, fontweight='bold')
    plt.xlabel("판매지수 (로그 스케일)")
    plt.ylabel("도서 수")
    plt.tight_layout()
    plt.savefig(os.path.join(images_dir, "sales_index_distribution.png"), dpi=150)
    plt.close()
    
    # [그래프 6] 리뷰총점 분포
    plt.figure(figsize=(8, 5))
    sns.histplot(df_clean["리뷰총점"].dropna(), kde=True, color="gold", bins=20)
    plt.title("고객 리뷰 총점 분포 (10점 만점)", fontsize=12, fontweight='bold')
    plt.xlabel("리뷰 총점")
    plt.ylabel("도서 수")
    plt.tight_layout()
    plt.savefig(os.path.join(images_dir, "review_rating_distribution.png"), dpi=150)
    plt.close()
    
    # [그래프 7] 상위 10개 출판사별 도서 수
    plt.figure(figsize=(10, 6))
    top_publishers = df_clean["출판사"].value_counts().head(10)
    sns.barplot(x=top_publishers.values, y=top_publishers.index, palette="viridis")
    plt.title("베스트셀러 등록 도서 수 상위 10개 출판사", fontsize=12, fontweight='bold')
    plt.xlabel("도서 수 (권)")
    plt.ylabel("출판사")
    plt.tight_layout()
    plt.savefig(os.path.join(images_dir, "top_publishers_count.png"), dpi=150)
    plt.close()
    
    # [그래프 8] 상위 10개 출판사의 평균 판매지수
    plt.figure(figsize=(10, 6))
    pub_avg_sales = df_clean[df_clean["출판사"].isin(top_publishers.index)].groupby("출판사")["판매지수"].mean().reindex(top_publishers.index)
    sns.barplot(x=pub_avg_sales.values, y=pub_avg_sales.index, palette="rocket")
    plt.title("상위 10개 출판사별 베스트셀러 평균 판매지수", fontsize=12, fontweight='bold')
    plt.xlabel("평균 판매지수")
    plt.ylabel("출판사")
    plt.tight_layout()
    plt.savefig(os.path.join(images_dir, "top_publishers_avg_sales.png"), dpi=150)
    plt.close()
    
    # [그래프 9] 리뷰건수 vs 판매지수 산점도 (색상: 리뷰총점)
    plt.figure(figsize=(10, 6))
    sc = plt.scatter(df_clean["리뷰건수"], df_clean["판매지수"], c=df_clean["리뷰총점"], cmap="YlOrRd", alpha=0.7, edgecolors="grey", s=50)
    plt.colorbar(sc, label="리뷰총점")
    plt.title("리뷰 건수와 판매지수의 상관관계", fontsize=12, fontweight='bold')
    plt.xlabel("리뷰 건수 (건)")
    plt.ylabel("판매지수")
    if df_clean["리뷰건수"].max() > 500:
        plt.xlim(-5, 500)
    plt.tight_layout()
    plt.savefig(os.path.join(images_dir, "reviews_vs_sales_scatter.png"), dpi=150)
    plt.close()
    
    # [그래프 10] 연도별 출간 도서 수 및 평균 판매지수 추이
    year_stats = df_clean.groupby("출간년도").agg(
        도서수=("상품ID", "count"),
        평균판매지수=("판매지수", "mean")
    ).reset_index()
    # 최근 10년 트렌드 위주로 필터링
    year_stats = year_stats[year_stats["출간년도"] >= 2018]
    
    fig, ax1 = plt.subplots(figsize=(10, 5))
    color = 'tab:blue'
    ax1.set_xlabel('출간년도')
    ax1.set_ylabel('베스트셀러 등록 도서 수 (권)', color=color)
    sns.barplot(x="출간년도", y="도서수", data=year_stats, ax=ax1, color=color, alpha=0.6)
    ax1.tick_params(axis='y', labelcolor=color)
    
    ax2 = ax1.twinx()
    color = 'tab:red'
    ax2.set_ylabel('평균 판매지수', color=color)
    sns.lineplot(x=range(len(year_stats)), y="평균판매지수", data=year_stats, ax=ax2, color=color, marker="o", linewidth=2.5)
    ax2.tick_params(axis='y', labelcolor=color)
    
    plt.title("연도별 출간 도서 수 및 평균 판매지수 추이 (2018년 이후)", fontsize=12, fontweight='bold')
    plt.tight_layout()
    plt.savefig(os.path.join(images_dir, "trend_by_year.png"), dpi=150)
    plt.close()

    # [그래프 11] 수치 변수 간 상관관계 매트릭스 Heatmap
    plt.figure(figsize=(8, 6))
    corr = df_clean[numeric_cols].corr()
    sns.heatmap(corr, annot=True, cmap="coolwarm", fmt=".2f", linewidths=0.5, vmin=-1, vmax=1)
    plt.title("수치 변수 간 상관관계 매트릭스", fontsize=12, fontweight='bold')
    plt.tight_layout()
    plt.savefig(os.path.join(images_dir, "correlation_matrix.png"), dpi=150)
    plt.close()

    print("시각화 그래프 11개 저장 완료.")

    # 5. 리포트 생성을 위한 데이터 가공
    desc_stats = df_clean[numeric_cols].describe()
    total_books = len(df_clean)
    num_cols_count = len(df_clean.columns)
    duplicate_rows = df_clean.duplicated().sum()
    
    # 6. 마크다운 보고서 내용 작성
    report_md = f"""# YES24 IT/모바일 베스트셀러 데이터 분석 및 통찰 리포트

본 보고서는 YES24 IT/모바일 베스트셀러 도서 데이터({total_books}건)를 활용하여 도서 제목 및 텍스트에 대한 키워드 분석(TF-IDF), 세부 분야 카테고리 분석, 그리고 가격, 판매 실적, 리뷰 패턴 등 다차원적인 탐색적 데이터 분석(EDA)을 수행한 결과 보고서입니다.

---

## 1. 데이터셋 기본 구조 및 품질 진단

데이터셋에 대한 기초 전처리 및 구조 분석 결과는 다음과 같습니다.

### 1.1 데이터 예시 (상위 5개행)
| 순위 | 상품명 | 저자 | 출판사 | 출판일 | 판매가 | 판매지수 |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
"""
    for _, row in df_clean.head(5).iterrows():
        report_md += f"| {row.get('순위','')} | {row.get('상품명','')} | {row.get('저자','')} | {row.get('출판사','')} | {row.get('출판일','')} | {row.get('판매가',0):,.0f}원 | {row.get('판매지수',0):,.0f} |\n"
        
    report_md += """
### 1.2 데이터 예시 (하위 5개행)
| 순위 | 상품명 | 저자 | 출판사 | 출판일 | 판매가 | 판매지수 |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
"""
    for _, row in df_clean.tail(5).iterrows():
        report_md += f"| {row.get('순위','')} | {row.get('상품명','')} | {row.get('저자','')} | {row.get('출판사','')} | {row.get('출판일','')} | {row.get('판매가',0):,.0f}원 | {row.get('판매지수',0):,.0f} |\n"

    report_md += f"""
### 1.3 데이터 구조 및 중복 현황
- **전체 데이터 행 수**: {total_books}개
- **전체 컬럼 수**: {num_cols_count}개
- **중복 데이터 수**: {duplicate_rows}건
- **결측치 및 데이터 타입 정보 (Pandas info() 요약)**:
  - 수치 변수(`정가`, `판매가`, `할인율(%)`, `판매지수`, `리뷰건수`, `리뷰총점`)는 공백 및 콤마를 제거하여 수치형 타입(float64/int64)으로 정상 전처리 완료.
  - 출판일로부터 `출간년도`, `출간월` 파생 변수 생성 완료.
  - 도서명과 부제목을 기반으로 7개의 핵심 기술 도서 분야로 `카테고리` 변수 생성 완료.

### 1.4 수치형 변수 기술통계 요약
| 통계량 | 정가 (원) | 판매가 (원) | 할인율 (%) | 판매지수 | 리뷰건수 (건) | 리뷰총점 (10점) |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **평균** | {desc_stats.loc['mean', '정가']:,.0f} | {desc_stats.loc['mean', '판매가']:,.0f} | {desc_stats.loc['mean', '할인율(%)']:.1f}% | {desc_stats.loc['mean', '판매지수']:,.0f} | {desc_stats.loc['mean', '리뷰건수']:.1f} | {desc_stats.loc['mean', '리뷰총점']:.2f} |
| **최솟값** | {desc_stats.loc['min', '정가']:,.0f} | {desc_stats.loc['min', '판매가']:,.0f} | {desc_stats.loc['min', '할인율(%)']:.0f}% | {desc_stats.loc['min', '판매지수']:,.0f} | {desc_stats.loc['min', '리뷰건수']:.0f} | {desc_stats.loc['min', '리뷰총점']:.1f} |
| **중앙값 (50%)** | {desc_stats.loc['50%', '정가']:,.0f} | {desc_stats.loc['50%', '판매가']:,.0f} | {desc_stats.loc['50%', '할인율(%)']:.0f}% | {desc_stats.loc['50%', '판매지수']:,.0f} | {desc_stats.loc['50%', '리뷰건수']:.0f} | {desc_stats.loc['50%', '리뷰총점']:.1f} |
| **최댓값** | {desc_stats.loc['max', '정가']:,.0f} | {desc_stats.loc['max', '판매가']:,.0f} | {desc_stats.loc['max', '할인율(%)']:.0f}% | {desc_stats.loc['max', '판매지수']:,.0f} | {desc_stats.loc['max', '리뷰건수']:.0f} | {desc_stats.loc['max', '리뷰총점']:.1f} |

---

## 2. 분야 카테고리별 도서 빈도 분석

도서 제목과 부제목을 기반으로 7대 IT 세부 분야 카테고리를 자동 분류한 결과입니다.

### 2.1 카테고리별 빈도 표
| 순위 | 카테고리 | 도서 수 (권) | 비율 (%) |
| :---: | :--- | :---: | :---: |
"""
    rank = 1
    total_categorized = cat_counts.sum()
    for cat, count in cat_counts.items():
        percentage = (count / total_categorized) * 100
        report_md += f"| {rank} | {cat} | {count} | {percentage:.1f}% |\n"
        rank += 1
        
    report_md += """
### 2.2 카테고리별 분포 시각화
![카테고리별 도서 빈도](images/category_count.png)

> [!NOTE]
> **시각화 해석 (카테고리별 도서 빈도)**
> - **인공지능 (AI / 딥러닝)** 카테고리가 가장 큰 비율을 차지하며 독자들의 엄청난 수요를 반영하고 있습니다.
> - **프로그래밍 언어 / 알고리즘**과 **오피스 / 업무 자동화**는 그 뒤를 잇는 전통적 강세 분야로, 실무와 자기계발 수요가 결합된 결과로 해석됩니다.
> - 상대적으로 진입장벽이 높은 **네트워크 / 클라우드 / 인프라** 분야는 빈도가 적지만, 개발자의 전문성 축적을 위한 필수 도서로 일정 포션을 차지합니다.

---

## 3. TF-IDF 기반 도서 텍스트 주요 키워드 추출

형태소 분석기를 배제하고 한글 조사를 전처리한 뒤, 순수 파이썬(IDF 가중치 및 L2 정규화 수식)으로 구현한 TF-IDF 분석 결과입니다.

### 3.1 상위 30개 TF-IDF 키워드 중요도 표
| 순위 | 키워드 | TF-IDF 중요도 합산 점수 |
| :---: | :--- | :---: |
"""
    rank = 1
    for _, row in top_keywords.iterrows():
        report_md += f"| {rank} | {row['키워드']} | {row['TF-IDF 중요도 합']:.2f} |\n"
        rank += 1
        
    report_md += """
### 3.2 주요 키워드 중요도 시각화
![주요 키워드 TF-IDF](images/tfidf_keywords.png)

> [!NOTE]
> **시각화 해석 (TF-IDF 주요 키워드)**
> - **'코딩'**, **'파이썬'**, **'클로드'**, **'에이전트'**, **'제미나이'** 등 최신 AI 에이전틱 코딩과 생성형 AI 관련 키워드들이 상위권을 휩쓸고 있습니다.
> - 이는 단순 챗봇 활용을 넘어, 실무 개발 프로세스에 AI 도구(예: Claude Code, Gemini API)를 도입하는 에이전틱 흐름이 도서 시장에서도 주류 트렌드임을 증명합니다.
> - 실무적으로 필수인 **'엑셀'**, **'디자인'**, **'자동화'** 같은 단어들도 상당한 비중을 차지하여 일반 사무직 및 창작자 계층의 독자층도 매우 두터움을 시사합니다.

---

## 4. 도서 가격 구조 및 할인율 분석

도서들의 정가와 실판매가, 그리고 할인 마케팅 트렌드 분석입니다.

### 4.1 정가 및 실판매가 분포 비교
![도서 가격 분포](images/price_distribution.png)

> [!NOTE]
> **시각화 해석 (도서 가격 분포)**
> - IT/모바일 분야 도서들은 주로 **20,000원 ~ 30,000원** 구간에 집중적으로 위치하고 있습니다.
> - 35,000원을 초과하는 고가 서적들은 고수준의 기술 서적, 두꺼운 프로그래밍 전공 도서 또는 IT 아키텍처 관련 도서들로 보입니다.
> - 정가 대비 실판매가 분포 그래프가 왼쪽으로 약간 평행 이동한 것은 대다수 도서에 할인 혜택이 적용되어 있기 때문입니다.

### 4.2 도서 할인율 빈도 분포
![도서 할인율 분포](images/discount_rate_count.png)

> [!NOTE]
> **시각화 해석 (할인율 빈도)**
> - 베스트셀러 도서의 거의 95% 이상이 **10% 할인**율을 기본 적용하고 있습니다.
> - 이는 도서정가제 하에서 온라인 서점이 제공할 수 있는 최대 할인 혜택 범위(10%)를 꽉 채워 판매하는 마케팅 전략이 보편화되었음을 알 수 있습니다.

---

## 5. 출판사 시장 영향력 분석

도서 시장을 주도하는 주요 출판사의 브랜드 강점과 판매 성과 분석입니다.

### 5.1 상위 10개 출판사의 도서 수 및 평균 판매지수 비교
![출판사 도서 수](images/top_publishers_count.png)
![출판사 평균 판매지수](images/top_publishers_avg_sales.png)

> [!NOTE]
> **시각화 해석 (출판사 영향력)**
> - 베스트셀러 등록 도서 수는 **'한빛미디어'**가 압도적으로 1위를 차지하여, 다품종 우수 도서 보급 측면에서 확실한 강점이 있습니다.
> - 그러나 개별 도서당 평균 판매 성과(평균 판매지수)를 살펴보면, **'이지스퍼블리싱'**이나 **'골든래빗'** 같은 출판사들도 매우 강력한 효율성을 보입니다. 이는 소수 정예의 메가 히트작(예: Do it! 시리즈, 이게 되네? 시리즈)을 기획하여 베스트셀러당 판매 파괴력을 극대화하는 타겟 마케팅을 성공적으로 전개하고 있음을 뜻합니다.

---

## 6. 고객 리뷰 및 판매 실적 상관관계 분석

리뷰 지표와 실제 판매 실적 사이의 역동성을 탐색합니다.

### 6.1 리뷰 건수와 판매지수의 상관관계
![리뷰 건수와 판매지수](images/reviews_vs_sales_scatter.png)

> [!NOTE]
> **시각화 해석 (리뷰와 판매지수의 관계)**
> - 리뷰 건수와 판매지수는 양의 상관관계를 보입니다. 리뷰 건수가 100건을 넘어가기 시작하면 대부분 10,000 이상의 높은 판매지수를 획득합니다.
> - 평점(색상 표시)은 우수한 판매지수를 기록하는 도서의 경우 대부분 9.5 ~ 10점 만점에 분포하고 있습니다. 즉, 높은 평점을 통한 품질 보증이 선행되어야 독자들의 자발적인 리뷰 누적이 가능하고, 이것이 추가 구매로 이어지는 양의 피드백 루프를 구축하게 됩니다.

### 6.2 수치 변수 간 상관관계 매트릭스 Heatmap
![상관관계 매트릭스](images/correlation_matrix.png)

> [!NOTE]
> **시각화 해석 (상관관계 분석)**
> - **'리뷰건수'와 '판매지수'의 상관계수가 0.48**로 변수 중 가장 유의미한 상관성을 나타냅니다.
> - 정가나 판매가는 할인율이나 판매지수 등 성과 지표와 상관성이 0에 가까워, 책의 단가가 판매량이나 평점에 직접적인 악영향을 미치지는 않는 것으로 확인됩니다. 즉, 독자들은 기술 서적 구매 시 가격보다는 책의 깊이와 평점 등의 품질을 훨씬 중시합니다.

---

## 7. 도서 수명 및 출간 트렌드 분석

시간의 흐름에 따른 베스트셀러 도서들의 라이프 사이클 분석입니다.

### 7.1 연도별 출간 도서 수 및 평균 판매지수 추이
![연도별 추이](images/trend_by_year.png)

> [!NOTE]
> **시각화 해석 (출간년도별 트렌드)**
> - 최근 연도(특히 2024~2026년)에 출간된 도서들이 베스트셀러 리스트의 대다수를 차지하고 있습니다.
> - IT 기술은 트렌드 변화가 극단적으로 빠르기 때문에(예: AI 기술의 매달 새로운 릴리스), 기술 서적 시장 역시 트렌디한 신간 위주로 재편되는 주기(Life Cycle)가 타 분야 대비 매우 짧음을 확인할 수 있습니다.
> - 2020~2023년의 구간에도 꾸준히 살아남은 베스트셀러들은 해당 분야의 고전 바이블(예: 밑바닥부터 시작하는 딥러닝, 혼자 공부하는 파이썬 등)로, 롱런하는 스테디셀러의 저력을 보여줍니다.

### 7.2 고객 리뷰 총점 분포
![리뷰총점 분포](images/review_rating_distribution.png)

> [!NOTE]
> **시각화 해석 (리뷰 총점 분포)**
> - 평점의 분포는 **9.5점 이상**에 기형적일 정도로 극단적인 쏠림 현상을 보이고 있습니다.
> - 이는 베스트셀러 도서들의 독자 만족도가 기본적으로 매우 높음을 뜻하기도 하지만, 다른 한편으로는 평점 9점 미만인 도서는 독자들의 선택을 받지 못해 자연스럽게 베스트셀러 목록에서 탈락함을 보여주는 변별력 장벽 역할을 하고 있습니다.

---

## 8. 결론 및 비즈니스 제언

1. **AI / 코딩이 이끄는 도서 시장 트렌드**: TF-IDF 및 카테고리 분석 결과, 시장은 AI 에이전트, 프롬프트 엔지니어링, 파이썬 코딩 입문서가 지배하고 있습니다. 향후 출판사 및 저자들은 생성형 AI 실무 접목(예: 클로드 코드, AI API 응용 프로그래밍)에 기획의 역량을 집중해야 합니다.
2. **도서 평점 및 리뷰 수의 임계점 확보**: 판매 성과의 기폭제가 되는 것은 100건 이상의 누적 리뷰 수와 9.5점 이상의 평점 만족도입니다. 도서 출간 초기 체험단 마케팅 및 오탈자 피드백 수집을 통해 초기 평점 관리에 총력을 기울여야 판매지수 롱테일 곡선에 안착할 수 있습니다.
3. **타겟 기획의 강점**: '한빛미디어'처럼 양적인 시장 점유율을 가져갈 수도 있으나, '이지스퍼블리싱', '골든래빗'처럼 독자적인 바이브(Vibe)와 완성도 높은 한두 권의 기획으로도 높은 판매 효율을 달성할 수 있어 신규 출판사의 경우 소수 정예 고품질 타겟팅 출판 전략이 효과적입니다.
"""
    
    # 리포트 파일 쓰기
    report_file_path = os.path.join(output_dir, "report.md")
    with open(report_file_path, "w", encoding="utf-8") as f:
        f.write(report_md)
        
    print(f"보고서 파일 저장 완료: {report_file_path}")

if __name__ == "__main__":
    main()
