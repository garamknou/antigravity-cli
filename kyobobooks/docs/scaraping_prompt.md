# 데이터 수집에 꼭 필요한 핵심 정보

## 네트워크 메뉴를 통해 실제 데이터를 가져오는 URL
- **기본 URL**: `https://store.kyobobook.co.kr/api/gw/best/best-seller/online`
- **Query Parameters**:
  - `page`: 페이지 번호 (예: `1`, `2`, ...)
  - `per`: 페이지당 도서 개수 (기본값: `20`)
  - `period`: 기간 코드 (일간 베스트셀러는 `001`)
  - `dsplDvsnCode`: 전시 구분 코드 (`001`)
  - `dsplTrgtDvsnCode`: 전시 대상 구분 코드 (`004`)
  - `saleCmdtClstCode`: 카테고리 분류 코드 (컴퓨터/IT는 `33`)

## 해당 Request에 대한 Header 정보
HTTP 요청 정보 중 보안 통과를 위해 가장 중요한 정보는 `x-api-gw-key` 헤더입니다. 이 헤더가 없을 경우 `401 Unauthorized` 에러를 반환합니다.

- **Host**: `store.kyobobook.co.kr`
- **User-Agent**: `Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36`
- **Referer**: `https://store.kyobobook.co.kr/bestseller/online/daily/domestic/33?page=1`
- **Content-Type**: `application/json`
- **x-api-gw-key**: `[Playwright 등으로 동적 캡처하여 사용해야 하는 게이트웨이 보안 키]`
  *(예시 키값: `eyJhbGciOiJkaXIiLCJlbmMiOiJBMjU2R0NNIn0..fGckpIc2rocGlaNW.tAQwssCAjZPkubQdkN4mxNuV_XEza4qmGB-uNJwIs032Enxo9a9ElYpvfVw8rEpp3seGnIBo4N9cAjpD56WGPuIkK-xrJfVkp3RRgwreIZoM-As3hxzMqpc-Rs38cnx-GAu9gUNJ.Mwf9x7KZlcYv9TdHt0YSEg`)*

## Payload
- GET 요청 방식을 사용하므로 POST Payload는 존재하지 않고 Query String 파라미터를 그대로 사용합니다.

## 응답 예시 (JSON 데이터의 일부 정보)
```json
{
  "data": {
    "bestSeller": [
      {
        "prstRnkn": 1,
        "saleCmdtid": "S000219929026",
        "cmdtName": "클로드 코드로 시작하는 실전 에이전틱 코딩",
        "chrcName": "Goos Kim",
        "pbcmName": "더 타이즈",
        "rlseDate": "20260521",
        "price": 33000,
        "sapr": 29700,
        "dscnRate": 10,
        "buyRevwNumc": 43,
        "buyRevwRvgr": 9.82,
        "saleCmdtClstName": "컴퓨터/IT"
      }
      // ... 추가 도서 정보
    ]
  }
}
```
데이터를 수집(크롤링 또는 API 호출)할 때마다 실제 요청 정보(URL, Header, Payload)와 응답 구조를 기반으로 파이썬 스크래핑 코드를 안전하게 작성합니다.