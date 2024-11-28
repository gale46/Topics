<?php
//bloom.php
class BloomFilter {
    private $size; //就是tableSize
    private $bitArray; //table
    private $hashCount; //hash function數量

    public function __construct($size, $hashCount) {
        $this->size = $size;
        $this->bitArray = array_fill(0, $size, 0);
        $this->hashCount = $hashCount;
    }

    //hash function，使用divide method
    //crc32為string轉成int，可以任意替換
    //i+ord() 可以避免clutering的問題
    private function hash($item, $i) {
        return (crc32($item) + $i * ord($item[0])) % $this->size;
    }

    //先將弱密碼加入bit array
    public function add($item) {
        for ($i = 0; $i < $this->hashCount; $i++) {
            $this->bitArray[$this->hash($item, $i)] = 1;
        }
    }

    public function mightContain($item) {
        for ($i = 0; $i < $this->hashCount; $i++) {
            if ($this->bitArray[$this->hash($item, $i)] == 0) {
                return false;
            }
        }
        return true;
    }
}

// //埃拉托斯特尼篩法，利用process concurrency的概念
function sieve_of_Eratosthenes($n) {
    // pipe 用來傳遞數據
    $descriptorspec = [
        0 => ["pipe", "r"], // 標準輸入
        1 => ["pipe", "w"], // 標準輸出
        2 => ["pipe", "w"], // 標準錯誤輸出
    ];

    // 初始化篩選 array
    $numbers = range(2, $n); // 生成 2 到 n 的 array

    // 使用 XAMPP 的 PHP 路徑，後面要改為child.php的位置
    //用child去篩選
    $process = proc_open('C:/xampp/php/php.exe C:/Users/chu/Desktop/web/child.php', $descriptorspec, $pipes);

    if (is_resource($process)) {
        // 將當前 array 寫入pipe
        fwrite($pipes[0], json_encode($numbers));
        fclose($pipes[0]);

        // 從pipe讀取篩選結果
        $filteredNumbers = stream_get_contents($pipes[1]);
        fclose($pipes[1]);

        // 檢查進程是否有錯誤
        $error = stream_get_contents($pipes[2]);
        fclose($pipes[2]);

        proc_close($process);

        if (!empty($error)) {
            die("Error from child process: $error");
        }

        // 解碼篩選後的array
        $primes = json_decode($filteredNumbers, true);
        if (json_last_error() !== JSON_ERROR_NONE) {
            die("Failed to decode JSON: " . json_last_error_msg());
        }

        // 計算 n/2 並找到第一個大於 n/2 的質數
        $half_n = $n / 2;
        foreach ($primes as $prime) {
            if ($prime > $half_n) {
                return $prime; // 返回第一個大於 n/2 的質數
            }
        }
    } else {
        die("Failed to create child process");
    }

    return $half_n; // 如果沒有找到，返回 null
}


//先找出key的數量，預設有7個
$keyNum = 7;


// 建立資料庫連接
$servername = "localhost";
$username = "root";
$password = "1234";
$dbname = "kkbox"; 

$conn = new mysqli($servername, $username, $password, $dbname);

// 檢查連接是否成功
if ($conn->connect_error) {
    die("Connection failed: " . $conn->connect_error);
}

// 查詢最大 user_id
$sql = "SELECT MAX(user_id) AS max_id FROM users";
$result = $conn->query($sql);

// 檢查結果
if ($result && $result->num_rows > 0) {
    // 輸出最大 ID
    $row = $result->fetch_assoc();
    $keyNum = $row['max_id'];
}

// 查詢資料庫中的所有密碼
$sql = "SELECT password FROM users"; 
$result = $conn->query($sql);

// 存放user的password
$databasePasswords = [];

// 檢查查詢是否有結果
if ($result && $result->num_rows > 0) {
    // 逐行取出密碼並加入陣列
    while($row = $result->fetch_assoc()) {
        if (!empty($row['password'])) {
            // 將每個密碼加入陣列中
            $databasePasswords[] = trim($row['password']); // 確保去除空白
        }
    }
}

// 關閉資料庫連接
$conn->close();

// 預設弱密碼列表
$weakPasswords = ['123456', 'password', 'qwerty', 'abc123', '111111', 'letmein', '123123'];
//合併兩個array，作為所有弱密碼，加到table中
$allweakPasswords = array_merge($weakPasswords, $databasePasswords);

//n為item數量
$n = count($allweakPasswords);

//希望false-positive 1%
//但因為hash function使用division method，所以table size最好為質數
//取一個比10 * keyNum還大的質數，根據哥德巴赫猜想，一個數與他的兩倍之間必有質數
//以下都是依照公式計算
$tableSize = intval(sieve_of_Eratosthenes(2 * (1 + ceil(($n * log(0.01)) / log(1 / pow(2, log(2)))))));

//hash function的數量
$hashCount = intval(round(($tableSize / $n) * log(2)));


//創建bloomfilter table，並將弱密碼加到table中
$bloomFilter = new BloomFilter($tableSize, $hashCount);
foreach ($allweakPasswords as $weakPassword) {
    $bloomFilter->add($weakPassword);
}


// 即時檢查密碼是否為弱密碼
if (isset($_POST['password'])) {
    $password = $_POST['password'];

    if ($bloomFilter->mightContain($password)) {
        echo 'weak';
    } else {
        echo 'strong';
    }
}
?>