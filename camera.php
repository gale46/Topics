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