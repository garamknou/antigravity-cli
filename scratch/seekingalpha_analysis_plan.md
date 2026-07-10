# Seeking Alpha 정보 수집 자동화 계획서 및 아키텍처

이 문서는 Seeking Alpha(https://seekingalpha.com) 사이트에서 PerimeterX 봇 탐지를 우회하고 데이터를 자동으로 수집하기 위해, **쿠키 세션을 재사용하는 방식**을 구현하고 검증하는 단계를 정의합니다.

## 1. Goal Description (목표)
- 수동 로그인을 통해 발급받은 세션 쿠키를 파일(`scratch/cookies.json`)로 저장하는 세션 빌더 스크립트를 작성합니다.
- 저장된 쿠키 파일을 플레이라이트에 주입하여 로그인 상태를 유지한 채 특정 종목 정보나 뉴스(예: AAPL)를 크롤링하는 시범 스크립트를 구현 및 검증합니다.

## 2. Proposed Changes (구현 세부사항)
- `scratch/save_session_cookies.py`: 수동 로그인 및 엔터키 감지 후 쿠키 파일 저장 도구.
- `scratch/crawl_with_cookies.py`: 쿠키를 주입받아 Seeking Alpha 주가/뉴스 페이지(AAPL 등)를 헤드리스 모드로 크롤링하는 봇.
