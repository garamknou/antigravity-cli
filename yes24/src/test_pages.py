# -*- coding: utf-8 -*-
import requests
from bs4 import BeautifulSoup

def test_pages():
    url = "https://www.yes24.com/product/category/BestSellerContents"
    headers = {
        "Referer": "https://www.yes24.com/product/category/daybestseller?pageNumber=1&pageSize=24&categoryNumber=001001003&type=day",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/149.0.0.0 Safari/537.36",
        "X-Requested-With": "XMLHttpRequest"
    }
    
    pages = [1, 15, 16, 17, 18]
    for p in pages:
        params = {
            "categoryNumber": "001001003",
            "sumGb": "06",
            "sex": "A",
            "age": "255",
            "goodsTp": "0",
            "addOptionTp": "0",
            "excludeTp": "2",
            "pageNumber": str(p),
            "pageSize": "24",
            "goodsStatGb": "06",
            "eBookTp": "0",
            "bestType": "DAY_BESTSELLER",
            "type": "day"
        }
        res = requests.get(url, params=params, headers=headers)
        soup = BeautifulSoup(res.text, "lxml")
        li_list = soup.select("li[data-goods-no]")
        print(f"\n--- 페이지: {p} (총 {len(li_list)}개 상품) ---")
        for i, li in enumerate(li_list[:5]):
            goods_no = li.get("data-goods-no")
            name_el = li.select_one("a.gd_name")
            name = name_el.text.strip() if name_el else "이름없음"
            print(f"  {i+1}. ID: {goods_no} - {name[:30]}")

if __name__ == "__main__":
    test_pages()
