<?php
//處理註冊資料
//成功跳回 login.php
//失敗  reg.php
// 設定資料庫連線
$host = 'localhost';
$dbname = 'project'; // 請替換成你的資料庫名稱
$user = 'root';    // 請替換成你的資料庫使用者名稱
$pass = ''; // 請替換成你的資料庫密碼

try {
    $pdo = new PDO("mysql:host=$host;dbname=$dbname", $user, $pass);
    $pdo->setAttribute(PDO::ATTR_ERRMODE, PDO::ERRMODE_EXCEPTION);
} catch (PDOException $e) {
    die("無法連線資料庫: " . $e->getMessage());
}

// 檢查表單是否送出
if ($_SERVER['REQUEST_METHOD'] === 'POST') {
    $username = $_POST['username'];
    $password = $_POST['password'];

    // 檢查是否有重複的 username
    $stmt = $pdo->prepare("SELECT COUNT(*) FROM users WHERE username = ?");
    $stmt->execute([$username]);
    $userExists = $stmt->fetchColumn();

    if ($userExists) {
        // 如果 username 已存在，跳轉回註冊頁面
        header("Location: reg.php?error=username_taken");
        exit();
    } else {
        // 加到資料庫
        $stmt = $pdo->prepare("INSERT INTO users (username, password) VALUES (?, ?)");
        $stmt->execute([$username, $password]);

        // 查詢最大 user_id
        $sql = "SELECT MAX(user_id) AS max_id FROM users";
        $result = $pdo->query($sql)->fetch(PDO::FETCH_ASSOC); // 提取查詢結果
        $maxUserId = $result['max_id']; // 提取 user_id 值

        // 插入 device_usage 表
        $stmt = $pdo->prepare("INSERT INTO device_usage (user_id) VALUES (?)");
        $stmt->execute([$maxUserId]);

        // 跳轉到 登入頁面
        header("Location: login.php");
        exit();
    }
}
?>
