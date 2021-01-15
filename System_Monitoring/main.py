import uvicorn, requests, json, datetime, os, socket
from fastapi import FastAPI, Request, HTTPException
from fastapi.templating import Jinja2Templates
from requests.auth import HTTPBasicAuth
from pytz import timezone

KST = timezone('Asia/Seoul')
app = FastAPI(debug=True)
templates = Jinja2Templates(directory="templates")


@app.route("/")
async def index(request: Request):
    hostname = ["218.55.23.206", "218.55.23.207", "218.55.23.208", "13.125.246.197", "52.79.215.253", "52.79.250.228"
                , "218.55.23.200", "13.209.69.162"]
    net_arr = []
    es_port = []
    for _host in hostname:
        res = os.system("ping -n 1 {}".format(_host))
        net_arr.append("Active") if res == 0 else net_arr.append("Death")
    port = [5601, 9200, 9092, 5000]
    for _i in range(0, 6):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        res = sock.connect_ex((hostname[_i], 9200))
        es_port.append("Open") if res == 0 else es_port.append("Close")
        sock.close()
    kibana_port = []
    for _host2 in [hostname[0], hostname[3]]:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        res = sock.connect_ex((_host2, 5601))
        kibana_port.append("Open") if res == 0 else kibana_port.append("Close")
        sock.close()
    ca_system_port = []
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    res = sock.connect_ex((hostname[2], 5000))
    ca_system_port.append("Open") if res == 0 else ca_system_port.append("Close")
    sock.close()
    params = {
        "request": request,
        "id": "~",
        "c1r1": [hostname[0], net_arr[0], es_port[0], kibana_port[0]],
        "c1r2": [hostname[1], net_arr[1], es_port[1], ca_system_port[0]],
        "c1r3": [hostname[2], net_arr[2], es_port[2]],
        "c2r1": [hostname[3], net_arr[3], es_port[3], kibana_port[1]],
        "c2r2": [hostname[4], net_arr[4], es_port[4]],
        "c2r3": [hostname[5], net_arr[5], es_port[5]],
        "c3r1": [hostname[6], net_arr[6]],
        "c3r2": [hostname[7], net_arr[7]],
        "c3r3": ["hostname[8]"],
    }
    return templates.TemplateResponse("index.html", params)


# Please, if Product Env used to execution the 'run.sh'!
if __name__ == '__main__':
    uvicorn.run(app, host='0.0.0.0', port=8100)