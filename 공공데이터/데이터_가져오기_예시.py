"""
공공데이터 포털 데이터 가져오기 예제  2021.02.06
홈페이지 예시가 Python2 버전이라 Python3버전으로 가져옴
두 가지 방법으로 Url Parse하는 방법과
requests 라이브러리 사용하는 방법
"""
from urllib import request, parse
import requests

url = 'http://openapi.airkorea.or.kr/openapi/services/rest/ArpltnInforInqireSvc/getMsrstnAcctoRltmMesureDnsty'
parms = {
    'ServiceKey': request.unquote('VXsaG%2B4LKw1ZEbhE%2FDpmlJm4RQiHtreZp2ksrBKmQf4quRUpkOU8xd5423ZqgFmAgFnM3%2BG1XsTTrhZHz7lG4g%3D%3D'),
    'numOfRows': '1',
    'pageNo': '20',  # 강서구
    'sidoName': '서울',
    'ver': '1.3',
    '_returnType': 'json'
}
queryParams = '?' + parse.urlencode(
    {
        parse.quote_plus('ServiceKey'): request.unquote('VXsaG%2B4LKw1ZEbhE%2FDpmlJm4RQiHtreZp2ksrBKmQf4quRUpkOU8xd5423ZqgFmAgFnM3%2BG1XsTTrhZHz7lG4g%3D%3D'),
        parse.quote_plus('numOfRows'): '10',
        parse.quote_plus('pageNo'): '1',
        parse.quote_plus('stationName'): '종로구',
        parse.quote_plus('dataTerm'): 'DAILY',
        parse.quote_plus('ver'): '1.3',
        parse.quote_plus('_returnType'): 'json'
    }
)

# 방법 1
req = request.Request(url + queryParams)
with request.urlopen(req) as url:
    s = url.read()
    print(s)

# 방법 2
res = requests.get(url="http://openapi.airkorea.or.kr/openapi/services/rest/ArpltnInforInqireSvc/getCtprvnRltmMesureDnsty",
                   params=parms)
for i in res.json()['list']:
    print("\n", i)

