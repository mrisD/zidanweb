from flask import Flask, jsonify, render_template
from flask_cors import CORS
from pymongo import MongoClient
from bson import ObjectId
import json

app = Flask(__name__)
CORS(app)  # 允许跨域访问

# 连接 MongoDB
client = MongoClient("mongodb://localhost:27017/")
db = client["zidan"]   # 你的数据库
collection = db["zidan"]  # 你的集合

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

@app.route("/api/ammo")
def get_ammo_data():
    data = [serialize_doc(doc) for doc in collection.find()]
    return jsonify(data)
@app.route("/")
def index():
    return render_template("index.html")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
