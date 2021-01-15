import uvicorn, requests, json, datetime
from typing import Optional
from fastapi import FastAPI, Request, HTTPException
from requests.auth import HTTPBasicAuth
from pytz import timezone

KST = timezone('Asia/Seoul')
app = FastAPI()
ELASTICSEARCH_SERVER_IP = 'http://52.79.215.253:9200/'


class PAYLOAD:
    # payload 내의 json data 예시 (데이터 구조 기반 규격 정의)
    def __init__(self, *args):
        for i, arg in enumerate(args):
            # print(i, arg)
            if i is 0:
                request = arg
                self.host = request.client.host + ":" + str(request.client.port)
            elif i is 1:
                self.partner_id = arg
            elif i is 2:
                self.model_name = arg
            elif i is 3:
                self.device_id = arg
            if 'model_name' not in self.__dict__:
                self.model_name = None
            if 'device_id' not in self.__dict__:
                self.device_id = None

    def body(self):
        _body = {
            "appliance_id": self.partner_id,  # 요청 가전사 아이디
            "appliance_auth_token": "",  # 가전사 엑세스 토큰
            "response_type": 1,  # 요청 응답 타입, 1일 경우 callback_url 필수 (0: Sync, 1: Async)
            "callback_data_type": 0,  # 응답 데이터 타입 (0: json, 1: csv)
            "callback_transfer_type": 0,  # 비동기 통신 타입 (0: http, 1: ftp, 2: socket)
            "callback_url": self.host,  # 비동기 callback 수신용 가전사 legacy ip:port
            "function_id": 0,  # 요청 분석/집계 항목, 세자리 숫자로 표현 됨 (1xx: 집계 데이터, 2xx: 반응분석, 3xx: 예측분석)
            "model_name": self.model_name,  # 가전 모델명 (분석 결과 필터링이 특정 모델으로 제한될 경우)
            "device_id": self.device_id,  # 가전 아이디 (분석 결과가 특정 가전으로 제한되는 경우, ex) 고장 예측)
            "period_start": "",  # 집계, 분석 시작 범위 일자
            "period_end": ""  # 집계, 분석 종료 범위 일자
        }
        if self.model_name is None:
            _body.pop('model_name')
        if self.device_id is None:
            _body.pop('device_id')
        return _body


parse = {
    "hyundai": 'iot-daeyoung-',  # 0 : Daeyoung HunDae Rental Care
    "everybot": 'iot-everybot-',  # 1 : Everybot
    "grib": 'iot-grib-',  # 2 : Grib
    "cw": 'iot-ct-'  # 3 : ChoungWu C & T
}
partner = ['hyundai', 'everybot', 'grib', 'cw']
models = ['ha-831', 'ha-830', 'ra1000', 'rs900', 'rs300', 'g100sr', 'cafu15']


def date_query(args, device=None):
    if device is None:
        if len(args) is 0:
            return {}
        elif len(args) != 2:
            raise Exception
        else:
            st, et = args
        if len(st) < 6 or len(et) < 6:
            return {"error": "Time is short."}
        if st > et:
            return {"error": "Please, Start Time is bigger than End Time."}
        return {
            "query": {
                "range": {
                    "reqTime": {
                        "gte": st,
                        "lte": et
                    }
                }
            }
        }
    else:
        if len(args) is 0:
            return {
                "sort": [
                    {
                        "@timestamp": {
                            "order": "desc"
                        }
                    }
                ],
                "query": {
                    "match": {
                        "deviceId": device
                    }
                }
            }
        elif len(args) != 2:
            raise Exception
        else:
            st, et = args
        if len(st) < 6 or len(et) < 6:
            return {"error": "Time is short."}
        if st > et:
            return {"error": "Please, Start Time is bigger than End Time."}
        return {
            "sort": [
                {
                    "@timestamp": {
                        "order": "desc"
                    }
                }
            ],
            "query": {
                "bool": {
                    "must": [
                        {
                            "range": {
                                "reqTime": {
                                    "gte": st,
                                    "lte": et
                                }
                            }
                        },
                        {
                            "match": {
                                "deviceId": device
                            }
                        }
                    ]
                }
            }
        }


@app.get("/")
async def basic_route(request: Request):
    # todo : 가전사 소속 총 데이터 수 반환
    end_point = "_count"
    try:
        query = "{}*/{}".format(parse["hyundai"], end_point)
        url = ELASTICSEARCH_SERVER_IP + query
        res = requests.post(url=url, auth=HTTPBasicAuth('elastic', 'rkwjs12#'), json=date_query(request.query_params.keys()))
    except Exception as e:
        raise e
    print(url)
    payload = PAYLOAD(request, "hyundai").body()
    payload["count"] = res.json()['count']
    print(payload)
    return payload


@app.get("/api/v1/{partner_id}")
async def abc(partner_id: str, request: Request):
    # todo : 가전사 소속 전 모델 분석 결과
    if partner_id not in partner:
        raise HTTPException(status_code=404, detail="partner_id error: 0: Hundae Rental Care 1: Everybot 2: Grib 3: Chungwoo C&T")
    end_point = "_count"
    try:
        query = "{}*/{}".format(parse[partner_id], end_point)
        url = ELASTICSEARCH_SERVER_IP + query
        res = requests.post(url=url, auth=HTTPBasicAuth('elastic', 'rkwjs12#'), json=date_query(request.query_params.values()))
    except Exception as e:
        raise e
    print(url)
    payload = PAYLOAD(request, partner_id).body()
    payload["count"] = res.json()['count']
    return payload


@app.get("/api/v1/{partner_id}/{model_name}")
async def bcd(partner_id: str, model_name: str, request: Request):
    # todo : 가전사 소속 특정 모델 관련 분석 결과
    if partner_id not in partner:
        raise HTTPException(status_code=404, detail="partner_id error: 0: Hundae Rental Care 1: Everybot 2: Grib 3: Chungwoo C&T")
    elif model_name not in models:
        raise HTTPException(status_code=404, detail="model_name error ex) ha-831, ha-830, ra1000, rs900, rs300, g100sr, cafu15")
    end_point = "_count"
    try:
        query = "{}{}/{}".format(parse[partner_id], model_name, end_point)
        url = ELASTICSEARCH_SERVER_IP + query
        res = requests.post(url=url, auth=HTTPBasicAuth('elastic', 'rkwjs12#'), json=date_query(request.query_params.values()))
    except Exception as e:
        raise e
    print(url)
    payload = PAYLOAD(request, partner_id, model_name).body()
    payload["count"] = res.json()['count']
    return payload


@app.get("/api/v1/{partner_id}/{model_name}/{device_id}")
async def qwe(partner_id: str, model_name: str, device_id: str, request: Request):
    # todo : 가전사 소속 특정 가전 관련 분석 결과
    if partner_id not in partner:
        raise HTTPException(status_code=404, detail="partner_id error: 0: Hundae Rental Care 1: Everybot 2: Grib 3: Chungwoo C&T")
    elif model_name not in models:
        raise HTTPException(status_code=404, detail="model_name error ex) ha-831, ha-830, ra1000, rs900, rs300, g100sr, cafu15")
    end_point = "_search"
    # params = "q=deviceId:{}&_source=@timestamp&sort=@timestamp:desc&size=1".format(device_id)
    params = "&size=1"
    try:
        query = "{}{}/{}?{}".format(parse[partner_id], model_name, end_point, params)
        url = ELASTICSEARCH_SERVER_IP + query
        res = requests.post(url=url, auth=HTTPBasicAuth('elastic', 'rkwjs12#'), json=date_query(request.query_params.values(), device=device_id))
    except Exception as e:
        raise e
    print(url)
    payload = PAYLOAD(request, partner_id, model_name, device_id).body()
    payload["timestamp"] = str(datetime.datetime.strptime(
        res.json()['hits']['hits'][0]['_source']['@timestamp'],
        "%Y-%m-%dT%H:%M:%S.%fZ")+datetime.timedelta(hours=9))
        # "%Y-%m-%dT%H:%M:%S.%fZ").astimezone(KST)+datetime.timedelta(hours=9))
    print(payload)
    return payload


# Please, if Product Env used to execution the 'run.sh'!
if __name__ == '__main__':
    uvicorn.run(app, host='0.0.0.0', port=8000)
