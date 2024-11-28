import cv2
import mediapipe as mp
import pyautogui
from datetime import datetime
import math
import numpy as np
from time import sleep
from pynput.keyboard import Controller
import time
import pymysql
import serial
import time
from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
from datetime import datetime

app = Flask(__name__)
CORS(app)
userId = 1

ser = serial.Serial('COM5', 9600, timeout=1)
time.sleep(2)


config = {
    'host': 'localhost',
    'user': 'root',
    'password': '',
    'database': 'project',
    'port': 3306
}

conn = pymysql.connect(**config)
cursor = conn.cursor()
sql = "SELECT * FROM device_usage ;"
cursor.execute(sql)
result = cursor.fetchall()
print(result)


cursor.execute(
    "SELECT gesture, address, command FROM ir_codes WHERE user_id=%s", (userId,))
result = cursor.fetchall()

# 從資料庫取出
irCode = {
    gesture: {'address': address, 'command': command}
    for gesture, address, command in result
}
print(irCode)
print(result)

is_muted = False


# 初始化 MediaPipe 手部追蹤模組
mpHands = mp.solutions.hands
hands = mpHands.Hands(max_num_hands=1)
mpDraw = mp.solutions.drawing_utils
keyboard = Controller()


# 初始化MediaPipe手勢檢測
mp_hands = mp.solutions.hands
hands = mp_hands.Hands(max_num_hands=2)  # 設定檢測兩隻手
mp_draw = mp.solutions.drawing_utils

# 設定螢幕的寬度和高度以進行滑鼠移動
screen_width, screen_height = pyautogui.size()


# 開啟攝像頭，並進行初始化
cap = cv2.VideoCapture(0)
time.sleep(2)  # 等待攝像頭初始化


# 初始化MediaPipe手勢檢測


def is_finger_bent(tip, pip):
    """ 判斷手指是否彎曲，TIP 是否位於 PIP 下方 """
    return tip.y > pip.y  # 如果 TIP 的 y 座標大於 PIP，手指被視為彎曲


# 初始化 MediaPipe Hand 模型
mp_hands = mp.solutions.hands
hands = mp_hands.Hands(static_image_mode=False, max_num_hands=2,
                       min_detection_confidence=0.5, min_tracking_confidence=0.5)

# 初始化 PyAutoGUI
pyautogui.FAILSAFE = False

# 初始化当前页数
current_page = 1

# 打开摄像头
cap = cv2.VideoCapture(0)

# 设置手势检测阈值
VOLUME_INCREMENT = 1
SCROLL_STEP = 50


def draw_keys(img):
    for i, row in enumerate(keys):
        for j, key in enumerate(row):
            x, y = 100 * j + 50, 100 * i + 50
            cv2.rectangle(img, (x, y), (x + 85, y + 85),
                          (255, 0, 255), cv2.FILLED)
            cv2.putText(img, key, (x + 20, y + 65),
                        cv2.FONT_HERSHEY_PLAIN, 4, (255, 255, 255), 4)
    cv2.putText(img, finalText, (60, 430),
                cv2.FONT_HERSHEY_PLAIN, 5, (255, 255, 255), 5)


# 手指弯曲检测


def is_finger_bent(landmarks, tip_idx, mcp_idx):
    return landmarks[tip_idx].y > landmarks[mcp_idx].y + 0.02


# 手指直立判断


def is_finger_straight(landmarks, tip_idx, mcp_idx):
    return landmarks[tip_idx].y < landmarks[mcp_idx].y - 0.05

# 平滑位置


def smooth_position(last_pos, new_pos, smoothing_factor=0.1):
    if last_pos is None:
        return new_pos
    return (
        int(last_pos[0] * (1 - smoothing_factor) +
            new_pos[0] * smoothing_factor),
        int(last_pos[1] * (1 - smoothing_factor) +
            new_pos[1] * smoothing_factor)
    )

# 初始化繪圖視窗


class DrawingWindow:
    def __init__(self, width, height):
        self.image = np.zeros((height, width, 3), np.uint8)  # 黑色背景
        self.last_point = None

    def draw(self, img, new_pos):
        img = cv2.flip(img, 1)
        if self.last_point is not None and new_pos is not None:
            smoothed_pos = smooth_position(self.last_point, new_pos)
            cv2.line(self.image, self.last_point, smoothed_pos, (0, 0, 255), 2)
            self.last_point = smoothed_pos
        else:
            self.last_point = new_pos

        cv2.imshow('Drawing', self.image)


# 建立繪圖視窗
drawing_window = DrawingWindow(720, 1280)


# 设置手势檢測阈值
VOLUME_INCREMENT = 1
SCROLL_STEP = 50


# 初始化参数
wCam, hCam = 640, 480
frameR = 100  # 内框大小
smoothening = 7
plocX, plocY = 0, 0
clocX, clocY = 0, 0

# 獲取螢幕尺寸
wScr, hScr = pyautogui.size()  # 獲取螢幕解析度
clickDistance = 30


# 獲取螢幕尺寸
wScr, hScr = pyautogui.size()  # 獲取螢幕解析度
clickDistance = 30


# 計算两个向量的夾角
def vector_2d_angle(v1, v2):
    v1_x, v1_y = v1
    v2_x, v2_y = v2
    try:
        angle = math.degrees(math.acos((v1_x * v2_x + v1_y * v2_y) / (
            ((v1_x ** 2 + v1_y ** 2) ** 0.5) * ((v2_x ** 2 + v2_y ** 2) ** 0.5))))
    except:
        angle = 180
    return angle

# 根據21個節点坐標計算每根手指的角度


def hand_angle(hand_):
    angle_list = []
    # 大拇指
    angle_list.append(vector_2d_angle(
        (hand_[0][0] - hand_[2][0], hand_[0][1] - hand_[2][1]),
        (hand_[3][0] - hand_[4][0], hand_[3][1] - hand_[4][1])))
    # 食指
    angle_list.append(vector_2d_angle(
        (hand_[0][0] - hand_[6][0], hand_[0][1] - hand_[6][1]),
        (hand_[7][0] - hand_[8][0], hand_[7][1] - hand_[8][1])))
    # 中指
    angle_list.append(vector_2d_angle(
        (hand_[0][0] - hand_[10][0], hand_[0][1] - hand_[10][1]),
        (hand_[11][0] - hand_[12][0], hand_[11][1] - hand_[12][1])))
    # 无名指
    angle_list.append(vector_2d_angle(
        (hand_[0][0] - hand_[14][0], hand_[0][1] - hand_[14][1]),
        (hand_[15][0] - hand_[16][0], hand_[15][1] - hand_[16][1])))
    # 小拇指
    angle_list.append(vector_2d_angle(
        (hand_[0][0] - hand_[18][0], hand_[0][1] - hand_[18][1]),
        (hand_[19][0] - hand_[20][0], hand_[19][1] - hand_[20][1])))
    return angle_list

# 根据手指角度列表返回对应手势编号


def hand_pos(angle_list):
    if all(angle >= 50 for angle in angle_list):
        return 0
    elif angle_list[0] >= 50 and angle_list[1] < 50 and all(angle >= 50 for angle in angle_list[2:]):
        return 1
    elif angle_list[0] >= 50 and angle_list[1] < 50 and angle_list[2] < 50 and all(angle >= 50 for angle in angle_list[3:]):
        return 2
    elif angle_list[0] >= 50 and angle_list[1] < 50 and angle_list[2] < 50 and angle_list[3] < 50 and angle_list[4] > 50:
        return 3
    elif angle_list[0] >= 50 and angle_list[1] < 50 and angle_list[2] < 50 and angle_list[3] < 50 and angle_list[4] < 50:
        return 4
    elif all(angle < 50 for angle in angle_list):
        return 5
    elif angle_list[0] < 50 and all(angle >= 50 for angle in angle_list[1:4]) and angle_list[4] < 50:
        return 6
    elif angle_list[0] < 50 and angle_list[1] < 50 and all(angle >= 50 for angle in angle_list[2:]):
        return 7
    elif angle_list[0] < 50 and angle_list[1] < 50 and angle_list[2] < 50 and angle_list[3] >= 50 and angle_list[4] >= 50:
        return 8
    elif angle_list[0] < 50 and angle_list[1] < 50 and angle_list[2] < 50 and angle_list[3] < 50 and angle_list[4] >= 50:
        return 9

    else:
        return None


def is_left_hand_eight(landmarks):
    """檢查左手是否比出數字 8（食指、中指和大拇指伸直，其餘彎曲）"""
    thumb_tip = landmarks[mp_hands.HandLandmark.THUMB_TIP]
    thumb_ip = landmarks[mp_hands.HandLandmark.THUMB_IP]

    index_tip = landmarks[mp_hands.HandLandmark.INDEX_FINGER_TIP]
    index_pip = landmarks[mp_hands.HandLandmark.INDEX_FINGER_PIP]

    middle_tip = landmarks[mp_hands.HandLandmark.MIDDLE_FINGER_TIP]
    middle_pip = landmarks[mp_hands.HandLandmark.MIDDLE_FINGER_PIP]

    ring_tip = landmarks[mp_hands.HandLandmark.RING_FINGER_TIP]
    pinky_tip = landmarks[mp_hands.HandLandmark.PINKY_TIP]

    # 判斷食指、中指和大拇指伸直，無名指和小指彎曲
    return (
        thumb_tip.y < thumb_ip.y and
        index_tip.y < index_pip.y and
        middle_tip.y < middle_pip.y and
        ring_tip.y > middle_pip.y and
        pinky_tip.y > middle_pip.y
    )


# 初始化 MediaPipe Hand 模型
hands = mp_hands.Hands(static_image_mode=False, max_num_hands=2,
                       min_detection_confidence=0.5, min_tracking_confidence=0.5)
pyautogui.FAILSAFE = False

# 打开摄像头
cap = cv2.VideoCapture(0)
wScr, hScr = pyautogui.size()  # 获取屏幕分辨率


# 主循环
while cap.isOpened():

    success, img = cap.read()
    img = cv2.flip(img, 1)
    imgRGB = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    results = hands.process(imgRGB)


# 從這裡是控制鍵盤

    ret, frame = cap.read()
    if not ret:
        break

   # frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    # results = hands.process(frame_rgb)

    # 初始化手势值
    left_hand_gesture = None
    left_hand_gesture = None
    x_distance = 0
    y_distance = 0  # 添加 y_distance 初始化
    if results.multi_hand_landmarks:
        for idx, hand_landmarks in enumerate(results.multi_hand_landmarks):
            handedness = results.multi_handedness[idx].classification[0].label
            h, w, _ = frame.shape
            hand_coords = [(int(landmark.x * w), int(landmark.y * h))
                           for landmark in hand_landmarks.landmark]
            angle_list = hand_angle(hand_coords)

            # 获取左手手势编号
            if handedness == 'Left':
                left_hand_gesture = hand_pos(angle_list)

            # 右手功能操作
            if handedness == 'Right' and left_hand_gesture is not None:

                index_tip = hand_landmarks.landmark[mp_hands.HandLandmark.INDEX_FINGER_TIP]
                thumb_tip = hand_landmarks.landmark[mp_hands.HandLandmark.THUMB_TIP]
                middle_tip = hand_landmarks.landmark[mp_hands.HandLandmark.MIDDLE_FINGER_TIP]

                x_distance = index_tip.x - thumb_tip.x
                y_distance = index_tip.y - middle_tip.y

                right_hand_coords = hand_coords  # 右手的格式
                right_hand_gesture = hand_pos(
                    hand_angle(right_hand_coords))  # 辨識右手手勢從0-9

                if left_hand_gesture == 1:  # 應用程式切換

                    last_switch_time = 0  # 上次切换的时间
                    SWITCH_DELAY = 1  # 设置切换间隔（单位：秒）

                    current_time = time.time()  # 获取当前时间

                    if current_time - last_switch_time > SWITCH_DELAY:  # 检查时间间隔
                        if x_distance > 0.1:
                            pyautogui.hotkey('alt', 'tab')  # 切换到下一个应用
                        elif x_distance < -0.1:
                            pyautogui.hotkey('alt', 'shift', 'tab')  # 切换到上一个应用

                        last_switch_time = current_time  # 更新上次切换时间
                    try:
                        sql = "UPDATE device_usage SET appliance_change	= appliance_change	+ 1 WHERE user_id = %s"
                        now = datetime.now()
                        formatted_time = now.strftime('%Y-%m-%d %H:%M:%S')
                        cursor.execute(
                            "INSERT INTO user_activity (user_id, activity, activity_time)VALUES (%s, %s, %s);", (userId, "appliance_change", now))
                        print(userId)
                        cursor.execute(sql, (userId))
                        conn.commit()
                        print("appliance_change更新成功！")
                    except pymysql.MySQLError as e:
                        print(f"資料庫錯誤: {e}")

                elif left_hand_gesture == 0:
                    last_switch_time = 0  # 上次切换的时间
                    SWITCH_DELAY = 1  # 设置切换间隔（单位：秒）
                    # 切换音量静音状态
                    pyautogui.press('volumemute')  # 切换音量静音
                    # 更新静音状态标志
                    is_muted = not is_muted  # 如果已经静音就恢复，反之静音

                elif left_hand_gesture == 2:  # 畫圖功能
                    new_pos = (int(index_tip.x * drawing_window.image.shape[1]), int(
                        index_tip.y * drawing_window.image.shape[0]))
                    drawing_window.draw(frame, new_pos)
                    try:
                        sql = "UPDATE device_usage SET drawing_gesture_count = drawing_gesture_count + 1 WHERE user_id = %s"
                        now = datetime.now()
                        formatted_time = now.strftime('%Y-%m-%d %H:%M:%S')
                        cursor.execute("INSERT INTO user_activity (user_id, activity, activity_time)VALUES (%s, %s, %s);", (
                            userId, "drawing_gesture_count", now))
                        cursor.execute(sql, (userId))
                        conn.commit()

                        print("drawing_gesture_count更新成功！")
                    except pymysql.MySQLError as e:
                        print(f"資料庫錯誤: {e}")

                elif left_hand_gesture == 3:  # 音量控制
                    distance = math.sqrt(
                        (thumb_tip.x - index_tip.x)**2 + (thumb_tip.y - index_tip.y)**2)
                    if distance > 0.1:
                        pyautogui.press('volumeup', presses=VOLUME_INCREMENT)
                    else:
                        pyautogui.press('volumedown', presses=VOLUME_INCREMENT)
                    try:
                        now = datetime.now()
                        formatted_time = now.strftime('%Y-%m-%d %H:%M:%S')
                        cursor.execute("INSERT INTO user_activity (user_id, activity, activity_time)VALUES (%s, %s, %s);", (
                            userId, "volume_gesture_count", now))
                        sql = "UPDATE device_usage SET volume_gesture_count = volume_gesture_count + 1 WHERE user_id = %s"
                        cursor.execute(sql, (userId))
                        conn.commit()
                        print("volume_gesture_count更新成功！")
                    except:
                        print("volume_gesture_count更新錯誤")

                elif left_hand_gesture == 4:  # 音樂控制
                    if x_distance > 0.1:
                        pyautogui.press('nexttrack')
                    elif x_distance < -0.1:
                        pyautogui.press('prevtrack')
                    try:
                        now = datetime.now()
                        formatted_time = now.strftime('%Y-%m-%d %H:%M:%S')
                        cursor.execute("INSERT INTO user_activity (user_id, activity, activity_time)VALUES (%s, %s, %s);", (
                            userId, "music_gesture_count", now))
                        sql = "UPDATE device_usage SET music_gesture_count = music_gesture_count + 1 WHERE user_id = %s"
                        cursor.execute(sql, (userId))
                        conn.commit()
                        print("music_gesture_count更新成功！")
                    except:
                        print("music_gesture_count更新錯誤")

                elif left_hand_gesture == 5:  # 網頁滾動
                    if y_distance > 0.1:
                        pyautogui.scroll(-SCROLL_STEP)
                    elif y_distance < -0.1:
                        pyautogui.scroll(SCROLL_STEP)
                    try:
                        now = datetime.now()
                        formatted_time = now.strftime('%Y-%m-%d %H:%M:%S')
                        cursor.execute("INSERT INTO user_activity (user_id, activity, activity_time)VALUES (%s, %s, %s);", (
                            userId, "scroll_gesture_count", now))
                        sql = "UPDATE device_usage SET scroll_gesture_count = scroll_gesture_count + 1 WHERE user_id = %s"
                        cursor.execute(sql, (userId))
                        conn.commit()
                        print("scroll_gesture_count更新成功！")
                    except:
                        print("scroll_gesture_count更新錯誤")

                elif left_hand_gesture == 6:  # 簡報翻頁
                    if x_distance > 0.1:
                        pyautogui.press('right')
                        current_page += 1
                    elif x_distance < -0.1:
                        pyautogui.press('left')
                        current_page = max(1, current_page - 1)
                    try:
                        now = datetime.now()
                        formatted_time = now.strftime('%Y-%m-%d %H:%M:%S')
                        cursor.execute("INSERT INTO user_activity (user_id, activity, activity_time)VALUES (%s, %s, %s);", (
                            userId, "slide_gesture_count", now))
                        sql = "UPDATE device_usage SET slide_gesture_count = slide_gesture_count + 1 WHERE user_id = %s"
                        cursor.execute(sql, (userId))
                        conn.commit()
                        print("slide_gesture_count更新成功！")
                    except:
                        print("slide_gesture_count更新錯誤")

                # 確保正確地使用 datetime.now().second
                elif left_hand_gesture == 7:
                    if right_hand_gesture in irCode:
                        address = irCode[right_hand_gesture]["address"]
                        command = irCode[right_hand_gesture]["command"]
                        print(address, command)
                        # 格式化為一個字串，準備傳送
                        message = f"{address}:{command}"

                        # 傳送為 bytes 格式
                        ser.write(bytes(message, 'utf-8'))
                        print("send")

                        time.sleep(1)
                        try:
                            now = datetime.now()
                            formatted_time = now.strftime('%Y-%m-%d %H:%M:%S')
                            cursor.execute("INSERT INTO user_activity (user_id, activity, activity_time)VALUES (%s, %s, %s);", (
                                userId, "household ", now))
                            sql = "UPDATE device_usage SET household_gesture_count  = household_gesture_count  + 1 WHERE user_id = %s"
                            cursor.execute(sql, (userId))
                            conn.commit()
                            print("household_gesture_count更新成功！")
                        except:
                            print("household_gesture_count更新錯誤")
                elif left_hand_gesture == 8:  # 滑鼠
                    left_hand_ready = False

                    def is_finger_bent1(tip, pip):
                        """判斷手指是否彎曲"""
                        return tip.y > pip.y  # TIP 在 PIP 下方則視為彎曲

                    while True:

                        success, image = cap.read()
                        if not success:
                            break  # 如果讀取失敗，退出迴圈

                        # 鏡像影像
                        image = cv2.flip(image, 1)  # 1 表示水平翻轉，0 表示垂直翻轉
                        # 轉換為 RGB 格式

                        image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
                        results = hands.process(image_rgb)

                        if results.multi_hand_landmarks:
                            for idx, hand_landmarks in enumerate(results.multi_hand_landmarks):
                                handedness = results.multi_handedness[idx].classification[0].label

                                if handedness == 'Left':  # 左手檢測
                                    left_hand_ready = is_left_hand_eight(
                                        hand_landmarks.landmark)

                                if handedness == 'Right' and left_hand_ready:
                                    # 提取右手座標
                                    index_tip = hand_landmarks.landmark[mp_hands.HandLandmark.INDEX_FINGER_TIP]
                                    index_pip = hand_landmarks.landmark[mp_hands.HandLandmark.INDEX_FINGER_PIP]
                                    middle_tip = hand_landmarks.landmark[mp_hands.HandLandmark.MIDDLE_FINGER_TIP]
                                    middle_pip = hand_landmarks.landmark[mp_hands.HandLandmark.MIDDLE_FINGER_PIP]

                                    # 設定食指和中指的顏色
                                    index_color = (0, 255, 0)  # 預設為綠色
                                    middle_color = (0, 255, 0)  # 預設為綠色

                                    # 滑鼠控制
                                    x = int(index_tip.x * screen_width)
                                    y = int(index_tip.y * screen_height)
                                    pyautogui.moveTo(x, y)

                                    # 判斷食指是否彎曲，模擬左鍵點擊
                                    if is_finger_bent1(index_tip, index_pip):
                                        pyautogui.mouseDown()
                                        pyautogui.mouseUp()
                                        # 左鍵按下時，食指變紅色
                                        index_color = (0, 0, 255)

                                    # 判斷中指是否彎曲，模擬右鍵點擊
                                    if is_finger_bent1(middle_tip, middle_pip):
                                        pyautogui.rightClick()
                                        # 右鍵按下時，中指變紅色
                                        middle_color = (0, 0, 255)

                                    # 根據手指節點的顏色繪製手指
                                    for i, landmark in enumerate(hand_landmarks.landmark):
                                        h, w, _ = image.shape
                                        cx, cy = int(
                                            landmark.x * w), int(landmark.y * h)

                                        if i == mp_hands.HandLandmark.INDEX_FINGER_TIP:
                                            color = index_color
                                        elif i == mp_hands.HandLandmark.MIDDLE_FINGER_TIP:
                                            color = middle_color
                                        else:
                                            color = (0, 255, 0)  # 其他節點保持綠色

                                        cv2.circle(image, (cx, cy),
                                                   10, color, cv2.FILLED)

                    else:
                        break

                    try:
                        now = datetime.now()
                        formatted_time = now.strftime('%Y-%m-%d %H:%M:%S')
                        cursor.execute("INSERT INTO user_activity (user_id, activity, activity_time)VALUES (%s, %s, %s);", (
                            userId, "mouse_gesture_count", now))
                        sql = "UPDATE device_usage SET mouse_gesture_count = mouse_gesture_count + 1 WHERE user_id = %s"
                        cursor.execute(sql, (userId))
                        conn.commit()
                        print("mouse_gesture_count更新成功！")
                    except:
                        print("mouse_gesture_count更新錯誤")

                elif left_hand_gesture == 9:  # 左手比"9"
                    left_hand_ready = False

                    # 設定按鍵配置
                    keys = [["Q", "W", "E", "R", "T", "Y", "U", "I", "O", "P"],
                            ["A", "S", "D", "F", "G", "H", "J", "K", "L", ";"],
                            ["Z", "X", "C", "V", "B", "N", "M", ",", ".", "/"]]

                    finalText = ""  # 顯示輸入結果的字串

                    # 定義按鈕繪製函數

                    def drawAll(img, buttonList):
                        for button in buttonList:
                            x, y = button.pos
                            w, h = button.size
                            # 使用 OpenCV 繪製矩形
                            cv2.rectangle(img, (x, y), (x + w, y + h),
                                          (255, 0, 255), cv2.FILLED)
                            cv2.putText(img, button.text, (x + 20, y + 65),
                                        cv2.FONT_HERSHEY_PLAIN, 4, (255, 255, 255), 4)
                        return img

                    # 定義按鈕類別

                    class Button():
                        def __init__(self, pos, text, size=[85, 85]):
                            self.pos = pos
                            self.size = size
                            self.text = text

                    # 創建按鈕列表
                    buttonList = []
                    for i in range(len(keys)):
                        for j, key in enumerate(keys[i]):
                            buttonList.append(
                                Button([100 * j + 30, 100 * i + 30], key))

                    # 定義是否顯示新視窗
                    show_new_window = False

                    # 繪製按鈕
                    img = drawAll(img, buttonList)

                    # 如果檢測到手
                    if handedness == 'Right':  # 檢測右手
                        handLms = hand_landmarks  # 取得右手的關鍵點
                        lmList = []
                        for id, lm in enumerate(handLms.landmark):
                            h, w, c = img.shape
                            cx, cy = int(lm.x * w), int(lm.y * h)
                            lmList.append([id, cx, cy])
                        mpDraw.draw_landmarks(
                            img, handLms, mpHands.HAND_CONNECTIONS)

                    if handedness == 'Left':  # 左手檢測
                        left_hand_ready = is_left_hand_eight(
                            hand_landmarks.landmark)

                    if handedness == 'Right' and left_hand_ready:

                        # 檢查是否點擊按鈕
                        if lmList:
                            for button in buttonList:
                                x, y = button.pos
                                w, h = button.size

                                # 判斷食指是否在按鈕範圍內
                                # 8 是食指尖的索引
                                # 判斷食指是否在按鈕範圍內
                                # 8 是食指尖的索引
                                if x < lmList[8][1] < x + w and y < lmList[8][2] < y + h:
                                    cv2.rectangle(
                                        img, (x - 5, y - 5), (x + w + 5, y + h + 5), (175, 0, 175), cv2.FILLED)
                                    cv2.putText(
                                        img, button.text, (x + 20, y + 65), cv2.FONT_HERSHEY_PLAIN, 4, (255, 255, 255), 4)

                                    # 檢測食指和中指的距離
                                    x1, y1 = lmList[8][1], lmList[8][2]  # 食指尖
                                    # 中指尖
                                    x2, y2 = lmList[12][1], lmList[12][2]
                                    length = ((x2 - x1) ** 2 +
                                              (y2 - y1) ** 2) ** 0.5

                                    # 如果距離小於 30，表示點擊
                                    if length < 30:

                                        # 模擬鍵盤按鍵輸入
                                        keyboard.press(button.text)
                                        finalText += button.text  # 更新輸入文字
                                        sleep(0.15)  # 避免重複點擊

                    # 鼠标控制：用食指的位置移動鼠標
                    finger_tip = lmList[8]
                    pyautogui.moveTo(finger_tip[0], finger_tip[1])
                    # 如果距離小於 30，表示點擊
                    if lmList:
                        for button in buttonList:
                            x, y = button.pos
                            w, h = button.size

                            # 判斷食指是否在按鈕範圍內
                            if x < lmList[8][1] < x + w and y < lmList[8][2] < y + h:  # 8 是食指尖的索引
                                cv2.rectangle(
                                    img, (x - 5, y - 5), (x + w + 5, y + h + 5), (175, 0, 175), cv2.FILLED)
                                cv2.putText(img, button.text, (x + 20, y + 65),
                                            cv2.FONT_HERSHEY_PLAIN, 4, (255, 255, 255), 4)

                                # 檢測食指和中指的距離
                                x1, y1 = lmList[8][1], lmList[8][2]  # 食指尖
                                x2, y2 = lmList[12][1], lmList[12][2]  # 中指尖
                                length = ((x2 - x1) ** 2 +
                                          (y2 - y1) ** 2) ** 0.5

                                # 繪製輸入框
                                cv2.rectangle(
                                    img, (50, 350), (700, 450), (175, 0, 175), cv2.FILLED)

                                # 調整文字位置並限制顯示長度
                                max_length = 30  # 最多顯示 30 個字元
                                if len(finalText) > max_length:
                                    finalText = finalText[-max_length:]

                                # 按鈕變綠色並顯示文字
                                cv2.rectangle(
                                    img, (x, y), (x + w, y + h), (0, 255, 0), cv2.FILLED)
                                cv2.putText(img, button.text, (x + 20, y + 65),
                                            cv2.FONT_HERSHEY_PLAIN, 4, (255, 255, 255), 4)

                                # 顯示更新的影像

                                cv2.imshow("Image", img)
                                print(f"食指位置: {lmList[8][1]}, {lmList[8][2]}")
                                print(f"按鈕範圍: x={x}, y={y}, w={w}, h={h}")
                                print(f"距離: {length}")

                    if show_new_window:
                        # 創建新視窗並顯示按鍵配置和輸入結果
                        new_window = np.zeros((720, 1280), np.uint8)
                        draw_keys(new_window)
                        cv2.imshow("Key Configuration", new_window)
                        cv2.waitKey(1)

                    try:
                        now = datetime.now()
                        formatted_time = now.strftime('%Y-%m-%d %H:%M:%S')
                        cursor.execute("INSERT INTO user_activity (user_id, activity, activity_time)VALUES (%s, %s, %s);", (
                            userId, "keyboard_gesture_count", now))
                        sql = "UPDATE device_usage SET keyboard_gesture_count = keyboard_gesture_count + 1 WHERE user_id = %s"
                        cursor.execute(sql, (userId))
                        conn.commit()
                        print("keyboard_gesture_count更新成功！")
                    except:
                        print("keyboard_gesture_count更新錯誤")

        # 手势名称映射
    gesture_names = {
        0: "mute",
        1: "Switch Apps",
        2: "Drawing Mode",
        3: "Volume Control",
        4: "Music Control",
        5: "Scroll Webpage",
        6: "Presentation Control",
        7: "Control fan",
        8: "Mouse Control",
        9: "Keyboard Mode"
    }

    # 显示当前手势名称
    if left_hand_gesture is not None:
        # 获取手势名称
        gesture_name = gesture_names.get(left_hand_gesture, "Unknown Gesture")

        # 在左上角显示手势名称
        cv2.putText(frame, f'Gesture: {gesture_name}', (10, 120), cv2.FONT_HERSHEY_SIMPLEX,
                    1, (0, 255, 0), 2, cv2.LINE_AA)

    # 显示手势检测结果

    if left_hand_gesture is not None:
        cv2.putText(frame, f'Left Hand Gesture: {left_hand_gesture}', (
            10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 2)
    if results.multi_handedness:
        cv2.putText(frame, f'X Distance: {x_distance:.2f}',
                    (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 2)
        cv2.putText(frame, f'Y Distance: {y_distance:.2f}', (
            10, 90), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 2)  # 添加 Y Distance 的显示

    # 显示摄像头画面
    cv2.imshow('Hand Gesture Control', frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break


if __name__ == '__main__':
    app.run(host='127.0.0.1', port=8082)
ser.close()
cap.release()
cv2.destroyAllWindows()
cursor.close()
conn.close()
