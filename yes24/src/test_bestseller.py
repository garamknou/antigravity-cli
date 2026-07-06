# -*- coding: utf-8 -*-
import requests
from bs4 import BeautifulSoup

def test_bestseller_page():
    url = "https://www.yes24.com/product/category/bestseller"
    params = {
        "pageNumber": "1",
        "pageSize": "120", # 120개로 테스트
        "categoryNumber": "001001003"
    }
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/149.0.0.0 Safari/537.36"
    }
    
    res = requests.get(url, params=params, headers=headers)
    print(f"상태 코드: {res.status_code}")
    soup = BeautifulSoup(res.text, "lxml")
    
    # li 상품 태그 탐색
    li_list = soup.select("li[data-goods-no]")
    print(f"li[data-goods-no] 개수: {len(li_list)}")
    
    for i, li in enumerate(li_list[:5]):
        goods_no = li.get("data-goods-no")
        name_el = li.select_one("a.gd_name")
        name = name_el.text.strip() if name_el else "이름없음"
        print(f"  {i+1}. ID: {goods_no} - {name[:30]}")

if __name__ == "__main__":
    test_bestseller_page()
