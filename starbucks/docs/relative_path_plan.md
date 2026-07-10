# 문서 및 코드 내 모든 경로의 상대 경로 전환 계획 (모든 프로젝트 공통)

본 계획서는 사용자의 지침에 따라 워크스페이스 전역의 모든 문서(마크다운 계획서, 보고서 등)와 코드(파이썬 소스 코드) 내에서 절대 경로 기술을 전면 배제하고, **상대 경로**만을 사용하여 모든 참조 및 출력 로그를 처리하도록 공통 규칙을 제정하고 기존 파일을 수정하기 위한 설계안입니다.

---

## 1. 목표 (Goal Description)
- **모든 프로젝트 공통 규칙 정의**: 에이전트가 작성하는 규칙 파일 및 소스 코드, 그리고 문서 내 경로 표기에 절대 경로가 포함되지 않도록 원칙을 정립합니다.
- **문서 및 코드 리팩토링**:
  - `starbucks/src/collector.py` 코드 내 출력 메시지의 절대 경로를 실행 위치 기준 상대 경로로 변경합니다.
  - `starbucks/docs/` 하위의 모든 마크다운 문서 내의 링크 및 텍스트 경로를 워크스페이스 기준 상대 경로로 변경합니다.

---

## 2. 사용자 검토 요구사항 (User Review Required)
- **마크다운 링크 형식**: 글로벌 아티팩트의 경우 시스템 연동을 위해 `file://` 스키마가 필요할 수 있으나, 워크스페이스 내부의 로컬 문서(예: `starbucks/docs/*`) 간에는 절대 경로를 제거하고 완벽히 상대 경로(예: `../data/starbucks_stores.csv`)로 교체합니다.
- **코드 내 경로**: 스크립트 실행 환경에 구애받지 않도록 코드 내 로그 출력 및 파일 입출력 시에도 워크스페이스 루트 또는 파일 기준 상대 경로만을 사용하도록 수정합니다.

---

## 3. 제안된 변경 사항 (Proposed Changes)

### [Component: Rule Definition]
모든 프로젝트에 공통 적용할 상대 경로 규칙을 생성합니다.

#### [NEW] .agents/rules/relative-paths.md
코드 및 문서 내 모든 경로 표현에 상대 경로를 사용해야 한다는 원칙을 기술하는 공통 규칙 파일입니다.

---

### [Component: Source Code]
파이썬 스크립트 실행 완료 시 출력되는 파일 경로를 상대 경로로 변경합니다.

#### [MODIFY] starbucks/src/collector.py
- 기존 `output_path = os.path.join(data_dir, 'starbucks_stores.csv')`를 생성한 후, 사용자 화면이나 로그에 완료 출력할 때 절대 경로가 아닌 워크스페이스 루트 기준의 상대 경로(`starbucks/data/starbucks_stores.csv`)로 출력하도록 수정합니다.

---

### [Component: Documentation Paths]
로컬 문서 내 모든 절대 경로 언급을 상대 경로로 변경합니다.

#### [MODIFY] starbucks/docs/starbucks_collection_plan.md
- 텍스트 내 절대 경로 설명을 상대 경로로 일괄 교환합니다.

#### [MODIFY] starbucks/docs/starbucks_collection_report.md
- 이전 계획서에 기록된 절대 경로 표현을 상대 경로 `starbucks/data/starbucks_stores.csv` 형태로 변경합니다.

#### [MODIFY] starbucks/docs/starbucks_pipeline_plan.md
- 계획서 내 절대 경로 기술부를 모두 상대 경로로 변경합니다.

#### [MODIFY] starbucks/docs/artifact_docs_sync_plan.md
- 본문 내 모든 절대 경로 기술부를 상대 경로로 변경합니다.

#### [MODIFY] starbucks/docs/walkthrough.md
- 로컬 마크다운 문서들 내부의 링크를 상대 경로 기반 링크로 전면 교체합니다.

---

## 4. 검증 계획 (Verification Plan)

### A. 수동 검증 단계
1. **규칙 파일 생성 확인**: `.agents/rules/relative-paths.md` 파일이 존재하고 정상 반영되었는지 확인합니다.
2. **코드 동작 및 로그 확인**: 
   - `uv run python starbucks/src/collector.py` 실행 시 터미널 로그 출력이 절대 경로 없이 상대 경로로 정상 표기되는지 검증합니다.
3. **문서 내 절대 경로 탐색**: 
   - `grep` 등을 이용하여 `starbucks/docs/` 폴더 내 마크다운 파일에 `D:` 또는 `C:` 등의 드라이브 문자 및 절대 경로가 포함되어 있는지 전수 검사하여 누락을 방지합니다.
