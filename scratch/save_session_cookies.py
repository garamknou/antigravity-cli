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

def prompt_input(prompt):
    # sys.stdin 및 stdout 인코딩 재설정
    if hasattr(sys.stdin, 'reconfigure'):
        sys.stdin.reconfigure(encoding='utf-8')
    return input(prompt)

async def wait_for_user_confirm():
    loop = asyncio.get_event_loop()
    # input()은 블로킹 함수이므로 run_in_executor에서 비동기 처리
    await loop.run_in_executor(None, prompt_input, "\n로그인 및 캡차 해결을 모두 마쳤다면 [여기에 Enter 키]를 눌러주세요...\n")

async def run():
    print("Playwright 기동 중 (수동 로그인 대기 모드)...")
    async with async_playwright() as p:
        browser = await p.chromium.launch(
            headless=False,  # 실제 조작을 위해 False 유지
            args=[
                "--disable-blink-features=AutomationControlled",
                "--no-sandbox",
                "--disable-setuid-sandbox"
            ]
        )
        
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
            viewport={"width": 1280, "height": 800},
            locale="ko-KR,ko;q=0.9,en-US;q=0.8,en;q=0.7"
        )
        await context.add_init_script("delete navigator.__proto__.webdriver;")
        page = await context.new_page()
        
        url = "https://seekingalpha.com"
        print(f"Seeking Alpha 메인 페이지({url})로 이동합니다...")
        await page.goto(url, wait_until="domcontentloaded")
        await page.wait_for_timeout(3000)
        
        # 메인 페이지에서 우상단 'LOG IN' 버튼이 보일 때 클릭 시도
        print("로그인 버튼 클릭 시도 중...")
        try:
            login_btn = page.locator("text=LOG IN, text=Log In, [data-test-id='login-button']").first
            if await login_btn.is_visible():
                await login_btn.click()
                print("로그인 모달이 로드되었습니다.")
        except Exception as e:
            print(f"자동 로그인 모달 열기 실패 (직접 브라우저에서 진행해 주세요): {e}")
            
        print("\n" + "="*60)
        print(" [수동 로그인 진행 가이드]")
        print(" 1. 브라우저 화면에서 아래 정보로 로그인을 완료해 주세요:")
        print("    - ID: seekingalpha.six@outlook.com")
        print("    - PW: Y2t9E9qF")
        print(" 2. Cloudflare/PerimeterX 캡차가 나타나면 수동으로 풀어주세요.")
        print(" 3. 로그인이 완전히 완료되어 주가 및 개인 화면이 나타나면")
        print("    이 터미널 창으로 돌아와 [Enter] 키를 입력해 주시기 바랍니다.")
        print("="*60 + "\n")
        
        # 사용자가 엔터를 칠 때까지 무한 대기
        await wait_for_user_confirm()
        
        # 엔터 입력 시점의 쿠키 저장
        print("엔터 감지됨. 세션 쿠키를 수집합니다...")
        await page.wait_for_timeout(2000)  # 추가 세션 정합성을 위해 2초 대기
        cookies = await context.cookies()
        
        cookie_path = "scratch/cookies.json"
        os.makedirs("scratch", exist_ok=True)
        with open(cookie_path, "w", encoding="utf-8") as f:
            json.dump(cookies, f, indent=4)
            
        print(f"세션 쿠키가 {cookie_path}에 안전하게 저장되었습니다!")
        print(f"저장된 쿠키 개수: {len(cookies)}")
        
        # 로그인 상태 스크린샷 남겨서 에이전트가 확인 가능하게 함
        await page.screenshot(path="scratch/login_success_verification.png")
        print("로그인 확인용 스크린샷이 scratch/login_success_verification.png에 저장되었습니다.")
        
        await browser.close()

if __name__ == "__main__":
    asyncio.run(run())
