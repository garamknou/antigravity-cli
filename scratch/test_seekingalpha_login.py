import asyncio
import os
import sys
import json
import tempfile

# 임시 디렉토리 환경변수 강제 지정 (샌드박스 및 권한 이슈 방지)
tmp_dir = os.path.abspath("scratch/tmp")
try:
    os.makedirs(tmp_dir, exist_ok=True)
except Exception:
    pass
os.environ['TEMP'] = tmp_dir
os.environ['TMP'] = tmp_dir
os.environ['TMPDIR'] = tmp_dir
tempfile.tempdir = tmp_dir

from playwright.async_api import async_playwright

async def run():
    print("Playwright 시작 중...")
    async with async_playwright() as p:
        print("Chromium 브라우저 시작 (Headless=True)...")
        # 실제 사용자 브라우저처럼 보이기 위한 옵션 설정
        browser = await p.chromium.launch(
            headless=True,
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
        
        # webdriver 탐지 우회
        await context.add_init_script("delete navigator.__proto__.webdriver;")
        
        page = await context.new_page()
        
        # 1. Seeking Alpha 메인 페이지 접속
        url = "https://seekingalpha.com"
        print(f"{url} 접속 시도 중...")
        
        try:
            # domcontentloaded 상태로 접속 후 안정화 대기
            await page.goto(url, wait_until="domcontentloaded", timeout=60000)
            await page.wait_for_timeout(5000)  # 자바스크립트 실행 완료 대기
        except Exception as e:
            print(f"페이지 접속 중 오류 발생: {e}")
            await page.screenshot(path="scratch/error_screenshot.png")
            await browser.close()
            return
            
        print("페이지 로드 완료. 'LOG IN' 버튼 검색 중...")
        
        # 2. 'LOG IN' 버튼 매칭 및 클릭 시도
        # 다양한 셀렉터 후보군을 지정하여 탐색
        login_selectors = [
            "text=LOG IN",
            "text=Log In",
            "button:has-text('LOG IN')",
            "a:has-text('LOG IN')",
            "[data-test-id='login-button']",
            "button:has-text('Log In')"
        ]
        
        login_btn = None
        for selector in login_selectors:
            try:
                locator = page.locator(selector).first
                if await locator.is_visible():
                    login_btn = locator
                    print(f"매칭된 로그인 버튼 셀렉터: {selector}")
                    break
            except Exception:
                continue
                
        if not login_btn:
            print("오류: 화면에서 'LOG IN' 버튼을 찾을 수 없습니다.")
            await page.screenshot(path="scratch/login_btn_not_found.png")
            await browser.close()
            return
            
        # 버튼 클릭
        await login_btn.click()
        print("로그인 버튼 클릭 완료. 로그인 모달 대기 중...")
        await page.wait_for_timeout(5000)  # 모달 로드 대기
        
        # 클릭 후 스크린샷 저장
        await page.screenshot(path="scratch/after_login_click.png")
        print("클릭 후 스크린샷 저장 완료: scratch/after_login_click.png")
        
        # 3. 로그인 입력 필드 탐색
        email_selector = "input[type='email'], input[name='email'], input[placeholder*='Email']"
        password_selector = "input[type='password'], input[name='password'], input[placeholder*='Password']"
        submit_selector = "button[type='submit'], button:has-text('Sign In'), button:has-text('LOG IN'), button:has-text('Log In')"
        
        email_locator = page.locator(email_selector).first
        password_locator = page.locator(password_selector).first
        submit_locator = page.locator(submit_selector).first
        
        if await email_locator.is_visible() and await password_locator.is_visible():
            print("로그인 폼 감지 성공. 자격 증명 입력 중...")
            
            # 정보 입력
            await email_locator.fill("seekingalpha.six@outlook.com")
            await page.wait_for_timeout(1000)
            await password_locator.fill("Y2t9E9qF")
            await page.wait_for_timeout(1000)
            
            # 입력 상태 스크린샷
            await page.screenshot(path="scratch/login_credentials_entered.png")
            print("자격 증명 입력 후 스크린샷 저장 완료.")
            
            # 로그인 버튼 클릭
            if await submit_locator.is_visible():
                print("로그인 제출 버튼 클릭...")
                await submit_locator.click()
                await page.wait_for_timeout(10000)  # 로그인 처리 및 리다이렉트 대기
                
                # 로그인 시도 후 상태 스크린샷
                await page.screenshot(path="scratch/after_login_submit.png")
                print("로그인 제출 후 스크린샷 저장 완료: scratch/after_login_submit.png")
                
                # 로그인 성공 여부 판별 (로그인 버튼이 사라졌거나, My Portfolio 등의 텍스트 감지)
                # 혹은 쿠키 확인
                cookies = await context.cookies()
                # 닉네임이나 사용자 정보가 페이지에 나타나는지 확인
                page_content = await page.content()
                
                # 세션 쿠키 저장
                with open("scratch/cookies.json", "w", encoding="utf-8") as f:
                    json.dump(cookies, f, indent=4)
                print("쿠키 세션 저장 완료: scratch/cookies.json")
                
                # 간단한 로그인 성공 여부 검증
                is_logged_in = False
                for c in cookies:
                    if "session" in c["name"].lower() or "auth" in c["name"].lower() or "user" in c["name"].lower():
                        is_logged_in = True
                        
                print(f"로그인 검증 결과: {'성공 추정' if is_logged_in else '실패 추정 (쿠키 미확인)'}")
            else:
                print("오류: 로그인 제출 버튼을 찾을 수 없습니다.")
        else:
            print("오류: 이메일 또는 비밀번호 입력 필드가 모달 내에 존재하지 않습니다.")
            
        await browser.close()

if __name__ == "__main__":
    asyncio.run(run())
