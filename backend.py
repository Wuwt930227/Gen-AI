from flask import Flask, request, jsonify, render_template, url_for#???
from flask_cors import CORS
import warnings
import tensorflow as tf
from sentence_transformers import SentenceTransformer
import faiss
import numpy as np
import chardet
import openai
from collections import deque

# 忽略 TensorFlow 的未來警告
warnings.filterwarnings("ignore", category=FutureWarning)

# 初始化 Flask 應用
app = Flask(__name__, template_folder='templates')  # 指定模板文件夾
CORS(app)  # 啟用 CORS，允許跨域請求

#  建立關鍵字對應圖片的字典
image_dict = {
    "登入": ["登入頁面.png"], 
    "首頁": ["首頁.png"],
    "系統": ["系統.png"],
    "收發": ["總收發.png"],
    "收文": ["總收發.png"],
    "分文": ["總收發.png"],
    "基本資": ["機關1.png", "機關2.png"], 
    "機關資": ["機關1.png", "機關2.png"],
    "核印": ["機關3.png"],
    "簽名": ["機關3.png"],
    "代理": ["代理人設定.png", "代理人設定時間.png"],
    "行事曆": ["行事曆1.png"],
    "新增行事曆": ["行事曆2.png"],
    "公告": ["公告1.png"],
    "新增公告": ["公告2.png"],
    "機關管理": ["機關管理1.png"],
    "管理新增": ["機關管理2.png"],
    "角色": ["角色1.png"],
    "新增角色": ["角色2.png"],
    "角色新增": ["角色2.png"],
    "個人": ["個人資料.png"],
    "組織": ["組織架構1.png", "組織架構2.png", "組織架構調整.png"],
    "標點": ["通用標點字符.png"],
    "簽核": ["通用簽核.png"],
    "部門": ["部門人員.png", "部門合併.png", "部門拆分.png", "部門拆分2.png", "部門轉移.png"],
    "職務": ["新增職務.png", "新增職務權限.png", "職務查看.png", "職務設定匯入.png", "職務編輯.png", "職務調整.png", "職務權限.png"],
    "順會": ["順會分會.png"],
    "會辦": ["經辦會辦.png"],
    "維護": ["維護.png"],
    "公文群組": ["公文共用群組.png"],
    "機關人員": ["機關人員.png", "機關人員新增.png"],
}


