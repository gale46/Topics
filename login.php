
<?php
//登入頁面 -> search.php

// 開啟會話以便存取會話變數
session_start();

// 資料庫連接設定
$servername = "localhost"; // 資料庫伺服器名稱或 IP
$username = "root"; // 替換為你的資料庫用戶名
$password = ""; // 替換為你的資料庫密碼
$dbname = "project"; // 替換為你的資料庫名稱

// 創建資料庫連接
$conn = new mysqli($servername, $username, $password, $dbname);

// 檢查資料庫連接是否成功
if ($conn->connect_error) {
    die("連接失敗: " . $conn->connect_error); // 輸出錯誤信息並終止腳本
}

// 登入邏輯
if ($_SERVER['REQUEST_METHOD'] == 'POST') {
    // 獲取用戶提交的用戶名和密碼
    $username = $_POST['username'];
    $password = $_POST['password'];

    // 準備 SQL 語句以查詢用戶的密碼
    $stmt = $conn->prepare("SELECT * FROM users WHERE username = ?");
    $stmt->bind_param("s", $username); // 將用戶名綁定到 SQL 語句
    $stmt->execute(); // 執行查詢
    $result = $stmt->get_result(); // 儲存查詢結果，以便檢查用戶是否存在
    $row = $result->fetch_assoc();
    $stored_password = $row["password"];
    $stored_id = $row["user_id"];

    // 檢查用戶是否存在

    if ($password == $stored_password) {
        // 如果密碼正確，設置會話變數以標記用戶已登入
        $_SESSION['loggedin'] = true;
        $_SESSION['username'] = $username; // 儲存用戶名以便顯示
        $_SESSION['user_id'] = $stored_id;
        header("Location: search.php"); // 登入成功後跳轉頁面
        exit; // 終止當前腳本以防止後續代碼執行
    } else {
        $error = "密碼錯誤，或用戶不存在"; // 密碼不正確
        
    }
    
    $stmt->close(); // 關閉語句
}

// // 登出邏輯
// if (isset($_GET['logout'])) {
//     session_unset(); // 清除所有會話變數
//     session_destroy(); // 銷毀會話
//     header("Location: index.php"); // 返回登入頁面
//     exit; // 終止當前腳本
// }


    ?>
    <!DOCTYPE html>
    <html>
    <head>
        <title>登入</title>
    </head>
    <style>
        /* 全局樣式 */
        body {
            font-family: Arial, sans-serif;
            background-color: #1c1d26; /* 深灰背景色 */
            color: #ffffff; /* 白色文字 */
            margin: 0;
            padding: 0;
            display: flex;
            flex-direction: column;
            align-items: center;
        }

        /* 標題 */
        h1, h2, h3 {
            color: #e44c65; /* 紅色點綴 */
        }

        /* 表單樣式 */
        form {
            background-color: #272833; /* 深灰背景 */
            padding: 20px;
            border-radius: 8px;
            box-shadow: 0 4px 8px rgba(0, 0, 0, 0.3);
            width: 300px;
            display: flex;
            flex-direction: column;
            gap: 15px;
        }

        form label {
            font-size: 1rem;
            margin-bottom: 5px;
        }

        form input[type="text"], 
        form input[type="password"] {
            padding: 10px;
            border: none;
            border-radius: 5px;
            width: calc(100% - 20px);
        }

        form input[type="submit"] {
            padding: 10px;
            border: none;
            border-radius: 5px;
            background-color: #e44c65;
            color: #ffffff;
            font-weight: bold;
            cursor: pointer;
            transition: background-color 0.3s;
        }

        form input[type="submit"]:hover {
            background-color: #c4374f;
        }

        /* 錯誤提示文字 */
        form p {
            color: #e44c65;
            font-size: 0.9rem;
            margin: 0;
        }

        nav {
            margin-top: 20px;
            background-color: #272833;
            padding: 10px 0;
            width: 100%;
            text-align: center;
            box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2);
        }

        nav ul {
            list-style: none;
            padding: 0;
            margin: 0;
            display: flex;
            justify-content: center;
            gap: 15px;
        }

        nav ul li {
            display: inline-block;
        }

        nav ul li a {
            color: #ffffff;
            text-decoration: none;
            font-size: 1rem;
            padding: 5px 10px;
            border: 1px solid rgba(255, 255, 255, 0.3);
            border-radius: 4px;
            transition: background-color 0.3s, border-color 0.3s;
        }

        nav ul li a:hover {
            background-color: #e44c65;
            border-color: #e44c65;
        }

       
        @media (max-width: 480px) {
            form {
                width: 90%;
            }

            nav ul li a {
                font-size: 0.8rem;
            }
        }

    </style>
    <body>
        <form method="POST" action="">
            <label for="username">用戶名:</label>
            <input type="text" id="username" name="username" required> <!-- 用戶名輸入框 -->
            <br>
            <label for="password">密碼:</label>
            <input type="password" id="password" name="password" required> <!-- 密碼輸入框 -->
            <br>
            <input type="submit" value="登入"> <!-- 登入按鈕 -->
        </form>
        <?php if (isset($error)) echo "<p>$error</p>"; ?> <!-- 顯示錯誤信息（如果有） -->
        <nav id="nav">
                <ul>
                    <li><a href="reg.php">註冊</a></li>
                    <!--
                    <li><a href="search.php">使用紀錄</a></li>
                    <li><a href="camera.php">手勢偵測</a></li>
                    <li><a href="ir_operation.php">家電控制</a></li>-->
                </ul>
        </nav>
    </body>
    </html>



<?php
// 關閉資料庫連接
$conn->close();
?>

<!-- 
    沒登入法參訪
    if (!isset($_SESSION['loggedin']) || $_SESSION['loggedin'] !== true){
        header("Location: index.php")
    }

-->