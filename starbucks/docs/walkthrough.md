# 데이터 파이프라인 프레임워크 스킬 기반 스타벅스 수집 및 EDA 완료 보고 (Walkthrough)

본 프로젝트는 `.agents/skills/data-pipeline-framework/SKILL.md` 스킬 규격에 따라 `config.json`을 수립하고, 스타벅스 맞춤형 API 스크래퍼 코드 개조 및 의존성 라이브러리(`scikit-learn`, `koreanize-matplotlib`, `setuptools`) 구성을 완료한 후, 전국 스타벅스 매장 정보 수집 및 다차원 EDA 분석(11개 시각화 이미지 생성)을 완전 자동화하여 수행하였습니다.

---

## 1. 수행 결과 및 변경 사항 (Changes Made)

### A. 설정 파일 구성 (Configuration)
- **설정 파일**: [config.json](../../config.json) (로컬)
  - 프로젝트 명(`starbucks`), 스타벅스 대상 URL 지정 및 범용 5대 속성(`name`, `category`, `value_1`, `value_2`, `detail_text`)의 컬럼 매핑을 적용하였습니다.

### B. 파이프라인 엔진 구동 및 템플릿 배포 (Pipeline Initialization)
- `engine.py init` 명령어를 통해 `starbucks/` 디렉터리 내에 `src/`, `data/`, `images/`, `docs/`, `reports/` 구조를 자동 생성하고 템플릿 코드들을 치환 배포하였습니다.
- **배포된 스크립트**:
  - [scraping.py](../src/scraping.py) (로컬) : 스타벅스 POST API에 맞춤 쿼리를 전송하고 범용 5대 속성으로 매핑하여 저장하도록 개조하였습니다.
  - [eda.py](../src/eda.py) (로컬) : 데이터 무결성 검증, 11개 다차원 분석 차트 그리기 및 TF-IDF 핵심 키워드 가중치를 자동 계산하도록 배포되었습니다.
  - [dashboard_data_builder.py](../src/dashboard_data_builder.py) (로컬) : 컴파일러.

### C. 데이터 수집 및 EDA 결과물 (Data & Visualization Output)
- **적재 데이터**: [starbucks_bestseller.csv](../data/starbucks_bestseller.csv) (로컬)
  - 전국 **2,177개** 스타벅스 지점 정보가 범용 5대 속성 포맷으로 적재되었습니다.
- **기초 통계 보고서**: [basic_statistics.txt](./basic_statistics.txt) (로컬)
  - 결측치 정보, 수치형 변수(위경도) 기술통계 정보 및 빈도 높은 지점 통계를 저장하였습니다.
- **TF-IDF 중요 키워드**: [tfidf_keywords.csv](./tfidf_keywords.csv) (로컬)
  - 도로명주소 텍스트를 마이닝하여 `서울특별시`, `경기도`, `1층`, `강남구`, `중구` 등 중요도가 높은 주소별 주요 단어 가중치를 도출했습니다.
- **시각화 이미지 11개 적재**: [starbucks/images/](../images) (로컬)
  - `01_price_histogram.png` (위도 분포)
  - `02_sale_price_histogram.png` (경도 분포)
  - `05_top_publishers.png` (시도별 매장 점유 빈도)
  - `07_price_vs_sale_price.png` (지리적 분포 산점도 - 한국 지도 형상 확인 가능)
  - `11_tfidf_keywords_bar.png` (주소 텍스트 TF-IDF 키워드 순위 차트)

---

## 2. 해결된 주요 오류 및 검증 (Troubleshooting & Verification)

1. **의존성 모듈 설치**:
   - `sklearn` 모듈 누락 문제 -> `uv pip install scikit-learn`으로 해결.
   - `koreanize_matplotlib` 모듈 누락 문제 -> `uv pip install koreanize-matplotlib`로 해결.
   - Python 3.12+ 환경에서 `distutils` 제거에 따른 `koreanize-matplotlib` 구동 중단 문제 -> `uv pip install setuptools`로 복구 완료.
2. **상대 경로 규칙 검증**:
   - 프레임워크가 가동 및 빌드한 최종 데이터 로그와 문서 상에서 절대 경로가 완전히 배제되었음을 검증했습니다.
