<!--註冊頁面-->
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>註冊帳號</title>
    <style>
        /* 顯示文字的顏色*/
        .error { color: red; }
        .weak { color: red; }
        .strong { color: green; }
    </style>
</head>
<body>
    <h2>註冊帳號</h2>
    
    
    <?php if (isset($_GET['error']) && $_GET['error'] == 'username_taken'): ?>
        <p class="error">這個帳號已經被使用，請選擇其他帳號。</p>
    <?php endif; ?>

    <!-- 註冊資料到 register.php 去處理-->
    <form id="register-form" action="register.php" method="POST">

        <label for="username">帳號:</label>
        <input type="text" id="username" name="username" required><br><br>

        <label for="password">密碼:</label>
        <input type="password" id="password" name="password" required><br><br>

        <!-- 密碼強度提示 -->
        <span id="password-feedback"></span><br><br>

        <input type="submit" value="註冊">
    </form>

    <script>
        /**
         * Rabin-Karp algo，檢查密碼中是否有weak string
         * text - password
         * pattern - weak string pattern
         * 轉乘Unicode
         * 256 作為radix
         */
        function rabinKarpSearch(text, pattern) {
            const prime = 101; // 一個用於哈希函數的質數，q
            const n = text.length; // 密碼的長度
            const m = pattern.length; // 弱字串的長度

            let patternHash = 0; // weak string的hash value，p
            let textHash = 0; // password當前的hash value，t_s
            let h = 1;

            // 算出 h 
            for (let i = 0; i < m - 1; i++) {
                h = (h * 256) % prime;
            }

            // prepocessing
            for (let i = 0; i < m; i++) {
                patternHash = (patternHash * 256 + pattern.charCodeAt(i)) % prime;
                textHash = (textHash * 256 + text.charCodeAt(i)) % prime;
            }

            // matching
            for (let i = 0; i <= n - m; i++) {
                // hash value相同，再做檢查
                if (patternHash === textHash) {
                    let match = true;
                    for (let j = 0; j < m; j++) {
                        if (text[i + j] !== pattern[j]) {
                            match = false;
                            break;
                        }
                    }
                    if (match) {
                        return true; // 找到弱字串
                    }
                }

                // 計算t_{s+1}
                if (i < n - m) {
                    textHash = (256 * (textHash - text.charCodeAt(i) * h) + text.charCodeAt(i + m)) % prime;
                    if (textHash < 0) textHash += prime; // 有可能會變negative
                }
            }

            return false; 
        }

        // listener
        document.getElementById('password').addEventListener('input', function() {
            const password = this.value; 
            const feedback = document.getElementById('password-feedback'); // 提示區域
            let feedbackText = ''; // 顯示密碼強弱

            // 設定weak string
            const weakStrings = ['bb', 'aa'];
            let weakStringFound = false;

            // Rabin-Karp 檢查弱字串
            for (let weakString of weakStrings) {
                if (rabinKarpSearch(password, weakString)) {
                    weakStringFound = true;
                    feedbackText = '密碼包含弱字串，請盡量避免使用';
                    feedback.className = 'weak'; // style設為weak
                    break; // 如果找到弱字串，提早退出
                }
            }

            // 如果未找到弱字串，進一步使用 Bloom Filter 檢查
            if (!weakStringFound) {
                const xhr = new XMLHttpRequest(); // AJAX 請求
                xhr.open('POST', 'bloom.php', true); // 指向 Bloom Filter 的檢查腳本
                xhr.setRequestHeader('Content-Type', 'application/x-www-form-urlencoded');
                xhr.onreadystatechange = function() {
                    if (xhr.readyState === 4 && xhr.status === 200) {
                        // 根據 Bloom Filter 的回應更
                        if (xhr.responseText === 'weak' || password.length < 6) {
                            feedbackText = feedbackText || '密碼太弱，請避免使用常見密碼';
                            feedback.className = 'weak';
                        } else {
                            feedbackText = feedbackText || '密碼強';
                            feedback.className = 'strong';
                        }
                        feedback.textContent = feedbackText; // 更新提示文字
                    }
                };
                xhr.send('password=' + encodeURIComponent(password)); // 傳送密碼給伺服端檢查
            } else {
                feedback.textContent = feedbackText; // 更新弱字串檢查提示
            }
        });
    </script>
    <nav id="nav">
                <ul>
                    <li><a href="login.php">登入</a></li>
                    <!--
                    <li><a href="search.php">使用紀錄</a></li>
                    <li><a href="camera.php">手勢偵測</a></li>
                    <li><a href="ir_operation.php">家電控制</a></li>-->
                </ul>
        </nav>
</body>
</html>