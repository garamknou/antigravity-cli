# Seeking Alpha 정보 수집 자동화 검증 결과 (Walkthrough)

제공해주신 로그인 계정을 바탕으로 Seeking Alpha(https://seekingalpha.com) 사이트의 자동 로그인 및 정보 수집 가능 여부를 분석하고, **세션 쿠키 재사용(Session Cookie Reuse)** 방식을 구현하여 검증을 완료한 결과 보고서입니다.

---

## 1. 검증 결과 요약: 성공 (Success)
- **완전 무인 로그인 불가능**: 최초 로그인 시 PerimeterX 봇 차단 및 CAPTCHA 오버레이 레이어가 강제로 활성화되어 무인 ID/PW 자동 입력 로그인은 차단됩니다.
- **쿠키 세션 재사용 완벽 작동**: 수동 로그인 지원 도구(`save_session_cookies.py`)를 통해 캡차를 통과한 정상 로그인 세션 쿠키(56개)를 추출하여 `scratch/cookies.json`으로 저장한 뒤, 이를 헤드리스 크롤러(`crawl_with_cookies.py`)에 주입한 결과 **로그인 상태 복원 및 데이터 수집에 완벽히 성공**하였습니다.

---

## 2. 세부 구현 및 검증 과정

### [1단계] 세션 쿠키 수집 도구 작성 및 실행
- 파일: [save_session_cookies.py](file:///D:/3_Resource/antigravity-cli/scratch/save_session_cookies.py)
- **구현**: 브라우저 창을 띄워 사용자에게 안전한 로그인 환경을 제공하고, 사용자가 로그인을 완료한 뒤 터미널에 Enter 키를 누르면 즉시 전체 세션 쿠키를 덤프하는 방식을 채택하여 익명 세션이 수집되는 오작동을 해결하였습니다.
- **결과**: `scratch/cookies.json`에 56개의 인증 쿠키가 성공적으로 덤프되었습니다.

### [2단계] 쿠키 주입 기반 헤드리스 크롤러 실행
- 파일: [crawl_with_cookies.py](file:///D:/3_Resource/antigravity-cli/scratch/crawl_with_cookies.py)
- **구현**: Playwright의 `context.add_cookies()`를 사용하여 헤드리스 브라우저에 쿠키를 주입하고 `https://seekingalpha.com/symbol/AAPL` 페이지에 접속.
- **결과**:
  - 화면 내 `LOG IN` 버튼 감지되지 않음 (0개) -> **로그인 복원 성공 확인**
  - **수집된 AAPL 관련 분석 아티클 제목 및 URL 목록 (상위 10개)**:
    ```plain
    [1] Apple Nears A Peak; Accelerating Services Monetization Meets Demand Destruction Risks
        URL: https://seekingalpha.com/article/4920352-apple-nears-a-peak-accelerating-services-monetization-meets-demand-destruction-risks
    ...
    ```
