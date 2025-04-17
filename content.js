(function() {
    // **防止重複添加小工具**
    if (document.getElementById("floating-widget")) return;

    //將滾輪自動滾到底部
    function scrollChatToBottom() {
        const chatContainer = document.getElementById("chat-container");
        chatContainer.scrollTop = chatContainer.scrollHeight;
    }

    // **建立小工具主容器**
    let widget = document.createElement("div");
    widget.id = "floating-widget";
    let imageUrl = chrome.runtime.getURL("Button.png");    

    // **設定小工具的 HTML 結構**+刷新📸
    widget.innerHTML = `
    <div id="floating-widget-inner">
        <div id="widget-button">
            <img src="${imageUrl}" alt="AI助手" id="widget-icon">
        </div>

        <div id="widget-content" style="display: none;">
            <!-- 頂部標題欄 -->
            <div class="widget-header">
                <div class="widget-title">AI 小助手</div>
                <div style="margin-left:auto; padding-right:10px;">
                    <button id="wwwwwwwwwww" title="搜尋畫面">📸</button>
                    <button id="refresh-button" title="清除對話">🔄</button>
                    <button id="search-keyword-btn" title="搜尋訊息">🔎</button>
                    <button id="increase-font" title="放大字體">A+</button>
                    <button id="decrease-font" title="縮小字體">A-</button>
                    <!-- 更多按鈕 -->
                </div>
            </div>

            <div id="chat-container"></div>

            <div id="input-container">
                <textarea id="userInput" placeholder="輸入問題..."></textarea>
                <button id="sendBtn">⫸</button>
            </div>
        </div>
    </div>
`;
    document.body.appendChild(widget);

    // 歡迎訊息
    window.addEventListener("load", function() {
        // 檢查 LocalStorage 中是否已顯示過歡迎訊息
        //if (!localStorage.getItem("welcomeMessageShown")) {
            const chatContainer = document.getElementById("chat-container");
            const welcomeMessage = document.createElement("div");
            welcomeMessage.classList.add("welcome-message");
            welcomeMessage.innerHTML = "您好！歡迎使用AI小助手。請在輸入框輸入問題<br>提示:可以拖曳小助手的位置<br>雙擊按鈕可返回預設位置";
            chatContainer.appendChild(welcomeMessage);
            // 設置歡迎訊息顯示過的標誌
            localStorage.setItem("welcomeMessageShown", "true");

            // 設定歡迎訊息顯示一段時間後消失（可選）
            setTimeout(() => {
                welcomeMessage.style.display = "none"; // 隱藏歡迎訊息
            }, 8000); 
        //}
    });

    // **實現拖曳功能**
    let isDragging = false, offsetX, offsetY;
    const widgetButton = document.getElementById("widget-button");

    widgetButton.addEventListener("mousedown", function(e) {
        isDragging = true;
        offsetX = e.clientX - widget.offsetLeft;
        offsetY = e.clientY - widget.offsetTop;
        widget.style.position = "absolute";

        //雙擊回到預設位子
        document.getElementById("widget-icon").addEventListener("dblclick", () => {
            widget.style.position = "fixed"; // 恢復預設的固定位置
            widget.style.right = "30px";
            widget.style.bottom = "16px";
            widget.style.left = "";  // 清除之前拖曳留下的 left/top
            widget.style.top = "";
        });
    });

    window.addEventListener("mousemove", function(e) {
        if (isDragging) {
            let newX = e.clientX - offsetX;
            let newY = e.clientY - offsetY;
            widget.style.left = newX + "px";
            widget.style.top = newY + "px";
        }
    });

    window.addEventListener("mouseup", function() {
        isDragging = false;
    });

    // **點擊按鈕切換小工具顯示/隱藏 + 同步刷新按鈕狀態**
    const refreshButton = document.getElementById("refresh-button");
    const chatContainer = document.getElementById("chat-container");

    // **點擊主按鈕切換對話框顯示**
    widgetButton.addEventListener("click", () => {
        const content = document.getElementById("widget-content");
        const isVisible = content.style.display === "block";
        
        if (isVisible) {
            content.style.display = "none";
        } else {
            content.style.display = "block";

            content.style.height = "450px";  
            content.style.width = "360px"; 
        }
    });

    //  點擊刷新只清空內容，不關閉視窗
    refreshButton.addEventListener('click', () => {
        chatContainer.innerHTML = '';
        const inputBox = document.getElementById("userInput");
        if (inputBox) inputBox.value = '';

        const initMessage = document.createElement('div');
        initMessage.className = 'chat-bubble system-bubble';
        initMessage.textContent = '已清除所有對話，請重新提問！';
        chatContainer.appendChild(initMessage);
    });

    //按鈕切換字體
    let currentFontSize = 16; // 預設氣泡字體大小

    document.getElementById("increase-font").addEventListener("click", () => {
        if (currentFontSize < 30) {
            currentFontSize += 2;
            updateBubbleFontSize();
        }
    });

    document.getElementById("decrease-font").addEventListener("click", () => {
        if (currentFontSize > 12) {
            currentFontSize -= 2;
            updateBubbleFontSize();
        }
    });

    function updateBubbleFontSize() {
        const bubbles = document.querySelectorAll(".chat-bubble");
        bubbles.forEach(bubble => {
            bubble.style.fontSize = `${currentFontSize}px`;
        });
    }

    //搜尋功能
    document.getElementById("search-keyword-btn").addEventListener("click", () => {
        let keyword = prompt("請輸入要搜尋的關鍵字：");
        if (!keyword) return;
    
        let chatContainer = document.getElementById("chat-container");
        let bubbles = chatContainer.querySelectorAll(".chat-bubble");
    
        // 移除舊的高亮
        bubbles.forEach(bubble => {
            bubble.innerHTML = bubble.innerHTML.replace(/<span class="highlight">(.*?)<\/span>/g, "$1");
        });
    
        // 高亮新的關鍵字
        let regex = new RegExp(`(${keyword})`, "gi");
        bubbles.forEach(bubble => {
            bubble.innerHTML = bubble.innerHTML.replace(regex, `<span class="highlight">$1</span>`);
        });
    });
    
    // **允許 Enter 鍵發送訊息**
    document.getElementById("userInput").addEventListener("keypress", function(event) {
        if (event.key === "Enter") {
            event.preventDefault();
            document.getElementById("sendBtn").click();
        }
    });

    // **發送訊息並處理回應**
    document.getElementById("sendBtn").addEventListener("click", async () => {
        let userMessage = document.getElementById("userInput").value.trim();
        if (!userMessage) {
            alert("請輸入問題！");
            return;
        }

        // **顯示用戶訊息**
        let chatContainer = document.getElementById("chat-container");
        let userBubble = `<div class='chat-bubble user-bubble'>${userMessage}</div>`;
        chatContainer.innerHTML += userBubble;
        document.getElementById("userInput").value = "";
        scrollChatToBottom(); // 自動捲底

        try {
            // **發送請求到後端**
            let response = await fetch("http://127.0.0.1:5001/send", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ message: userMessage })
            });
            let data = await response.json();

            // **處理文字回應**
            let formattedReply = data.reply
                .replace(/\n/g, "<br>")   // 確保換行正確顯示
                .replace(/(\d+)\.\s/g, "<br><strong>$1.</strong> "); // 強調數字

            chatContainer.innerHTML += `<div class='chat-bubble ai-bubble'><strong>A：</strong> ${formattedReply}</div>`;
            scrollChatToBottom();

            // **處理多張圖片**
            if (data.image_urls && Array.isArray(data.image_urls)) {
                data.image_urls.forEach(imgUrl => {
                    let imgElement = document.createElement("img");
                    imgElement.src = imgUrl;
                    imgElement.classList.add("response-image");
                    imgElement.style.maxWidth = "100%";
                    imgElement.style.display = "block";
                    imgElement.style.marginTop = "10px";
                    imgElement.style.cursor = "pointer";

                    chatContainer.appendChild(imgElement);
                });
            }
        } catch (error) {
            console.error("錯誤:", error);
            chatContainer.innerHTML += "<div class='chat-bubble error-bubble'>無法連接到伺服器</div>";
        }
    });

    // **圖片放大功能：事件委派，支援所有 response-image 圖片**
    document.addEventListener("click", function (event) {
        if (event.target.classList.contains("response-image")) {
            const imgUrl = event.target.src;

            let overlay = document.createElement("div");
            overlay.className = "fullscreen-image";
            overlay.innerHTML = `
                <div class="overlay-content">
                    <img src="${imgUrl}" class="full-size-image">
                </div>
            `;
            document.body.appendChild(overlay);

            overlay.addEventListener("click", function (e) {
                if (e.target === overlay || e.target.classList.contains('full-size-image')) {
                    document.body.removeChild(overlay);
                }
            });
        }
    });

})();
