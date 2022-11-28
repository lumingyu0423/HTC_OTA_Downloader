import requests
import time
import hashlib
from tqdm import tqdm

def getX1():
    t = str(timestamp)
    shift_value = 0
    for i in range(4, len(t)):
        tmp = t[len(t) - i]
        if tmp != '0':
            shift_value = int(tmp, 36)
            break
    time_head = t[:len(t) - shift_value]
    time_tail = t[len(t) - shift_value:]
    data = time_tail + SN + IMEI + time_head
    h = hashlib.sha256()
    h.update(data.encode('ascii'))
    return h.hexdigest().upper()

def getHTC1S():
    t = int(time_ms)
    tmp = SN + str(time_ms)
    if t <= 0:
        return tmp
    while True:
        i = t % 10
        if i == 0:
            t = t / 10
        else:
            index = int(len(tmp) - i)
            return tmp[index:] + tmp[:index]

def checkin():
    headers = {
        'User-Agent': 'Android-Checkin/8.0',
        'x-active-g': 'DivadGS38Omatump76'
    }
    queryjson = {
        "country":"US",
        "adminArea":"",
        "locality":"",
        "zip":"",
        "sub_locality":"",
        "statusCode":7,
        "digest":"",
        "locale":"en_US",
        "imei":"353002100146660",
        "timeZone":"GMT-08:00",
        "mFlag":"1",
        "aaReport":"com",
        "currentOS":"aos",
        "mAct":"NA",
        "mNos":"NA,NA",
        "sn_digest":"0",
        "model_number": model,
        "last_checkin_msec":"0",
        'timeStamp': timestamp,
        'checkin': {
            'build': {
                "carrier":"htc",
                "product":"htc_rtx",
                "revision":"0",
                "serialno":"FA0611N00326",
                "bootloader":"",
                "radio":"",
                "changelist":"",
                "build_type":"user",
                'build_taskid': taskid,
                'firmware_version': version
            },
            'client_version': 'A10.0(P)',
            "cid": cidnum,
            "checkin_type":"Manual", # Auto
            "mcc_mnc":"",
            "sim_mcc_mnc":"",
            "connection_media":"Wifi",
            "mid": modelid
        },
        'x1': getX1(),
        "retryType":"0"
    }
    r = requests.post(chkUrl, headers=headers, json=queryjson)
    return r.json()

def getOTAPkg():
    headers = {
        'User-Agent': 'Android-Checkin/8.0',
        'htc1s': htc1s
    }
    r = requests.get(uri, headers=headers, stream=True)
    total_size = int(r.headers['Content-Length'])
    pbar = tqdm(total=total_size, unit="B", unit_scale=True, ncols=100)
    with open(pkg, 'wb') as f:
        for chunk in r.iter_content(chunk_size=1024 * 1024):
            f.write(chunk)
            pbar.update(len(chunk))
        pbar.close()
    f.close()

checkinUrl = 'https://andchin-2.htc.com/htcfotacheckin/rest/checkin'
checkinUrlCN = 'https://andchin-2.htccomm.com.cn/htcfotacheckin/rest/checkin'

SN = 'FA0611N00326'
IMEI = '353002100146660'
timestamp = int(time.time() * 1000)

# china = input(">> China Variant? (Y/n): ")

# if china.upper() == 'Y':
    # chkUrl = checkinUrlCN
# else:
    # chkUrl = checkinUrl
chkUrl = checkinUrl

tid = 0

model = input(">> Model: ")
version = input(">> Version: ")
cidnum = input(">> CID: ")
taskid = input(">> Task id(Can be empty): ")
modelid = input(">> Model id(Can be empty): ")

# Model: htc_rtxspcs
# Version: 1.04.651.6
# CID: SPCS_001
# Taskid: 545803
# Mid: 2Q6U10000

#print(response)

restart = True

while restart:
    restart = False
    
    response = checkin()
    if taskid == "" : taskid = 1
    taskid = int(taskid) + tid
    print(taskid)
    
    if 'intent' in response:
        intent = response['intent'][0]
        print(intent)
        if 'data_uri' in intent:
            uri = intent['data_uri']
            pkg = intent['pkgFileName']
            for extra in intent['extra']:
                if extra['name'] == 'promptSize':
                    size = extra['value']
                    break
            time_ms = response['time_msec']
            htc1s = getHTC1S()
            print('>> FILE: ' + pkg)
            print('>> SIZE: ' + size)
            input("Press ENTER to download...")
            getOTAPkg()
            restart = False
        else:
            tid = tid + 1
            print(tid)
            restart = True
            time.sleep(5)
            #print('ERROR!!!')
    else:
        print('ERROR!!!')
