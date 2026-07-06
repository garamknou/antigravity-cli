# Implementation Plan - YES24 베스트셀러 데이터 탐색적 데이터 분석 (EDA)

YES24 IT/모바일 종합 베스트셀러 도서 데이터([yes24_bestseller.csv](../data/yes24_bestseller.csv)) 869건을 대상으로 도서 시장의 트렌드, 가격 패턴, 평점 구조, 출판사 영향력 등을 시각화 및 통계 분석을 통해 규명하고 유의미한 분석 리포트를 도출하는 계획입니다.

## User Review Required

> [!IMPORTANT]
> **패키지 추가 설치 필요**
> 데이터 분석 및 시각화를 위해 파이썬 시각화 라이브러리인 `matplotlib`와 `seaborn`을 가상환경에 추가 설치해야 합니다. (샌드박스 우회 옵션 필요)
>
> **한글 폰트 적용**
> 윈도우 OS 콘솔 및 시각화 차트 내 한글 깨짐 방지를 위해 `Malgun Gothic` 폰트를 차트에 설정하여 진행합니다.

## Proposed Changes

### [EDA 분석 프로세스]

1. **데이터 전처리 (Data Preprocessing)**
   - `출판일` 컬럼에서 년도와 월 정보를 분리하여 파생 변수(`출간년도`, `출간월`) 생성
   - 결측치(부제목, 포인트 등)에 대한 정제 처리 및 자료형 검증
2. **단변량 분석 (Univariate Analysis)**
   - 가격 대 분포(정가, 판매가) 시각화 (KDE & Histogram)
   - 판매지수, 리뷰건수, 리뷰총점의 분포 확인 및 이상치 탐색
   - 베스트셀러 점유 상위 출판사(Top 10) 및 대표 저자 분포 확인
3. **관계 분석 (Bivariate & Multivariate Analysis)**
   - 수치형 변수(판매가, 할인율, 판매지수, 리뷰건수, 리뷰총점) 간의 피어슨 상관계수 산출 및 Heatmap 시각화
   - 판매지수와 리뷰건수, 가격과의 관계 분석 (Scatter plot & Trend line)
   - 상위 출판사별 도서 가격대 및 평균 판매지수 비교 (Box plot & Bar plot)
   - 출간 시기(년도/월)에 따른 베스트셀러 분포 및 판매지수 합계 추이 분석 (Line plot)
4. **인사이트 분석 보고서 작성**
   - 수집된 모든 시각화 차트 이미지들을 [yes24/images](../images) 디렉터리에 저장
   - 최종 분석 결과를 정리한 [eda_report.md](./eda_report.md) 아티팩트 문서 생성

---

### [Component Name]

#### [NEW] [eda_analysis.py](../src/eda_analysis.py)
- pandas, matplotlib, seaborn을 활용한 데이터 가공, 시각화 이미지 생성 및 분석 리포트 마크다운 초안 작성을 처리하는 통합 분석 스크립트.

#### [NEW] [eda_report.md](./eda_report.md)
- 수집된 데이터 분석 결과를 차트와 함께 종합하여 시장 통찰을 보고하는 탐색적 데이터 분석 보고서.

---

## Verification Plan

### Automated Tests
- 가상환경 패키지 설치:
  `uv pip install matplotlib seaborn`
- EDA 분석 스크립트 실행:
  `.venv\Scripts\python.exe yes24\src\eda_analysis.py`

### Manual Verification
- [yes24/images](../images) 폴더 내에 생성된 차트 이미지(`price_dist.png`, `correlation_matrix.png`, `top_publishers.png`, `sales_vs_reviews.png`) 파일들이 왜곡이나 한글 깨짐 현상 없이 완벽하게 렌더링되었는지 확인합니다.
- 최종 작성된 [eda_report.md](./eda_report.md) 보고서의 품질을 검증합니다.
