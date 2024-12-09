<?php
session_start();
if(isset($_SESSION["user_id"])){
    echo "使用者". $_SESSION["user_id"];
}

if (!isset($_SESSION['loggedin']) || $_SESSION['loggedin'] !== true){
    header("Location: login.php");
}
?>

<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Hand Gesture Capture</title>
    <style>/* 基本樣式 */
        body {
            font-family: Arial, sans-serif;
            background-color: #1c1d26; /* 深色背景 */
            color: #ffffff; /* 白色文字 */
            margin: 0;
            padding: 0;
            text-align: center;
        }

        nav {
            background-color: #272833;
            padding: 10px 0;
            box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2);
            margin-bottom: 20px;
        }

        nav ul {
            list-style: none;
            padding: 0;
            margin: 0;
            display: flex;
            justify-content: center;
            gap: 20px;
        }

        nav ul li {
            display: inline-block;
        }

        nav ul li a {
            color: #ffffff;
            text-decoration: none;
            font-size: 1rem;
            padding: 5px 15px;
            border: 1px solid rgba(255, 255, 255, 0.3);
            border-radius: 4px;
            transition: background-color 0.3s, border-color 0.3s;
        }

        nav ul li a:hover {
            background-color: #e44c65;
            border-color: #e44c65;
        }

        /* 標題樣式 */
        h1 {
            font-size: 2rem;
            margin: 20px 0;
            color: #e44c65;
        }

        /* 影像顯示區 */
        video {
            border: 5px solid #ffffff;
            border-radius: 10px;
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.5);
            margin-top: 20px;
        }

      
        @media (max-width: 768px) {
            video {
                width: 100%;
                height: auto;
            }

            nav ul li a {
                font-size: 0.8rem;
                padding: 5px 10px;
            }

            h1 {
                font-size: 1.5rem;
            }
        }
        </style>
</head>
<body>
        <nav>        
            <ul>
                <li><a href="search.php">使用紀錄</a></li>
                <li><a href="camera.php">手勢偵測</a></li>
                <li><a href="ir_operation.php">家電控制</a></li>
            </ul>
        </nav>
    <h1>Hand Gesture Capture</h1>

    <!-- 顯示影像的區域 -->
    <video id="video" width="640" height="380" autoplay></video>

    <script>
        // 初始化攝影機
        const videoElement = document.getElementById('video');

        // 開啟攝影機
        navigator.mediaDevices.getUserMedia({ video: true })
            .then(stream => {
                videoElement.srcObject = stream;
            })
            .catch(err => {
                console.error("Error accessing the camera: ", err);
            });

        // 每 100 毫秒捕獲影像並傳送
        setInterval(function() {
            // 捕捉畫面並轉換為圖片
            const canvas = document.createElement('canvas');
            canvas.width = videoElement.videoWidth;
            canvas.height = videoElement.videoHeight;
            const context = canvas.getContext('2d');
            context.drawImage(videoElement, 0, 0, canvas.width, canvas.height);

            // 取得影像的 base64 編碼
            const imageData = canvas.toDataURL('image/jpeg'); // 確保是 'image/jpeg'

            // 使用 AJAX 發送影像和 user_id 到後端
            fetch('http://localhost:8082/process_image', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    image: imageData,  // 這裡會發送完整的 Base64 編碼
                    user_id: '<?php echo $_SESSION["user_id"]; ?>'
                })
            })
            .catch(error => {
                console.error('Error:', error);
            });
        }, 500); // 每 100 毫秒捕獲並發送一次
    </script>
</body>
</html>