from pytrends.request import TrendReq
import pandas as pd

# 구글 트렌드 연결
pytrends = TrendReq(hl='ko-KR', tz=360)

# 검색할 키워드 설정 (예: 요즘 핫한 k-pop 아티스트나 장르)
keywords = ["k-pop"]
pytrends.build_payload(keywords, timeframe='today 1-m') # 최근 1달간 데이터

# 데이터 가져오기
data = pytrends.interest_over_time()

# 결과 출력
print("--- 구글 트렌드 데이터 샘플 ---")
print(data.head())