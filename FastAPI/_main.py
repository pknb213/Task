from typing import Optional
from fastapi import FastAPI
from pymongo import MongoClient
import uvicorn, requests
from requests.auth import HTTPBasicAuth

app = FastAPI()

url = "mongodb://user:rkwjs12#@218.55.23.208:9400/?authSource=test&authMechanism=SCRAM-SHA-256"
client = MongoClient(url)
db = client['test']
col = db['col_1']

data = {
    "name": "Cheon",
    "age": 29
}


@app.get("/")
def read_root():
    print(list(col.find()))
    res = requests.get(url="http://52.79.215.253:9200/", auth=HTTPBasicAuth('elastic', 'rkwjs12#'))
    print(res.json(), type(res.json()))
    print(res.text, type(res.text))
    print(res.content, type(res.content))
    print(res.headers, type(res.headers))
    print(res.raw, type(res.raw))
    return {"id": list(map(str, col.find()))}


@app.get("/items/me")
def read_item_by_me():
    return {"my_items": "me"}


@app.get("/items/{item_id}")
def read_item(item_id: int, q: Optional[str] = None):
    x = col.insert_one(data)
    return {"item_id": item_id, "q": q, "data": str(x)}


# Please, if Product Env used to execution the 'run.sh'!
if __name__ == '__main__':
    uvicorn.run(app, host='0.0.0.0', port=8000)