import asyncio
import os
import sys
import json
import tempfile
from playwright.async_api import async_playwright

# 임시 디렉토리 지정 (권한 에러 방지)
tmp_dir = os.path.abspath("scratch/tmp")
try:
    os.makedirs(tmp_dir, exist_ok=True)
except Exception:
    pass
os.environ['TEMP'] = tmp_dir
os.environ['TMP'] = tmp_dir
os.environ['TMPDIR'] = tmp_dir
tempfile.tempdir = tmp_dir

async def run():
    print("Playwright 기동 중 (쿠키 세션 재사용 모드)...")
    
    # 1. 저장된 쿠키 로드
    cookie_file = "scratch/cookies.json"
    if not os.path.exists(cookie_file):
        print(f"오류: 쿠키 파일({cookie_file})이 존재하지 않습니다. 먼저 로그인을 완료해 주세요.")
        return
        
    with open(cookie_file, "r", encoding="utf-8") as f:
        cookies = json.load(f)
    print(f"로드된 쿠키 개수: {len(cookies)}")
    
    async with async_playwright() as p:
        # 헤드리스 모드로 크롤링 가능 여부 확인
        print("Chromium 브라우저 시작 (Headless=True)...")
        browser = await p.chromium.launch(
            headless=True,
            args=[
                "--disable-blink-features=AutomationControlled",
                "--no-sandbox",
                "--disable-setuid-sandbox"
            ]
        )
        
        # 브라우저 컨텍스트 생성 및 쿠키 주입
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
            viewport={"width": 1280, "height": 900},
            locale="ko-KR,ko;q=0.9,en-US;q=0.8,en;q=0.7"
        )
        await context.add_init_script("delete navigator.__proto__.webdriver;")
        
        # 쿠키 주입
        await context.add_cookies(cookies)
        print("세션 쿠키 브라우저에 주입 완료.")
        
        page = await context.new_page()
        
        # 2. AAPL 종목 분석 페이지로 다이렉트 이동
        ticker = "AAPL"
        url = f"https://seekingalpha.com/symbol/{ticker}"
        print(f"{ticker} 종목 분석 페이지({url})로 이동 중...")
        
        try:
            await page.goto(url, wait_until="domcontentloaded", timeout=60000)
            print("페이지 로딩 중... 자바스크립트 안정화 대기(10초)...")
            await page.wait_for_timeout(10000)
        except Exception as e:
            print(f"페이지 이동 중 오류 발생: {e}")
            await page.screenshot(path="scratch/crawl_error.png")
            await browser.close()
            return
            
        # 3. 크롤링 결과 화면 캡처 및 HTML 저장
        screenshot_path = "scratch/crawl_result.png"
        html_path = "scratch/crawl_result.html"
        await page.screenshot(path=screenshot_path)
        print(f"크롤링 결과 스크린샷 저장 완료: {screenshot_path}")
        
        html_content = await page.content()
        with open(html_path, "w", encoding="utf-8") as f:
            f.write(html_content)
        print(f"HTML 소스 저장 완료: {html_path}")
        
        # 4. 로그인 상태 유지 여부 검증
        page_title = await page.title()
        print(f"페이지 제목: {page_title}")
        
        # 로그아웃 상태일 때 나타나는 'LOG IN' 버튼이 돔에 남아있는지 확인
        login_btn_count = await page.locator("text=LOG IN, text=Log In").count()
        print(f"화면 내 로그인 버튼 개수: {login_btn_count}")
        if login_btn_count == 0:
            print("결과: 로그인 상태가 정상적으로 유지되고 있습니다! (LOG IN 버튼 미노출)")
        else:
            print("결과: 로그인 세션 주입에 실패했거나 세션이 만료되었습니다. (LOG IN 버튼이 다시 보임)")
            
        # 5. 시범 데이터 추출 (분석 기사 제목 및 링크)
        print("\n--- 시범 데이터 추출 (최신 분석/뉴스 타이틀) ---")
        
        # Seeking Alpha 종목 페이지의 분석글 영역 탐색 (일반적인 제목 셀렉터)
        # Seeking Alpha는 아티클 제목에 보통 data-test-id="post-list-author-article-title" 이나 a[data-test-id="post-title"] 등을 사용함
        # 동적 구조를 고려하여 넓은 범위의 셀렉터로 제목을 찾음
        title_selectors = [
            "a[data-test-id='post-title']",
            "a[data-test-id='article-title']",
            "h3[data-test-id='post-title'] a",
            "[data-test-id='article-list-item'] a",
            "a[href*='/article/']"
        ]
        
        articles_found = []
        for selector in title_selectors:
            try:
                locators = page.locator(selector)
                count = await locators.count()
                if count > 0:
                    print(f"셀렉터 '{selector}' 매칭 성공 (검색된 아이템 수: {count})")
                    for i in range(min(count, 10)):  # 상위 10개만 추출
                        title_text = await locators.nth(i).inner_text()
                        link = await locators.nth(i).get_attribute("href")
                        if title_text and link:
                            full_link = f"https://seekingalpha.com{link}" if link.startswith("/") else link
                            articles_found.append({"title": title_text.strip(), "link": full_link})
                    break
            except Exception as e:
                continue
                
        # 추출된 아티클 출력
        if articles_found:
            for idx, art in enumerate(articles_found, 1):
                print(f"[{idx}] {art['title']}")
                print(f"    URL: {art['link']}")
        else:
            print("아티클 제목 자동 추출 실패. (사이트 구조 변경 또는 렌더링 지연 가능성)")
            print("팁: scratch/crawl_result.png 및 crawl_result.html 파일을 열어 데이터 구조를 확인해 보세요.")
            
        await browser.close()

if __name__ == "__main__":
    asyncio.run(run())
