<!DOCTYPE HTML>
<html>
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
					<h1 id="logo"><a href="index.php"><img width="100" src="images/sealsleeping.gif"/></a></h1>
					<nav id="nav">
						<ul>
                        <li><a href="index.php">首頁</a></li>
							<li><a href="pictures.php">上傳作品</a></li>
							<li><a href="sign_up.php">報名比賽</a></li>
							<?php
                                session_start();
                                if (isset($_SESSION['email'])) {
                                    echo '<li><a href="logout.php" class="button primary">登出</a></li>';
                                    echo '<li><span>' . $_SESSION['email'] . ' Hello!!</span></li>';
                                } else {
                                    echo '<li><a href="login.php" class="button primary">登入</a></li>';
                                }
                                ?>
						</ul>
					</nav>
				</header>

        <!-- Main -->
        <div id="main" class="wrapper style1">
            <div class="container">
                <header class="major">
                    <h2>註冊</h2>
                </header>

                <!-- Form -->
                <section style="text-align: center;">
					<form method="post" action="register_process.php">
						<div class="row gtr-uniform gtr-50">
							<div class="col-6 col-12-xsmall">
								<input type="text" name="username" id="username" placeholder="用戶名" required />
							</div>
							<div class="col-6 col-12-xsmall">
								<input type="email" name="email" id="email" placeholder="Email" required size="30" />
							</div>
							<div class="col-6 col-12-xsmall">
								<input type="password" name="password" id="password" placeholder="密碼" required size="30" />
							</div>
							<div class="col-12">
								<ul class="actions">
									<li><input type="submit" value="註冊" class="primary" /></li>
									<li><input type="reset" value="清除" /></li>
								</ul>
							</div>
						</div>
					</form>
				</section>


            </div>
        </div>

        <!-- Footer -->
        <footer id="footer">
            <ul class="icons">
                <li><a href="#" class="icon brands alt fa-twitter"><span class="label">Twitter</span></a></li>
                <li><a href="#" class="icon brands alt fa-facebook-f"><span class="label">Facebook</span></a></li>
                <li><a href="#" class="icon brands alt fa-linkedin-in"><span class="label">LinkedIn</span></a></li>
                <li><a href="#" class="icon brands alt fa-instagram"><span class="label">Instagram</span></a></li>
                <li><a href="#" class="icon brands alt fa-github"><span class="label">GitHub</span></a></li>
                <li><a href="#" class="icon solid alt fa-envelope"><span class="label">Email</span></a></li>
            </ul>
            <ul class="copyright">
                <li>&copy; 版權被海豹吃了。</li><li>Design: <a href="https://www.youtube.com/watch?v=dD1wBSsNOL0&t=2s">SEAL</a></li>
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

</body>
</html>
