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

#  根據問題獲取對應的圖片 URL
def get_image_urls(query):
    image_urls = []
    for keyword, image_names in image_dict.items():
        if keyword in query:
            if isinstance(image_names, list):  # 如果是列表，就取全部
                image_urls.extend(
                    [url_for('static', filename=f'images/{img}', _external=True) for img in image_names]
                )
            else:  # 避免舊格式遺漏
                image_urls.append(url_for('static', filename=f'images/{image_names}', _external=True))
    
    return list(set(image_urls))  # 避免重複的圖片 URL


# 初始化儲存最近三個問題檢索內容的 deque
retrieved_history = deque(maxlen=3)

# 檢測文件編碼並載入文本數據
try:
    with open("億威電子-電子公文系統操作手冊.txt", "rb") as file:
        raw_data = file.read()
        result = chardet.detect(raw_data)
        encoding = result['encoding']

    with open("億威電子-電子公文系統操作手冊.txt", "r", encoding=encoding) as file:
        data = file.read()

    passages = data.split("\n\n")
    print(f"成功載入文本，共有 {len(passages)} 段落")
except Exception as e:
    print(f"載入文本數據時出錯: {e}")
    passages = []

# 初始化嵌入模型和 FAISS 索引
try:
    model = SentenceTransformer('all-MiniLM-L6-v2')
    embeddings = model.encode(passages, convert_to_tensor=True).cpu().numpy()
    print(f"嵌入向量生成成功，嵌入向量形狀: {embeddings.shape}")

    faiss_index = faiss.IndexFlatL2(embeddings.shape[1])  # 初始化 FAISS 索引
    faiss_index.add(embeddings)
    print(f"FAISS 索引初始化成功，包含的向量數量: {faiss_index.ntotal}")
except Exception as e:
    print(f"初始化嵌入或 FAISS 索引時出錯: {e}")
    embeddings = None
    faiss_index = None


# 定義回答問題的函數，加入記憶功能
def answer_question(query, top_k=500, similarity_threshold=1.1):
    image_urls = get_image_urls(query)#WWWW
    relevant_results = []  # 初始化 relevant_results 為空列表
    if faiss_index is None or embeddings is None:
        print("錯誤: 嵌入或 FAISS 索引未正確初始化。")
        return "錯誤: 嵌入或 FAISS 索引未正確初始化。", []

    try:
        # 確保 FAISS 索引對象正確
        if not isinstance(faiss_index, faiss.IndexFlatL2):
            print("錯誤: faiss_index 不是有效的 FAISS 索引對象。")
            return "錯誤: FAISS 索引對象無效。", []

        # 將查詢轉換為嵌入向量
        query_embedding = model.encode([query], convert_to_tensor=True).cpu().numpy()
        print(f"查詢向量生成成功: {query_embedding.shape}")

        # 在 FAISS 中進行檢索
        distances, indices = faiss_index.search(query_embedding, top_k)
        print(f"檢索結果 (距離): {distances[0]}")
        print(f"檢索結果 (索引): {indices[0]}")

        # 篩選相關段落，並輸出檢索到的內容
        relevant_results = []
        for i, (distance, idx) in enumerate(zip(distances[0], indices[0])):
            if distance < similarity_threshold and idx < len(passages):
                result = {"context": passages[idx], "distance": distance}
                relevant_results.append(result)
                print(f"\n檢索結果 {i+1}:")
                print(f"段落內容: {passages[idx]}")
                print(f"相關性距離: {distance}")

        # 儲存當前問題的檢索內容到記憶
        retrieved_history.append({"query": query, "results": relevant_results})

        # 整理記憶中的內容
        memory_context = ""
        for i, memory in enumerate(retrieved_history):
            memory_context += f"過去問題 {i+1}: {memory['query']}\n相關內容:\n"
            memory_context += "\n".join([res["context"] for res in memory["results"]]) + "\n\n"

        # 組合記憶與當前上下文
        if relevant_results:
            retrieved_passages = "\n".join([res["context"] for res in relevant_results])
            context = f"以下是與您的問題相關的文本內容：\n\n{retrieved_passages}\n\n" \
                      f"參考過去問題記憶：\n\n{memory_context}"
        else:
            context = f"未找到與您的問題相關的內容。\n\n參考過去問題記憶：\n\n{memory_context}"
    except Exception as e:
        print(f"FAISS 搜索過程中出錯: {e}")
        return "檢索過程中出現錯誤。", [], image_urls

        
        return reply, relevant_results, image_urls  # **回傳圖片 URL 列表**
    except Exception as e:
        print(f"呼叫 OpenAI API 時出錯: {e}")
        return "生成回答時出現錯誤。", []

# 主頁路由
@app.route('/')
def index():
    return render_template('Untitled.html')

# 處理 API 請求
@app.route('/send', methods=['POST'])
def send():
    data = request.get_json()
    if not data or 'message' not in data:
        return jsonify({"status": "error", "message": "請求資料不完整。"})

    user_message = data.get('message', '').strip()
    print(f"使用者訊息: {user_message}")
    reply, relevant_results, image_urls = answer_question(user_message)#WWW
    print (f"<INFO>送出去的訊息:{reply}")

    print(f"送出的圖片 URL 列表: {image_urls}")#debug
    return jsonify({"status": "success", "reply": reply, "image_urls": image_urls})#wwww

# 啟動應用
if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True, port=5001)
