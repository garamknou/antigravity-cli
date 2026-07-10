# 아티팩트 파일의 로컬 docs 폴더 동기화 및 관리 계획 (모든 프로젝트 공통)

본 계획서는 에이전트가 생성하는 글로벌 아티팩트 파일(계획서, Walkthrough 등)을 프로젝트 루트의 `docs/` 폴더 하위에 실시간으로 복사 및 보존하여, 프로젝트별로 모든 산출물을 자체적으로 관리할 수 있도록 공통 규칙을 제정하고 기존 파일들을 동기화하는 계획을 수립합니다.

---

## 1. 목표 (Goal Description)
- **모든 프로젝트 공통 규칙 수립**: 에이전트가 채팅 화면에 계획서 및 Walkthrough 아티팩트를 렌더링하기 위해 글로벌 아티팩트 디렉터리에 파일을 작성할 때, 해당 아티팩트의 사본이 대상 프로젝트의 `docs/` 폴더 내에도 자동 복사되어 영구 보존되도록 규칙을 정의합니다.
- **기존 아티팩트 동기화**: 이전 단계에서 생성된 계획서 및 Walkthrough 파일들을 로컬 워크스페이스 `starbucks/docs/` 아래로 안전하게 이전/복사합니다.

---

## 2. 사용자 검토 요구사항 (User Review Required)
- **규칙 정의의 적절성**: `.agents/rules/artifact-docs.md`로 신규 규격이 생성되어 모든 프로젝트에 공통 적용됩니다.
- **동기화 대상 파일**:
  - `starbucks_pipeline_plan.md` -> `starbucks/docs/starbucks_pipeline_plan.md`
  - `walkthrough.md` -> `starbucks/docs/walkthrough.md`
  - `artifact_docs_sync_plan.md` -> `starbucks/docs/artifact_docs_sync_plan.md` (본 계획서)

> [!NOTE]  
> Antigravity의 아티팩트 승인(Proceed) 팝업 기능은 오직 시스템 전역 브레인 디렉터리에 아티팩트 파일이 생성될 때만 작동하므로, 시스템 전역 경로에 먼저 파일을 쓴 다음, 해당 내용을 즉시 로컬 워크스페이스의 `docs/`에 복사하는 동기화 방식을 취합니다.

---

## 3. 제안된 변경 사항 (Proposed Changes)

### [Component: Rule Definition]
모든 프로젝트에 공통 적용할 아티팩트 동기화 규칙을 생성합니다.

#### [NEW] .agents/rules/artifact-docs.md
에이전트가 아티팩트(계획서, walkthrough 등)를 작성할 때, 해당 파일의 복사본을 해당 프로젝트 폴더 내 `docs/` 디렉터리에 동일하게 생성 및 관리해야 한다는 원칙을 담은 규칙 명세서입니다.

---

### [Component: Documentation Sync]
기존 및 신규 아티팩트를 로컬 폴더에 복사합니다.

#### [NEW] starbucks/docs/starbucks_pipeline_plan.md
이전 단계의 수집 파이프라인 계획서 아티팩트를 로컬 폴더에 적재합니다.

#### [NEW] starbucks/docs/walkthrough.md
이전 단계의 최종 완료보고 아티팩트를 로컬 폴더에 적재합니다.

#### [NEW] starbucks/docs/artifact_docs_sync_plan.md
본 아티팩트 복사 및 공통 규칙 제정 계획서 자체를 로컬 폴더에 적재합니다.

---

## 4. 검증 계획 (Verification Plan)

### A. 수동 검증 단계
1. **규칙 파일 생성 확인**: `.agents/rules/artifact-docs.md` 파일이 존재하고 올바르게 인지되는지 확인합니다.
2. **동기화 여부 확인**:
   - `starbucks/docs/` 디렉터리에 `starbucks_pipeline_plan.md`, `walkthrough.md`, `artifact_docs_sync_plan.md` 세 파일이 모두 성공적으로 복사되었는지 파일 목록과 크기를 대조합니다.
3. **가독성 검증**: 로컬 `docs` 폴더 내 마크다운 링크와 형식에 깨짐이 없는지 확인합니다.
