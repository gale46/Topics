<!--註冊頁面會跳到register.php驗證-->
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>註冊帳號</title>
    <style>
        /* 全局樣式 */
        body {
            font-family: Arial, sans-serif;
            background-color: #1c1d26; /* 背景色深灰 */
            color: #ffffff; /* 文字顏色白色 */
            margin: 0;
            padding: 0;
        }

        h2 {
            color: #e44c65; /* 標題顏色 */
            text-align: center;
            margin-top: 20px;
        }

        /* 表單樣式 */
        form {
            width: 80%;
            max-width: 400px;
            margin: 0 auto;
            background-color: #272833; /* 深灰背景 */
            padding: 20px;
            border-radius: 8px;
            box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2);
        }

        form label {
            display: block;
            font-size: 1rem;
            margin-bottom: 8px;
            color: #ffffff;
        }

        form input[type="text"],
        form input[type="password"] {
            width: 100%;
            padding: 10px;
            margin-bottom: 20px;
            border: 1px solid rgba(255, 255, 255, 0.3);
            border-radius: 4px;
            background-color: #1c1d26;
            color: #ffffff;
            font-size: 1rem;
            box-sizing: border-box;
        }

        form input[type="text"]:focus,
        form input[type="password"]:focus {
            border-color: #e44c65;
            outline: none;
        }

        form input[type="submit"] {
            width: 100%;
            padding: 10px;
            background-color: #e44c65;
            color: #ffffff;
            border: none;
            border-radius: 4px;
            font-size: 1rem;
            cursor: pointer;
            transition: background-color 0.3s;
        }

        form input[type="submit"]:hover {
            background-color: #e76278;
        }

        /* 密碼提示樣式 */
        #password-feedback {
            display: block;
            font-size: 0.9rem;
            margin-top: -15px;
            margin-bottom: 20px;
        }

        .weak {
            color: #ff5722; /* 弱密碼顏色 */
        }

        .strong {
            color: #39c088; /* 強密碼顏色 */
        }

        /* 錯誤提示樣式 */
        .error {
            color: #ff5722; /* 錯誤訊息顏色 */
            text-align: center;
            margin-bottom: 20px;
        }

        #nav {
            text-align: center;
            margin-top: 20px;
        }

        #nav ul {
            list-style: none;
            padding: 0;
        }

        #nav ul li {
            display: inline-block;
            margin: 0 10px;
        }

        #nav ul li a {
            color: #ffffff;
            text-decoration: none;
            font-size: 1rem;
            padding: 5px 10px;
            border: 1px solid rgba(255, 255, 255, 0.3);
            border-radius: 4px;
            transition: background-color 0.3s, border-color 0.3s;
        }

        #nav ul li a:hover {
            background-color: #e44c65;
            border-color: #e44c65;
            color: #ffffff;
        }

        @media (max-width: 480px) {
            form {
                padding: 15px;
            }

            form label {
                font-size: 0.9rem;
            }

            form input[type="text"],
            form input[type="password"],
            form input[type="submit"] {
                font-size: 0.9rem;
            }

            #nav ul li a {
                font-size: 0.9rem;
                padding: 5px;
            }
        }

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