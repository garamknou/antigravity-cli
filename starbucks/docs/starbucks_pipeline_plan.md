# 스타벅스 매장 정보 수집 파이프라인 수립 및 로컬 문서 저장 계획

본 계획서는 스타벅스 코리아 전국 매장 정보 수집 시스템을 안정적으로 구축하고, 수집 가이드 및 데이터 분석 결과 문서를 시스템 전역 경로(글로벌 브레인 디렉터리)가 아닌 **로컬 워크스페이스의 `starbucks/docs/` 디렉터리** 내에 온전히 통합 관리하기 위한 설계안입니다.

---

## 1. 목표 (Goal Description)
- **로컬 문서 저장 정책 준수**: 스타벅스 수집 계획서 및 매뉴얼 등 모든 산출물 문서를 워크스페이스의 `starbucks/docs/` 하위에 저장하여 프로젝트 독립성과 유지보수성을 극대화합니다.
- **수집 파이프라인 검증**: 스타벅스 내부 API(`getSidoList.do`, `getStore.do`)를 안전하게 순회 조회하여 전국 매장 정보를 수집하는 스크립트를 재정비하고 실행합니다.
- **규칙 준수**: 지수 백오프, 0.3~0.8초 랜덤 딜레이, `utf-8-sig` 한글 인코딩, 파이썬 파일 상단 `# -*- coding: utf-8 -*-` 명시 등을 완벽히 준수합니다.

---

## 2. 사용자 검토 요구사항 (User Review Required)
- **로컬 워크스페이스 문서 저장**: 모든 세부 매뉴얼과 수집 결과 보고서가 `starbucks/docs/`에 저장되는지 확인해 주십시오.
- **공통 가상환경 사용**: 워크스페이스 루트의 공통 `.venv`를 사용하여 패키지를 실행합니다.

> [!IMPORTANT]
> 본 작업은 실제 스타벅스 비공식 API 서버에 요청을 전송하므로, 서버에 부하를 주지 않도록 지정된 딜레이와 백오프 로직을 준수하여 실행합니다.

---

## 3. 제안된 변경 사항 (Proposed Changes)

### [Component: Documentation]
글로벌 브레인 디렉터리가 아닌 프로젝트 내부 `starbucks/docs/` 폴더에 관련 문서를 적재합니다.

#### [NEW] starbucks/docs/starbucks_collection_plan.md
스타벅스 수집 API의 구조, 파라미터 정보 및 수집 워크플로우에 대한 설명서입니다.

#### [NEW] starbucks/docs/starbucks_collection_report.md
수집된 매장 수 통계, 최종 데이터 적재 성공 확인 및 구동 방법을 설명하는 보고서 겸 수집 매뉴얼 문서입니다.

---

### [Component: Source Code]
수집 파이프라인의 안전성과 예외 처리 기능을 강화합니다.

#### [MODIFY] starbucks/src/collector.py
- 기존 작성된 코드의 견고성을 확인하고, 경로 탐색 시 OS 독립적인 경로 설정(절대경로 및 상대경로의 명확한 분리)을 보장합니다.
- 최상단 파일 인코딩 지시자 및 한국어 docstring을 준수합니다.

---

## 4. 검증 계획 (Verification Plan)

### A. 자동 및 수동 검증 단계
1. **가상환경 의존성 검증**: `.venv\Scripts\python -c "import requests, pandas"` 명령어 실행에 오류가 없는지 확인합니다.
2. **수집기 구동**: `uv run python starbucks/src/collector.py` 실행을 통한 수집 시작.
3. **데이터 검증**:
   - `starbucks/data/starbucks_stores.csv` 생성 확인.
   - 인코딩이 `utf-8-sig`로 지정되었으며, 한글 깨짐이 없는지 확인.
   - 전국 매장 데이터(약 2,100여 개)가 누락 없이 정상적으로 결합되었는지 행 개수 확인.
4. **산출물 확인**:
   - `starbucks/docs/starbucks_collection_plan.md`가 존재하며 정상 기록되어 있는지 검증.
   - `starbucks/docs/starbucks_collection_report.md` 생성 및 결과 내용 기록 확인.
