from flask import Flask, jsonify, render_template, request
from flask_cors import CORS
from pymongo import MongoClient
from bson import ObjectId
import json
import base64
import hashlib
import struct
import time
from base64 import b64decode

import requests
from Crypto.Cipher import AES
from Crypto.Util.Padding import unpad

from 三角洲小涛查.mySpider.script.chaojiying import Chaojiying_Client
app = Flask(__name__)
CORS(app)  # 允许跨域访问

# 连接 MongoDB
client = MongoClient("mongodb://localhost:27017/")
db = client["zidan"]   # 你的数据库
collection = db["zidan"]  # 你的集合



key_words = [
    875652709, 929261158, 912602681, 962814305,
    959656038, 859333937, 808608355, 946025318
]
iv_words = [
    1665232450, 2037021011, 1196389236, 1433161059
]


aaa = [
        ["=", "*|"],
        ["1", "aa|a"],
        ["2", "ab|a"],
        ["3", "ba|a"],
        ["4", "t|tc"],
        ["5", "t|ts"],
        ["8", "r|oq"],
        ["9", "f|oz"],
        ["0", "j|rz"]
    ]

def UrlDecBase64(encoded_str):
    """
    URL安全的Base64解码函数，包含特殊字符替换

    参数:
    encoded_str: Base64编码的字符串

    返回:
    bytes: 解码后的字节数据
    """
    # 第一步：将 '*|' 替换为 '='
    for replacement in aaa:
        old_char, new_char = replacement
        encoded_str = encoded_str.replace(new_char, old_char)

    # 第二步：URL安全字符替换：- -> +, _ -> /
    encoded_str = encoded_str.replace('-', '+').replace('_', '/')

    # 第三步：添加Base64填充字符（=）
    padding = len(encoded_str) % 4
    if padding:
        encoded_str += '=' * (4 - padding)

    # Base64解码，返回字节数据
    return base64.b64decode(encoded_str).decode('utf-8')

# === 转换为 bytes ===
aeskey = b''.join(struct.pack('>I', w) for w in key_words)
iv = b''.join(struct.pack('>I', w) for w in iv_words)



    # === 修复 base64 填充 ===
def fix_base64_padding(s):
    return s + '=' * ((4 - len(s) % 4) % 4)


# === 解密函数 ===
def decrypt(cipher_b64, key, iv):
    try:
        cipher_bytes = b64decode(cipher_b64)
        cipher = AES.new(key, AES.MODE_CBC, iv)
        plaintext = unpad(cipher.decrypt(cipher_bytes), AES.block_size)
        return plaintext.decode('utf-8')
    except Exception as e:
        return f"解密失败: {e}"



def getimgcapth(imgurl):
    req = requests.get(imgurl)
    if req.status_code == 200:
        imgdata=req.json()['data']['captcha'].replace('data:image/png;base64,', '')
        chaojiying=Chaojiying_Client('2173554564','ding20031110@..','928080')
        capth=chaojiying.PostPic_base64(imgdata, 1004)['pic_str']
        print(capth)
        return capth,req.json()['data']['key']
    else:
        return None,None

def gettoken( a):
    # 1. 获取 10 位 Unix 时间戳（秒级）
    tim = str(int(time.time() - 3))
    # 2. 第一次 MD5 (a + tim)
    # print(a+tim)
    a1 = hashlib.md5((a + tim).encode()).hexdigest()
    # print(a1)
    # 3. 第二次 MD5 (tim + a1)
    # print(tim+a1)
    result = hashlib.md5((tim + a1 + '私自使用，后果自负！我方保留起诉权利！').encode()).hexdigest()

    return result, tim  # 同时返回结果和时间戳，方便调用方使用



# 转换 ObjectId 为字符串 + 解析 listdata
def serialize_doc(doc):
    doc["_id"] = str(doc["_id"])
    if "jsondatas" in doc:
        jd = doc["jsondatas"]
        # 解析 listdata 字符串
        if "listdata" in jd and isinstance(jd["listdata"], str):
            try:
                jd["listdata"] = json.loads(jd["listdata"])
            except json.JSONDecodeError:
                jd["listdata"] = {"a": [], "b": []}
        doc = jd  # 直接返回 jsondatas 的内容
    return doc
def getcalculate(requestjson):
    a=requestjson['slots']
    # 映射字典
    key_mapping = {
        'gun': 'is_gun',
        'helmet': 'is_tk',
        'armor': 'is_hj',
        'chest': 'is_xg',
        'backpack': 'is_bb',
        'pistol': 'is_sq'
    }

    # 使用列表推导式更高效地构建参数字符串
    params = [f"{key_mapping[key]}={'1' if value else '0'}" for key, value in a.items()]
    st = '&' + '&'.join(params)
    #key_num, key = getimgcapth('https://www.acgice.com/api/captcha')
    url = f"https://api.acgice.com/api/sjz/jzv3_diy?zb={str(int(requestjson['targetValue'])-int(requestjson['currentValue']))}&key={requestjson['captchaKey']}&key_num={requestjson['captcha']}{st}&token=196d54b0aed789ef9d9eae4e53f99c84&timestamp=1757659207"
    url = url.split('&token')[0]
    token, tim = gettoken(url.split('?')[1])
    url = url + '&token=' + token + '&timestamp=' + tim
    payload = {}
    headers = {
        'accept': 'application/json, text/plain, */*',
        'accept-language': 'zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6',
        'cache-control': 'no-cache',
        'origin': 'https://www.acgice.com',
        'pragma': 'no-cache',
        'priority': 'u=1, i',
        'referer': 'https://www.acgice.com/',
        'sec-ch-ua': '"Chromium";v="140", "Not=A?Brand";v="24", "Microsoft Edge";v="140"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Windows"',
        'sec-fetch-dest': 'empty',
        'sec-fetch-mode': 'cors',
        'sec-fetch-site': 'same-site',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/140.0.0.0 Safari/537.36 Edg/140.0.0.0'
    }

    response = requests.request("GET", url, headers=headers, data=payload)


    try:
        jsondata=response.json()
        if jsondata['data']==[]:
            return response.json()
        else:
            data = fix_base64_padding(response.json()['data'])
            data = decrypt(data, aeskey, iv)
            return UrlDecBase64(data.replace('非法侵入计算机信息系统罪,我方企业保留报警和起诉权利', ''))
    except:
            return None
@app.route("/api/ammo")
def get_ammo_data():
    data = [serialize_doc(doc) for doc in collection.find()]
    return jsonify(data)
@app.route("/")
def index():
    return render_template("index.html")

@app.route("/diyzhanbei")
def diyzhanbei():
    return render_template("zhabbeidiy.html")

@app.route('/calculate', methods=['POST'])
def calculate():
    # 获取前端发送的数据
    data = request.json
    result = getcalculate(data)
    return result


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
