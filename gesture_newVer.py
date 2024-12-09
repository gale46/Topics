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
from PIL import Image, ImageFont, ImageDraw

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

font_path = "NotoSansTC-Regular.ttf"
font = ImageFont.truetype(font_path, 32)
is_muted = False
ppt_next = False
distance_thumb_index = 0.1
distance_index_middle = 50
x_mouse=500
y_mouse=500
pyautogui.FAILSAFE = False
current_page = 1
VOLUME_INCREMENT = 1
SCROLL_STEP = 50
VOLUME_INCREMENT = 1
SCROLL_STEP = 50
wCam, hCam = 640, 480
frameR = 100  # 内框大小
smoothening = 7
plocX, plocY = 0, 0
clocX, clocY = 0, 0
clickDistance = 30
last_switch_time = 0  # 上次切换的时间
keys = [["Q", "W", "E", "R", "T", "Y", "U", "I", "O", "P"],
        ["A", "S", "D", "F", "G", "H", "J", "K", "L", ";"],
        ["Z", "X", "C", "V", "B", "N", "M", ",", ".", "/"]]
finalText = ""  # 顯示輸入結果的字串
# 定義按鈕類別
class Button():
    def __init__(self, pos, text, size=[50, 50]):
        self.pos = pos
        self.size = size
        self.text = text

# 創建按鈕列表
buttonList = []
for i in range(len(keys)):
    for j, key in enumerate(keys[i]):
        buttonList.append(
            Button([60 * j + 5, 100 * i + 10], key))

def draw_chinese_text(image, text, position, font, font_color=(0, 255, 0)):
    image_pil = Image.fromarray(cv2.cvtColor(image, cv2.COLOR_BGR2RGB)) # 將 OpenCV 圖片轉換為 Pillow 圖片
    draw = ImageDraw.Draw(image_pil) # 繪製文字
    draw.text(position, text, font=font, fill=font_color) # 將 Pillow 圖片轉回 OpenCV 圖片
    return cv2.cvtColor(np.array(image_pil), cv2.COLOR_RGB2BGR)

# 定義按鈕繪製函數
def drawAll(img, buttonList):
    for button in buttonList:
        x, y = button.pos
        w, h = button.size
        cv2.rectangle(img, (x, y), (x + w, y + h),(255, 0, 255), cv2.FILLED)
        cv2.putText(img, button.text, (x + 10, y + 35),
        cv2.FONT_HERSHEY_PLAIN, 3, (255, 255, 255), 4)
    return img

def is_finger_bent(tip, pip):
    return tip.y > pip.y  # 如果 TIP 的 y 座標大於 PIP，手指被視為彎曲

# 平滑位置, 用在手指繪畫
def smooth_position(last_pos, new_pos, smoothing_factor=0.1):
    if last_pos is None:
        return new_pos
    return (int(last_pos[0]*(1-smoothing_factor)+new_pos[0]*smoothing_factor), int(last_pos[1]*(1-smoothing_factor) + new_pos[1]*smoothing_factor))

# 計算两向量的夾角,用在鍵盤
def vector_2d_finger(v1, v2):
    v1_x, v1_y = v1
    v2_x, v2_y = v2
    try:
        finger = math.degrees(math.acos((v1_x * v2_x + v1_y * v2_y) / (
            ((v1_x ** 2 + v1_y ** 2) ** 0.5) * ((v2_x ** 2 + v2_y ** 2) ** 0.5))))
    except:
        finger = 180
    return finger

# 根據21個節點坐標計算每根手指的角度, 偵測手勢1,2,3等
def hand_finger(hand_):
    finger_list = []
    # 大拇指
    finger_list.append(vector_2d_finger((hand_[0][0] - hand_[2][0], hand_[0][1] - hand_[2][1]),(hand_[3][0] - hand_[4][0], hand_[3][1] - hand_[4][1])))
    # 食指
    finger_list.append(vector_2d_finger((hand_[0][0] - hand_[6][0], hand_[0][1] - hand_[6][1]),(hand_[7][0] - hand_[8][0], hand_[7][1] - hand_[8][1])))
    # 中指
    finger_list.append(vector_2d_finger((hand_[0][0] - hand_[10][0], hand_[0][1] - hand_[10][1]),(hand_[11][0] - hand_[12][0], hand_[11][1] - hand_[12][1])))
    # 無名指
    finger_list.append(vector_2d_finger((hand_[0][0] - hand_[14][0], hand_[0][1] - hand_[14][1]),(hand_[15][0] - hand_[16][0], hand_[15][1] - hand_[16][1])))
    # 小拇指
    finger_list.append(vector_2d_finger((hand_[0][0] - hand_[18][0], hand_[0][1] - hand_[18][1]),(hand_[19][0] - hand_[20][0], hand_[19][1] - hand_[20][1])))
    return finger_list

def hand_pos(finger_list):
    if all(finger >= 50 for finger in finger_list):
        return 0
    elif finger_list[0] >= 50 and finger_list[1] < 50 and all(finger >= 50 for finger in finger_list[2:]):
        return 1
    elif finger_list[0] >= 50 and finger_list[1] < 50 and finger_list[2] < 50 and all(finger >= 50 for finger in finger_list[3:]):
        return 2
    elif finger_list[0] >= 50 and finger_list[1] < 50 and finger_list[2] < 50 and finger_list[3] < 50 and finger_list[4] > 50:
        return 3
    elif finger_list[0] >= 50 and finger_list[1] < 50 and finger_list[2] < 50 and finger_list[3] < 50 and finger_list[4] < 50:
        return 4
    elif all(finger < 50 for finger in finger_list):
        return 5
    elif finger_list[0] < 50 and all(finger >= 50 for finger in finger_list[1:4]) and finger_list[4] < 50:
        return 6
    elif finger_list[0] < 50 and finger_list[1] < 50 and all(finger >= 50 for finger in finger_list[2:]):
        return 7
    elif finger_list[0] < 50 and finger_list[1] < 50 and finger_list[2] < 50 and finger_list[3] >= 50 and finger_list[4] >= 50:
        return 8
    elif finger_list[0] < 50 and finger_list[1] < 50 and finger_list[2] < 50 and finger_list[3] < 50 and finger_list[4] >= 50:
        return 9
    else:
        return None
    
# 初始化 MediaPipe 手部追蹤模組
mpHands = mp.solutions.hands
hands = mpHands.Hands(max_num_hands=2, min_detection_confidence=0.5, min_tracking_confidence=0.5)
mpDraw = mp.solutions.drawing_utils
keyboard = Controller()

screen_width, screen_height = pyautogui.size()
cap = cv2.VideoCapture(0)


#初始化繪圖視窗
class DrawingWindow:
    def __init__(self, width, height):
        self.image = np.zeros((height, width, 3), np.uint8)  #黑色背景
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

# 主循环
while cap.isOpened():
    success, img = cap.read() 
    img = cv2.flip(img, 1)
    imgRGB = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    results = hands.process(imgRGB)    
    left_hand_gesture = None
    x_distance = 0
    y_distance = 0

    if results.multi_hand_landmarks:
        for idx, hand_landmarks in enumerate(results.multi_hand_landmarks):
            handedness = results.multi_handedness[idx].classification[0].label
            h, w, _ = img.shape
            
            handLms = hand_landmarks  # 取得右手的關鍵點
            mpDraw.draw_landmarks(img, handLms, mpHands.HAND_CONNECTIONS)
            
            if handedness == 'Right':
                hand_coords_right = [(int(landmark.x * w), int(landmark.y * h))
                               for landmark in hand_landmarks.landmark]
                index_tip_right = hand_landmarks.landmark[mpHands.HandLandmark.INDEX_FINGER_TIP]
                index_pip_right = hand_landmarks.landmark[mpHands.HandLandmark.INDEX_FINGER_PIP]
                thumb_tip_right = hand_landmarks.landmark[mpHands.HandLandmark.THUMB_TIP]
                middle_tip_right = hand_landmarks.landmark[mpHands.HandLandmark.MIDDLE_FINGER_TIP]    
                middle_pip_right = hand_landmarks.landmark[mpHands.HandLandmark.MIDDLE_FINGER_PIP]    
                x_distance = index_tip_right.x - thumb_tip_right.x
                y_distance = index_tip_right.y - middle_tip_right.y
                distance_thumb_index = math.sqrt((thumb_tip_right.x - index_tip_right.x)**2 + (thumb_tip_right.y - index_tip_right.y)**2)
                x1, y1 = hand_coords_right[8][0], hand_coords_right[8][1]  # 食指尖
                x2, y2 = hand_coords_right[12][0], hand_coords_right[12][1]  # 中指尖
                distance_index_middle = ((x2 - x1) ** 2 + (y2 - y1) ** 2) ** 0.5   # 檢測食指和中指的距離
                x_mouse = int(index_tip_right.x * screen_width)
                y_mouse = int(index_tip_right.y * screen_height)
                smoothed_pos = (int(index_tip_right.x * drawing_window.image.shape[1]), int(
                index_tip_right.y * drawing_window.image.shape[0]))


            if handedness == 'Left':
                hand_coords_left = [(int(landmark.x * w), int(landmark.y * h))
                               for landmark in hand_landmarks.landmark]
                finger_list = hand_finger(hand_coords_left)
                left_hand_gesture = hand_pos(finger_list) #hand_pos()返回123456789

            if left_hand_gesture == 0: # 靜音控制
                SWITCH_DELAY = 3  # 設置切换间隔（单位：秒）
                current_time = time.time()  # 獲取時間間隔
                if current_time - last_switch_time > SWITCH_DELAY:  # 查时間間隔
                    if is_muted == False:
                        pyautogui.press('volumemute')  # 切换音量静音
                        is_muted = True
                    else:
                        pyautogui.press('volumeup')
                        is_muted = False
                    last_switch_time = current_time  # 更新上次切換時間
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
                
            elif left_hand_gesture == 1:  # 應用程式切換
                SWITCH_DELAY = 3  # 設置切换间隔（单位：秒）
                current_time = time.time()  # 獲取時間間隔
                if current_time - last_switch_time > SWITCH_DELAY:  # 查时間間隔
                    if x_distance > 0.1:
                        pyautogui.hotkey('alt', 'tab')  # 切換到下一个
                    elif x_distance < -0.1:
                        pyautogui.hotkey('alt', 'shift', 'tab')  # 切換到上一个
                    last_switch_time = current_time  # 更新上次切換時間
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

            elif left_hand_gesture == 2:  # 畫圖功能
                if handedness == 'Right':
                    drawing_window.draw(img, smoothed_pos)
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
                    if distance_thumb_index > 0.1:
                        pyautogui.press('volumeup', presses=VOLUME_INCREMENT)
                    elif distance_thumb_index <0.1:
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
                if -0.1<x_distance <0.1:
                        ppt_next = False
                if x_distance > 0.1 and ppt_next == False:
                    pyautogui.press('right')
                    ppt_next = True
                    current_page += 1
                elif x_distance < -0.1 and ppt_next == False:
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
                if hand_coords_right in irCode:
                    address = irCode[hand_coords_right]["address"]
                    command = irCode[hand_coords_right]["command"]
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
                if handedness == 'Right':
                    pyautogui.moveTo(x_mouse, y_mouse)    
                    if distance_index_middle < 30: # 如果距離小於 30，表示點擊模擬左鍵點擊
                        pyautogui.mouseDown()
                        pyautogui.mouseUp()
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

            elif left_hand_gesture == 9:  #鍵盤   
                    img = drawAll(img, buttonList)                     # 繪製按鈕                                                                                                   
                 
                    if hand_coords_left:
                        for button in buttonList:
                            x, y = button.pos
                            w, h = button.size

                            if x < hand_coords_right[8][0] < x + w and y < hand_coords_right[8][1] < y + h:  # 8 是食指尖的索引
                                cv2.rectangle(img, (x - 5, y - 5), (x + w + 5, y + h + 5), (175, 0, 175), cv2.FILLED)
                                cv2.putText(img, button.text, (x + 20, y + 65), cv2.FONT_HERSHEY_PLAIN, 4, (255, 255, 255), 4)

                                if distance_index_middle < 30: # 如果距離小於 30，表示點擊                                           
                                    keyboard.press(button.text)
                                    finalText += button.text  # 更新輸入文字
                                    sleep(0.15)  # 避免重複點擊
                        cv2.rectangle(img, (50, 350), (700, 450), (175, 0, 175), cv2.FILLED)
                        cv2.putText(img, finalText, (60, 430), cv2.FONT_HERSHEY_PLAIN, 5, (255, 255, 255), 5)
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
                            
# 手勢名稱
    gesture_names = {
        0: "靜音",
        1: "切換應用程式",
        2: "繪圖模式",
        3: "音量控制",
        4: "音樂控制",
        5: "上下捲動",
        6: "投影片上下頁",
        7: "家電（電扇）",
        8: "手勢滑鼠",
        9: "手勢鍵盤"
    }
    
#顯示當前手勢名稱
    if left_hand_gesture is not None:
        gesture_name = gesture_names.get(left_hand_gesture, "未定義手勢")  # 獲取手势名稱
        img = draw_chinese_text(img, f"手勢功能: {gesture_name}", (10, 40), font, (0, 255, 0))
        cv2.putText(img, f'', (10, 20), cv2.FONT_HERSHEY_SIMPLEX,1, (0, 255, 0), 2, cv2.LINE_AA) # 在左上角顯示手势名稱

    if left_hand_gesture is not None:     # 顯示手势檢查结果
        cv2.putText(img, f'Left Hand Gesture: {left_hand_gesture}', (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 2)

    cv2.imshow('Hand Gesture Control', img)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break
cap.release()
cv2.destroyAllWindows()

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=8082)
ser.close()
cap.release()
cv2.destroyAllWindows()
cursor.close()
conn.close()
