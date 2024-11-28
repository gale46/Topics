-- phpMyAdmin SQL Dump
-- version 5.2.1
-- https://www.phpmyadmin.net/
--
-- 主機： 127.0.0.1
-- 產生時間： 2024-11-28 08:02:24
-- 伺服器版本： 10.4.32-MariaDB
-- PHP 版本： 8.2.12
CREATE DATABASE IF NOT EXISTS project;
USE project;
SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
START TRANSACTION;
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

--
-- 資料庫： `project`
--

DELIMITER $$
--
-- 程序
--
CREATE DEFINER=`root`@`localhost` PROCEDURE `GenerateUserActivity` ()   BEGIN
    DECLARE done INT DEFAULT FALSE;
    DECLARE v_user_id INT;
    DECLARE activity VARCHAR(255);
    DECLARE activity_time DATETIME;
    DECLARE start_date DATETIME DEFAULT '2024-11-18 00:00:00';
    DECLARE end_date DATETIME DEFAULT '2024-11-24 23:59:59';
    
    -- 確保只選擇實際存在的 user_id
    DECLARE user_cursor CURSOR FOR 
        SELECT user_id 
        FROM users 
        WHERE user_id IS NOT NULL;
        
    DECLARE CONTINUE HANDLER FOR NOT FOUND SET done = TRUE;

    -- 開始生成數據
    OPEN user_cursor;
    
    read_loop: LOOP
        FETCH user_cursor INTO v_user_id;
        
        IF done THEN
            LEAVE read_loop;
        END IF;

        SET @i = FLOOR(RAND() * (10)) + 5; -- 隨機生成5到15個活動
        
        WHILE @i > 0 DO
            SET activity = ELT(FLOOR(RAND() * 10) + 1,
                'appliance_change',
                'drawing_gesture_count',
                'volume_increase_gesture_count',
                'volume_decrease_gesture_count',
                'next_music_gesture_count',
                'previous_music_gesture_count',
                'scroll_up_gesture_count',
                'scroll_down_gesture_count',
                'next_slide_gesture_count',
                'previous_slide_gesture_count'
            );

            SET activity_time = start_date + INTERVAL FLOOR(RAND() * TIMESTAMPDIFF(SECOND, start_date, end_date)) SECOND;

            INSERT INTO user_activity (user_id, activity, activity_time)
            VALUES (v_user_id, activity, activity_time);
            
            SET @i = @i - 1;
        END WHILE;
    END LOOP;
    
    CLOSE user_cursor;
END$$

DELIMITER ;

-- --------------------------------------------------------

--
-- 資料表結構 `device_usage`
--

CREATE TABLE `device_usage` (
  `user_id` int(11) NOT NULL,
  `appliance_change` int(11) NOT NULL DEFAULT 0,
  `drawing_gesture_count` int(11) NOT NULL DEFAULT 0,
  `volume_gesture_count` int(11) NOT NULL DEFAULT 0,
  `music_gesture_count` int(11) NOT NULL DEFAULT 0,
  `scroll_gesture_count` int(11) NOT NULL DEFAULT 0,
  `slide_gesture_count` int(11) NOT NULL DEFAULT 0,
  `mouse_gesture_count` int(11) NOT NULL DEFAULT 0,
  `keyboard_gesture_count` int(11) NOT NULL DEFAULT 0,
  `household_gesture_count` int(11) NOT NULL DEFAULT 0
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- 傾印資料表的資料 `device_usage`
--

INSERT INTO `device_usage` (`user_id`, `appliance_change`, `drawing_gesture_count`, `volume_gesture_count`, `music_gesture_count`, `scroll_gesture_count`, `slide_gesture_count`, `mouse_gesture_count`, `keyboard_gesture_count`, `household_gesture_count`) VALUES
(1, 7, 3, 12, 7, 10, 9, 0, 13, 10),
(2, 0, 0, 0, 0, 0, 0, 0, 0, 0),
(3, 0, 0, 0, 0, 0, 0, 0, 0, 0),
(4, 0, 0, 0, 0, 0, 0, 0, 0, 0),
(5, 0, 0, 0, 0, 0, 0, 0, 0, 0);

-- --------------------------------------------------------

--
-- 資料表結構 `ir_codes`
--

CREATE TABLE `ir_codes` (
  `ir_code_id` int(11) NOT NULL,
  `address` varchar(5) NOT NULL,
  `ir_code_name` varchar(10) NOT NULL,
  `command` varchar(5) DEFAULT NULL,
  `user_id` int(11) NOT NULL,
  `gesture` int(1) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- 傾印資料表的資料 `ir_codes`
--

INSERT INTO `ir_codes` (`ir_code_id`, `address`, `ir_code_name`, `command`, `user_id`, `gesture`) VALUES
(2, '48', '開關', '136', 1, 1),
(3, '48', '擺頭', '133', 1, 2);

-- --------------------------------------------------------

--
-- 資料表結構 `users`
--

CREATE TABLE `users` (
  `user_id` int(11) NOT NULL,
  `username` varchar(50) NOT NULL,
  `password` varchar(255) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- 傾印資料表的資料 `users`
--

INSERT INTO `users` (`user_id`, `username`, `password`) VALUES
(1, 'user1', '1234'),
(2, 'user2', '1234'),
(3, 'user3', '1234'),
(4, 'user4', '1234'),
(5, 'user5', '1234'),
(10, 'user6', '1234'),
(11, 'user7', '1234'),
(12, 'user8', '1234'),
(13, 'user9', '1234'),
(14, 'user99', '1234');

-- --------------------------------------------------------

--
-- 資料表結構 `user_activity`
--

CREATE TABLE `user_activity` (
  `user_id` int(11) NOT NULL,
  `activity` varchar(255) NOT NULL,
  `activity_time` datetime NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- 傾印資料表的資料 `user_activity`
--

INSERT INTO `user_activity` (`user_id`, `activity`, `activity_time`) VALUES
(1, 'scroll_gesture_count', '2024-11-28 14:30:27'),
(1, 'scroll_gesture_count', '2024-11-28 14:30:28'),
(1, 'scroll_gesture_count', '2024-11-28 14:31:42'),
(1, 'scroll_gesture_count', '2024-11-28 14:31:43'),
(1, 'appliance_change', '2024-11-28 14:32:01'),
(1, 'appliance_change', '2024-11-28 14:32:02'),
(1, 'scroll_gesture_count', '2024-11-28 14:34:03'),
(1, 'scroll_gesture_count', '2024-11-28 14:34:04'),
(1, 'appliance_change', '2024-11-28 14:34:09'),
(1, 'appliance_change', '2024-11-28 14:34:10'),
(1, 'scroll_gesture_count', '2024-11-28 14:34:15'),
(1, 'scroll_gesture_count', '2024-11-28 14:34:16'),
(1, 'drawing_gesture_count', '2024-11-28 14:34:40'),
(1, 'slide_gesture_count', '2024-11-28 14:42:17'),
(1, 'slide_gesture_count', '2024-11-28 14:42:18'),
(1, 'slide_gesture_count', '2024-11-28 14:42:21'),
(1, 'slide_gesture_count', '2024-11-28 14:42:22'),
(1, 'slide_gesture_count', '2024-11-28 14:42:23'),
(1, 'slide_gesture_count', '2024-11-28 14:42:29'),
(1, 'slide_gesture_count', '2024-11-28 14:42:30'),
(1, 'slide_gesture_count', '2024-11-28 14:43:10'),
(1, 'appliance_change', '2024-11-28 14:43:54'),
(1, 'appliance_change', '2024-11-28 14:44:10'),
(1, 'music_gesture_count', '2024-11-28 14:44:35'),
(1, 'music_gesture_count', '2024-11-28 14:44:55'),
(1, 'scroll_gesture_count', '2024-11-28 14:45:12'),
(1, 'music_gesture_count', '2024-11-28 14:46:50'),
(1, 'scroll_gesture_count', '2024-11-28 14:46:51'),
(1, 'keyboard_gesture_count', '2024-11-28 14:47:25'),
(1, 'keyboard_gesture_count', '2024-11-28 14:47:26'),
(1, 'keyboard_gesture_count', '2024-11-28 14:47:27'),
(1, 'scroll_gesture_count', '2024-11-28 14:47:28'),
(1, 'scroll_gesture_count', '2024-11-28 14:47:29'),
(1, 'keyboard_gesture_count', '2024-11-28 14:47:30'),
(1, 'keyboard_gesture_count', '2024-11-28 14:47:31'),
(1, 'keyboard_gesture_count', '2024-11-28 14:47:32'),
(1, 'keyboard_gesture_count', '2024-11-28 14:47:33'),
(1, 'keyboard_gesture_count', '2024-11-28 14:47:34'),
(1, 'keyboard_gesture_count', '2024-11-28 14:47:35'),
(1, 'keyboard_gesture_count', '2024-11-28 14:47:36'),
(1, 'keyboard_gesture_count', '2024-11-28 14:47:37'),
(1, 'keyboard_gesture_count', '2024-11-28 14:47:38'),
(1, 'music_gesture_count', '2024-11-28 14:48:34'),
(1, 'volume_gesture_count', '2024-11-28 14:48:35'),
(1, 'music_gesture_count', '2024-11-28 14:48:36'),
(1, 'volume_gesture_count', '2024-11-28 14:48:41'),
(1, 'volume_gesture_count', '2024-11-28 14:48:46'),
(1, 'volume_gesture_count', '2024-11-28 14:48:47'),
(1, 'volume_gesture_count', '2024-11-28 14:48:48'),
(1, 'volume_gesture_count', '2024-11-28 14:48:49'),
(1, 'volume_gesture_count', '2024-11-28 14:48:50'),
(1, 'volume_gesture_count', '2024-11-28 14:48:51'),
(1, 'volume_gesture_count', '2024-11-28 14:48:52'),
(1, 'volume_gesture_count', '2024-11-28 14:48:53'),
(1, 'appliance_change', '2024-11-28 14:49:23'),
(1, 'volume_gesture_count', '2024-11-28 14:49:24'),
(1, 'keyboard_gesture_count', '2024-11-28 14:49:25'),
(1, 'household ', '2024-11-28 14:59:35'),
(1, 'slide_gesture_count', '2024-11-28 14:59:40'),
(1, 'music_gesture_count', '2024-11-28 14:59:44'),
(1, 'household ', '2024-11-28 14:59:45'),
(1, 'household ', '2024-11-28 14:59:50'),
(1, 'household ', '2024-11-28 14:59:57'),
(1, 'household ', '2024-11-28 15:00:19'),
(1, 'household ', '2024-11-28 15:00:22'),
(1, 'household ', '2024-11-28 15:00:35'),
(1, 'household ', '2024-11-28 15:00:38'),
(1, 'household ', '2024-11-28 15:00:41'),
(1, 'household ', '2024-11-28 15:01:22'),
(1, 'drawing_gesture_count', '2024-11-28 15:01:25'),
(1, 'music_gesture_count', '2024-11-28 15:01:26'),
(1, 'drawing_gesture_count', '2024-11-28 15:01:28'),
(1, 'volume_gesture_count', '2024-11-28 15:01:29');

--
-- 已傾印資料表的索引
--

--
-- 資料表索引 `device_usage`
--
ALTER TABLE `device_usage`
  ADD PRIMARY KEY (`user_id`),
  ADD KEY `user_id` (`user_id`);

--
-- 資料表索引 `ir_codes`
--
ALTER TABLE `ir_codes`
  ADD PRIMARY KEY (`ir_code_id`),
  ADD KEY `user_id` (`user_id`);

--
-- 資料表索引 `users`
--
ALTER TABLE `users`
  ADD PRIMARY KEY (`user_id`),
  ADD UNIQUE KEY `username` (`username`);

--
-- 資料表索引 `user_activity`
--
ALTER TABLE `user_activity`
  ADD PRIMARY KEY (`user_id`,`activity_time`);

--
-- 在傾印的資料表使用自動遞增(AUTO_INCREMENT)
--

--
-- 使用資料表自動遞增(AUTO_INCREMENT) `device_usage`
--
ALTER TABLE `device_usage`
  MODIFY `user_id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=6;

--
-- 使用資料表自動遞增(AUTO_INCREMENT) `ir_codes`
--
ALTER TABLE `ir_codes`
  MODIFY `ir_code_id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=4;

--
-- 使用資料表自動遞增(AUTO_INCREMENT) `users`
--
ALTER TABLE `users`
  MODIFY `user_id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=15;

--
-- 使用資料表自動遞增(AUTO_INCREMENT) `user_activity`
--
ALTER TABLE `user_activity`
  MODIFY `user_id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=2;

--
-- 已傾印資料表的限制式
--

--
-- 資料表的限制式 `device_usage`
--
ALTER TABLE `device_usage`
  ADD CONSTRAINT `device_usage_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `users` (`user_id`) ON DELETE CASCADE ON UPDATE CASCADE;

--
-- 資料表的限制式 `ir_codes`
--
ALTER TABLE `ir_codes`
  ADD CONSTRAINT `ir_codes_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `users` (`user_id`);

--
-- 資料表的限制式 `user_activity`
--
ALTER TABLE `user_activity`
  ADD CONSTRAINT `user_activity_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `users` (`user_id`);
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
