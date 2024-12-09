<?php
// child.php
//每個process代表一個prime篩選

// 從標準輸入讀取
$input = json_decode(file_get_contents('php://stdin'), true);

if (!is_array($input) || empty($input)) {
    // 若array為空，回傳empty array，不再向下遞迴
    echo json_encode([]);
    exit(0);
}

// 因為比input[0]小的數都沒辦法篩掉，所以它本身就是prime
$prime = $input[0];

// 過濾掉該prime的倍數
$filteredNumbers = array_filter($input, function($n) use ($prime) {
    return $n % $prime !== 0;
});

// 篩選後的array，傳給child，向下遞迴
$nextPrimes = [];
if (!empty($filteredNumbers)) {
    $descriptorspec = [
        0 => ["pipe", "r"], // 標準輸入
        1 => ["pipe", "w"], // 標準輸出
        2 => ["pipe", "w"], // 標準錯誤
    ];

    //下面跟parent差不多
    $process = proc_open('C:/xampp/php/php.exe C:/Users/chu/Desktop/web/child.php', $descriptorspec, $pipes);

    if (is_resource($process)) {

        fwrite($pipes[0], json_encode(array_values($filteredNumbers)));
        fclose($pipes[0]);


        $result = stream_get_contents($pipes[1]);
        fclose($pipes[1]);


        $error = stream_get_contents($pipes[2]);
        fclose($pipes[2]);

        proc_close($process);

        if (!empty($error)) {
            echo json_encode(['error' => 'Child process error']);
            exit(1);
        }

        $nextPrimes = json_decode($result, true);
        if (json_last_error() !== JSON_ERROR_NONE) {
            echo json_encode(['error' => 'Failed to decode JSON']);
            exit(1);
        }
    }
}

// 加入這個process的prime並回傳
array_unshift($nextPrimes, $prime); // 加到head可以不用再做sort
echo json_encode($nextPrimes);
exit(0);

?>
