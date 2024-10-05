<!DOCTYPE HTML>
<html lang="zh-Hant">
<head>
    <title>海豹躺平</title>
    <meta charset="utf-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1, user-scalable=no" />
    <link rel="stylesheet" href="assets/css/main.css" />
    <noscript><link rel="stylesheet" href="assets/css/noscript.css" /></noscript>
</head>
<body class="is-preload landing">
    <div id="page-wrapper">
        <!-- Header -->
        <header id="header">
            <h1 id="logo">
                <a href="index.php">
                    <img width="100" src="images/sealsleeping.gif" alt="海豹躺平"/>
                </a>
            </h1>
            <nav id="nav">
                <ul>
                    <li><a href="index.php">首頁</a></li>
                    <li><a href="introduce.php">介紹</a></li>
                    <li><a href="historical_record.php">歷史紀錄</a></li>
                    <li><a href="about_me.php">關於我們</a></li>
                </ul>
            </nav>
        </header>

        <!-- Main -->
        <div id="main" class="wrapper style1">
            <div class="container">
                <header class="major">
                    <h2>手勢控制系統</h2>
                    <p>使用手勢來控制系統功能</p>
                </header>

                <!-- 手勢控制區域 -->
                <section>
                    <div class="row gtr-50 gtr-uniform">
                        <div class="gesture-detection">
                            <video id="videoElement" autoplay playsinline></video> <!-- 手勢檢測的視頻 -->
                            <canvas id="overlay"></canvas> <!-- 用於繪製檢測結果 -->
                            <div id="gestureMessages"></div> <!-- 顯示手勢消息 -->
                        </div>
                    </div>
                </section>
        <!-- Footer -->
        <footer id="footer">
            <ul class="icons">
                <!-- 你的社交媒體圖標 -->
            </ul>
            <ul class="copyright">
                <li>&copy; 2024 海豹躺平. 版權所有.</li>
            </ul>
        </footer>
    </div>

    <!-- Scripts -->
    <script src="assets/js/jquery.min.js"></script>
    <script src="assets/js/jquery.scrolly.min.js"></script>
    <script src="assets/js/jquery.dropotron.min.js"></script>
    <script src="assets/js/jquery.scrollex.min.js"></script>
    <script src="assets/js/browser.min.js"></script>
    <script src="assets/js/breakpoints.min.js"></script>
    <script src="assets/js/util.js"></script>
    <script src="assets/js/main.js"></script>

    <!-- MediaPipe Libraries -->
    <script src="https://cdn.jsdelivr.net/npm/@mediapipe/hands/hands.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/@mediapipe/camera_utils/camera_utils.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/@mediapipe/drawing_utils/drawing_utils.js"></script>

    <script src="script.js"></script> <!-- 引入自定義 JavaScript -->
</body>
</html>
