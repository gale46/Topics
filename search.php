<?php
//登入後第一個跳轉的頁面
//查看user的使用紀錄
?>
<!DOCTYPE html>
    <html>
    <head>
        <title>登入</title>
    </head>
    <body>
        <nav>        
                <ul>
                    <li><a href="search.php">使用紀錄</a></li>
                    <li><a href="camera.php">手勢偵測</a></li>
                    <li><a href="ir_operation.php">家電控制</a></li>
                </ul>
        </nav>
    </body>
    </html>

<?php


session_start();
if(isset($_SESSION["user_id"])){
    echo "使用者". $_SESSION["user_id"];
}

// 資料庫連接設置
$servername = "localhost";
$username = "root"; // 請替換為你的使用者名稱
$password = ""; // 請替換為你的密碼
$dbname = "project"; // 請替換為你的資料庫名稱

if (!isset($_SESSION['loggedin']) || $_SESSION['loggedin'] !== true){
    header("Location: login.php");
}
// 創建連接
$conn = new mysqli($servername, $username, $password, $dbname);

// 檢查連接
if ($conn->connect_error) {
    die("Connection failed: " . $conn->connect_error);
}

// 查詢資料
$user_id = $_SESSION["user_id"];
$user_id = $conn->real_escape_string($user_id);
$sql = "SELECT * FROM device_usage WHERE user_id='$user_id'";//查次數
$time = "SELECT * FROM user_activity WHERE user_id='$user_id'";//查時間
$result = $conn->query($sql);
$activity = $conn->query($time);

// 檢查結果並顯示
if ($result->num_rows > 0) {
    echo "<table border='1'>
            <tr>
                <th>ID</th>
                <th>切換頁面</th>
                <th>滑鼠滾輪</th>
                <th>音樂控制</th>
                <th>投影片控制</th>
                <th>畫圖</th>
                <th>音量控制</th>
                <th>滑鼠功能</th>
                <th>鍵盤功能</th>
                <th>家電控制</th>
            </tr>";

    // 輸出每一行
    while($row = $result->fetch_assoc()) {
        echo "<tr>
                <td>{$row['user_id']}</td>
                <td>{$row['appliance_change']}</td>
                <td>{$row['scroll_gesture_count']}</td>
                <td>{$row['music_gesture_count']}</td>
                <td>{$row['slide_gesture_count']}</td>
                <td>{$row['drawing_gesture_count']}</td>
                <td>{$row['volume_gesture_count']}</td>
                <td>{$row['mouse_gesture_count']}</td>
                <td>{$row['keyboard_gesture_count']}</td>
                <td>{$row['household_gesture_count']}</td>
                
              </tr>";
    }
    echo "</table>";
} else {
    echo "沒有資料可顯示";
}

if ($activity->num_rows > 0) {
    echo "<table border='1'>
            <tr>
                <th>操作</th>
                <th>使用時間</th>
            </tr>";

    // 輸出每一行
    while($row = $activity->fetch_assoc()) {
        echo "<tr>
                <td>{$row['activity']}</td>
                <td>{$row['activity_time']}</td>
              </tr>";
    }
    echo "</table>";
} else {
    echo "沒有資料可顯示";
}
$conn->close();
?>