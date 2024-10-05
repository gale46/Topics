// script.js

// 等待頁面載入完成
window.addEventListener('DOMContentLoaded', () => {
    const videoElement = document.getElementById('videoElement');
    const canvasElement = document.getElementById('overlay');
    const canvasCtx = canvasElement.getContext('2d');
    const gestureMessages = document.getElementById('gestureMessages');

    // 設定 MediaPipe Hands
    const hands = new Hands({
        locateFile: (file) => {
            return `https://cdn.jsdelivr.net/npm/@mediapipe/hands/${file}`;
        }
    });

    hands.setOptions({
        maxNumHands: 2, // 設定最大偵測手數為2
        modelComplexity: 1,
        minDetectionConfidence: 0.7,
        minTrackingConfidence: 0.7
    });

    hands.onResults(onResults);

    // 使用 CameraUtils 來處理攝影機輸入
    const camera = new Camera(videoElement, {
        onFrame: async () => {
            await hands.send({image: videoElement});
        },
        width: 1280,
        height: 720
    });
    camera.start().then(() => {
        console.log('Camera started successfully.');
    }).catch((error) => {
        console.error('Error starting camera:', error);
    });

    // 用於儲存訊息的陣列
    const messageQueue = [];

    // 定義 addGestureMessage 函數
    function addGestureMessage(message) {
        // 檢查是否已存在相同訊息
        const existingMessage = Array.from(gestureMessages.children).find(msgDiv => msgDiv.innerText === message);
        if (existingMessage) {
            // 如果訊息已存在，重置其淡出計時器
            existingMessage.classList.remove('fadeOut');
            existingMessage.classList.add('fadeInUp'); // 重新添加淡入動畫

            // 移除現有的淡出計時器
            if (existingMessage.timerId) {
                clearTimeout(existingMessage.timerId);
            }

            // 設置新的淡出計時器
            existingMessage.timerId = setTimeout(() => {
                existingMessage.classList.add('fadeOut');
                existingMessage.addEventListener('animationend', () => {
                    existingMessage.remove();
                });
            }, 5000);

            return;
        }

        // 檢查訊息佇列長度，最多保留3條訊息
        const currentMessages = gestureMessages.querySelectorAll('.gestureMessage');
        if (currentMessages.length >= 3) {
            const oldestMessage = gestureMessages.firstChild;
            oldestMessage.classList.add('fadeOut');
            oldestMessage.addEventListener('animationend', () => {
                oldestMessage.remove();
                messageQueue.shift(); // 移除佇列中的最舊訊息
            });
        }

        // 創建新的訊息元素
        const messageDiv = document.createElement('div');
        messageDiv.classList.add('gestureMessage', 'opacity-100');
        messageDiv.innerText = message;

        // 創建標籤元素
        const labelDiv = document.createElement('div');
        labelDiv.classList.add('label');

        // 根據訊息佇列的位置分配標籤
        // 最舊的訊息標記為 "Oldest"，最新的訊息標記為 "Newest"
        if (messageQueue.length === 0) {
            labelDiv.innerText = 'Newest';
            messageDiv.classList.add('opacity-100');
        } else {
            labelDiv.innerText = 'Oldest';
            messageDiv.classList.add('opacity-80');
        }

        messageDiv.appendChild(labelDiv);
        gestureMessages.appendChild(messageDiv);

        // 添加訊息到佇列尾部
        messageQueue.push(message);

        // 設置自動淡出和移除計時器（例如，5秒後）
        messageDiv.timerId = setTimeout(() => {
            messageDiv.classList.add('fadeOut');
            messageDiv.addEventListener('animationend', () => {
                messageDiv.remove();
                const msgIndex = messageQueue.indexOf(message);
                if (msgIndex !== -1) {
                    messageQueue.splice(msgIndex, 1);
                }
            });
        }, 5000); // 5000 毫秒 = 5 秒
    }

    // 定義 onResults 函數
    function onResults(results) {
        console.log('onResults called');
        // 調整 canvas 大小
        canvasElement.width = results.image.width;
        canvasElement.height = results.image.height;

        // 清空畫布並填充黑色背景
        canvasCtx.save();
        canvasCtx.clearRect(0, 0, canvasElement.width, canvasElement.height);
        canvasCtx.fillStyle = 'black';
        canvasCtx.fillRect(0, 0, canvasElement.width, canvasElement.height);

        // 準備合併所有手的路徑
        const combinedPath = new Path2D();

        if (results.multiHandLandmarks && results.multiHandedness) {
            console.log(`Detected ${results.multiHandLandmarks.length} hands.`);
            results.multiHandLandmarks.forEach((landmarks, index) => {
                const handedness = results.multiHandedness[index].label; // 左手或右手
                console.log(`Hand ${index + 1}: ${handedness}`);

                // 創建手部遮罩路徑
                const handPath = new Path2D();
                landmarks.forEach((landmark, i) => {
                    const x = landmark.x * canvasElement.width;
                    const y = landmark.y * canvasElement.height;
                    if (i === 0) {
                        handPath.moveTo(x, y);
                    } else {
                        handPath.lineTo(x, y);
                    }
                });
                handPath.closePath();

                // 將每隻手的路徑添加到合併路徑中
                combinedPath.addPath(handPath);
            });

            // 使用合併後的路徑作為裁剪區域
            canvasCtx.clip(combinedPath);

            // 繪製攝影機影像，只顯示手部區域
            canvasCtx.drawImage(results.image, 0, 0, canvasElement.width, canvasElement.height);

            // 恢復裁剪區域
            canvasCtx.restore();

            // 再次填充黑色背景，僅保留手部區域
            canvasCtx.save();
            canvasCtx.fillStyle = 'black';
            canvasCtx.fillRect(0, 0, canvasElement.width, canvasElement.height);

            // 繪製每隻手部連接線和關鍵點，並偵測手勢
            results.multiHandLandmarks.forEach((landmarks, index) => {
                const handedness = results.multiHandedness[index].label; // 左手或右手

                // 增加抗鋸齒效果
                canvasCtx.imageSmoothingEnabled = true;
                canvasCtx.imageSmoothingQuality = 'high';

                // 繪製手部連接線和關鍵點，增加透明度和調整顏色
                drawConnectors(canvasCtx, landmarks, Hands.HAND_CONNECTIONS,
                              {color: 'rgba(0, 255, 0, 0.8)', lineWidth: 6});
                drawLandmarks(canvasCtx, landmarks, {color: 'rgba(255, 255, 255, 0.9)', lineWidth: 3, radius: 5});

                // 偵測手勢
                const gesture = detectGesture(landmarks);
                if (gesture) {
                    const message = `${handedness}: ${gesture}`;
                    console.log(`Detected gesture: ${message}`);
                    addGestureMessage(message);
                    // 根據手勢執行相應的控制，例如調整音量
                    controlVolume(gesture);
                }
            });

            canvasCtx.restore();
        } else {
            console.log('No hands detected.');
            // 如果沒有偵測到手，僅顯示黑色背景
            canvasCtx.fillStyle = 'black';
            canvasCtx.fillRect(0, 0, canvasElement.width, canvasElement.height);
        }
    }

    // 簡單的手勢偵測函數
    function detectGesture(landmarks) {
        // 根據手部關鍵點的座標來偵測具體的手勢
        // 例如，簡單判斷拇指和食指的距離來控制音量
        const thumbTip = landmarks[4];
        const indexTip = landmarks[8];
        const distance = Math.hypot(indexTip.x - thumbTip.x, indexTip.y - thumbTip.y);

        if (distance < 0.05) {
            return '音量減小';
        } else if (distance > 0.1) {
            return '音量增加';
        }
        return null; // 當前沒有特定手勢
    }

    // 控制音量的函數
    function controlVolume(action) {
        // 注意：由於瀏覽器的安全性限制，網頁無法直接控制系統音量
        // 這裡僅以網頁內的音量為例
        const audio = new Audio();
        if (action === '音量增加') {
            audio.volume = Math.min(audio.volume + 0.1, 1);
            console.log(`Audio volume increased to ${audio.volume}`);
        } else if (action === '音量減小') {
            audio.volume = Math.max(audio.volume - 0.1, 0);
            console.log(`Audio volume decreased to ${audio.volume}`);
        }
        // 您可以根據需要調整這部分的功能
    }
});
