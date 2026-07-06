# -*- coding: utf-8 -*-
import requests
from bs4 import BeautifulSoup
import re

def check_pages():
    url = "https://www.yes24.com/product/category/daybestseller?pageNumber=1&pageSize=24&categoryNumber=001001003&type=day"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/149.0.0.0 Safari/537.36"
    }
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.text, "lxml")

    print("--- '총' 또는 '건' 또는 '개' 포함 텍스트 ---")
    # find_all(string=...) 사용
    for el in soup.find_all(string=re.compile(r"총|건|개")):
        text = el.strip()
        if len(text) < 100 and any(char.isdigit() for char in text):
            print(text)

    print("\n--- 페이지네이션 요소 탐색 ---")
    # paging 관련 클래스 찾기
    paging_divs = soup.select("div.yesUI_pagen, div.paging, div.page, div.pagen")
    for div in paging_divs:
        print(f"DIV 태그 발견 - 클래스: {div.get('class')}")
        print(f"텍스트 내용: {div.text.strip()}")
        # 내부의 a 태그(페이지 번호)들
        a_tags = div.select("a")
        for a in a_tags:
            print(f"  A 태그: href={a.get('href')}, text={a.text.strip()}")

    # 그냥 모든 클래스 중에 'page'나 'paging' 들어가는 것들
    print("\n--- 'page'가 포함된 클래스들 ---")
    for tag in soup.find_all(class_=True):
        classes = tag.get("class")
        if any("page" in c.lower() or "paging" in c.lower() for c in classes):
            print(f"태그: {tag.name}, 클래스: {classes}, 텍스트: {tag.text.strip()[:100]}")

if __name__ == "__main__":
    check_pages()
