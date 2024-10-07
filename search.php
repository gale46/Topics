<?php
// 資料庫連接設置
$servername = "localhost";
$username = "root"; // 請替換為你的使用者名稱
$password = ""; // 請替換為你的密碼
$dbname = "project"; // 請替換為你的資料庫名稱

// 創建連接
$conn = new mysqli($servername, $username, $password, $dbname);

// 檢查連接
if ($conn->connect_error) {
    die("Connection failed: " . $conn->connect_error);
}

// 查詢資料
$sql = "SELECT * FROM device_usage";
$result = $conn->query($sql);

// 檢查結果並顯示
if ($result->num_rows > 0) {
    echo "<table border='1'>
            <tr>
                <th>ID</th>
                <th>家電狀態</th>
                <th>攝影機狀態</th>
                <th>下一手音樂次數</th>
                <th>上一手音樂次數</th>
                <th>簡報下一頁次數</th>
                <th>簡報上一頁次數</th>
                <th>手指繪畫次數</th>
                <th>音量調節次數</th>
                
            </tr>";

    // 輸出每一行
    while($row = $result->fetch_assoc()) {
        echo "<tr>
                <td>{$row['id']}</td>
                <td>{$row['appliance_status']}</td>
                <td>{$row['camera_status']}</td>
                <td>{$row['next_music_gesture_count']}</td>
                <td>{$row['previous_music_gesture_count']}</td>
                <td>{$row['next_slide_gesture_count']}</td>
                <td>{$row['previous_slide_gesture_count']}</td>
                <td>{$row['drawing_gesture_count']}</td>
                <td>{$row['volume_adjustment_gesture_count']}</td>
                
              </tr>";
    }
    echo "</table>";
} else {
    echo "沒有資料可顯示";
}

$conn->close();
?>