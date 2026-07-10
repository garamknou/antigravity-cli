# -*- coding: utf-8 -*-
"""
starbucks API 네트워크 요청 탐색 스크립트

이 스크립트는 Playwright를 사용하여 대상 웹 페이지를 로딩하고,
백그라운드에서 발생하는 데이터 통신 API의 URL, Method, Headers, Payload를 
감지하여 로그 파일 및 텍스트 파일로 저장합니다.

치환 대상 변수:
- TARGET_URL: https://www.starbucks.co.kr/store/store_map.do
- PROJECT_NAME: starbucks

작성자: Antigravity AI Data Pipeline Framework
"""

import asyncio
import json
from playwright.async_api import async_playwright

async def inspect_network():
    url = "https://www.starbucks.co.kr/store/store_map.do"
    project_name = "starbucks"
    output_log_path = f"{project_name}/docs/api_debug.txt"
    
    print(f"[Inspect] Playwright 브라우저를 시작하여 {url} 에 접속합니다...")
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )
        page = await context.new_page()
        
        api_requests = []
        
        # 네트워크 응답 감지 이벤트
        async def handle_response(response):
            res_url = response.url
            # 정적 파일 필터링 제외
            if any(ext in res_url for ext in [".png", ".jpg", ".jpeg", ".gif", ".css", ".js", ".woff", ".svg"]):
                return
            
            # API 식별용 임의 필터 (특정 게이트웨이나 도메인 포함 여부 확인 가능)
            if "api" in res_url or "data" in res_url or "list" in res_url or "query" in res_url:
                try:
                    status = response.status
                    text = await response.text()
                    req_headers = response.request.headers
                    
                    # 로컬 디버그 파일로 저장
                    with open(output_log_path, "w", encoding="utf-8") as f:
                        f.write(f"URL: {res_url}\n")
                        f.write(f"Status: {status}\n\n")
                        f.write("=== Request Headers ===\n")
                        f.write(json.dumps(req_headers, indent=2, ensure_ascii=False))
                        f.write("\n\n=== Response Body ===\n")
                        f.write(text[:5000]) # 본문은 상위 일부만 보관
                    print(f"[Inspect] 성공적으로 API 응답을 감지하여 저장했습니다: {output_log_path}")
                except Exception as e:
                    pass
                    
        page.on("response", handle_response)
        
        try:
            await page.goto(url, wait_until="networkidle", timeout=45000)
        except Exception as e:
            print(f"[Inspect] 페이지 대기 시간 만료 혹은 통신 지연 발생: {e}")
            
        await asyncio.sleep(3)
        await browser.close()
        
if __name__ == "__main__":
    asyncio.run(inspect_network())
