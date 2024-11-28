# -*- coding: utf-8 -*-
"""
Created on Fri Nov  8 12:57:32 2024

@author: User
"""
import cv2
import mediapipe as mp
import pyautogui
import math
import numpy as np
import pymysql
import serial
import time
from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
from datetime import datetime

ser = serial.Serial('COM5', 9600, timeout=1) 
time.sleep(2)

config = {
    'host': 'localhost',  
    'user': 'root',
    'password': '',   
    'database': 'project',
    'port': 3306  
}
userId=1
conn = pymysql.connect(**config)
cursor = conn.cursor()
sql = "SELECT * FROM device_usage ;"
cursor.execute(sql)
result = cursor.fetchall()
print(result)



cursor.execute("SELECT gesture, address, command FROM ir_codes WHERE user_id=%s", (userId,))
result = cursor.fetchall()

#從資料庫取出
irCode = {
    gesture: {'address': address, 'command': command}
    for gesture, address, command in result
}
print(irCode)
print(result)

# 初始化 MediaPipe Hand 模型
mp_hands = mp.solutions.hands
hands = mp_hands.Hands(static_image_mode=False, max_num_hands=2, min_detection_confidence=0.5, min_tracking_confidence=0.5)

# 初始化 PyAutoGUI
pyautogui.FAILSAFE = False

# 初始化当前页数
current_page = 1

# 打开摄像头
cap = cv2.VideoCapture(0)

# 设置手势检测阈值
VOLUME_INCREMENT = 1
SCROLL_STEP = 50

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
        int(last_pos[0] * (1 - smoothing_factor) + new_pos[0] * smoothing_factor),
        int(last_pos[1] * (1 - smoothing_factor) + new_pos[1] * smoothing_factor)
    )

# 初始化绘图窗口类
class DrawingWindow:
    def __init__(self, width, height):
        self.image = np.zeros((height, width, 3), np.uint8)  # 绘图窗口的黑色背景
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

# 创建绘图窗口实例
drawing_window = DrawingWindow(640, 480)


# 设置手势检测阈值
VOLUME_INCREMENT = 1
SCROLL_STEP = 50



# 初始化参数
wCam, hCam = 640, 480
frameR = 100  # 内框大小
smoothening = 7
plocX, plocY = 0, 0
clocX, clocY = 0, 0

# 获取屏幕尺寸
wScr, hScr = pyautogui.size()  # 获取屏幕解析度
clickDistance = 30


# 计算两个向量的夹角
def vector_2d_angle(v1, v2):
    v1_x, v1_y = v1
    v2_x, v2_y = v2
    try:
        angle = math.degrees(math.acos((v1_x * v2_x + v1_y * v2_y) / (((v1_x ** 2 + v1_y ** 2) ** 0.5) * ((v2_x ** 2 + v2_y ** 2) ** 0.5))))
    except:
        angle = 180
    return angle

# 根据21个节点坐标计算每根手指的角度
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

# 初始化 MediaPipe Hand 模型
hands = mp_hands.Hands(static_image_mode=False, max_num_hands=2, min_detection_confidence=0.5, min_tracking_confidence=0.5)
pyautogui.FAILSAFE = False

# 打开摄像头
cap = cv2.VideoCapture(0)
wScr, hScr = pyautogui.size()  # 获取屏幕分辨率

# 主循环
while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        break

    frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results = hands.process(frame_rgb)
    
    # 初始化手势值
    left_hand_gesture = None
    x_distance = 0
    y_distance = 0  # 添加 y_distance 初始化
    right_hand_gesture = None
    if results.multi_hand_landmarks:
        for idx, hand_landmarks in enumerate(results.multi_hand_landmarks):
            handedness = results.multi_handedness[idx].classification[0].label#判斷左右手
            h, w, _ = frame.shape
            hand_coords = [(int(landmark.x * w), int(landmark.y * h)) for landmark in hand_landmarks.landmark]#確保x, y軸為


            
            

            # 获取左手手势编号
            if handedness == 'Left':
                left_hand_coords = hand_coords
                left_hand_gesture = hand_pos(hand_angle(left_hand_coords))
            '''
            新增右手部節點
            '''
            if handedness == 'Right':
                right_hand_coords = hand_coords#右手的格式
                right_hand_gesture = hand_pos(hand_angle(right_hand_coords))#辨識右手手勢從0-9
                    
            # 右手功能操作
            if handedness == 'Right' and left_hand_gesture is not None:
                

                index_tip = hand_landmarks.landmark[mp_hands.HandLandmark.INDEX_FINGER_TIP]
                thumb_tip = hand_landmarks.landmark[mp_hands.HandLandmark.THUMB_TIP]
                middle_tip = hand_landmarks.landmark[mp_hands.HandLandmark.MIDDLE_FINGER_TIP]
                
                x_distance = index_tip.x - thumb_tip.x
                y_distance = index_tip.y - middle_tip.y


                if left_hand_gesture == 1:  # 应用切换
                    
                    if x_distance > 0.1:
                        pyautogui.hotkey('alt', 'tab')
                    elif x_distance < -0.1:
                        pyautogui.hotkey('alt', 'shift', 'tab')
                    try:
                        sql = "UPDATE device_usage SET appliance_change	= appliance_change	+ 1 WHERE user_id = %s"
                        now = datetime.now()
                        formatted_time = now.strftime('%Y-%m-%d %H:%M:%S')
                        cursor.execute("INSERT INTO user_activity (user_id, activity, activity_time)VALUES (%s, %s, %s);", (userId,"appliance_change", now))
                        print(userId)
                        cursor.execute(sql, (userId))
                        conn.commit()
                        print("appliance_change更新成功！")
                    except pymysql.MySQLError as e:
                        print(f"資料庫錯誤: {e}")

                elif left_hand_gesture == 2:  # 画图功能
                    new_pos = (int(index_tip.x * drawing_window.image.shape[1]), int(index_tip.y * drawing_window.image.shape[0]))
                    drawing_window.draw(frame, new_pos)
                    
                    try:
                        sql = "UPDATE device_usage SET drawing_gesture_count = drawing_gesture_count + 1 WHERE user_id = %s"
                        now = datetime.now()
                        formatted_time = now.strftime('%Y-%m-%d %H:%M:%S')
                        cursor.execute("INSERT INTO user_activity (user_id, activity, activity_time)VALUES (%s, %s, %s);", (userId,"drawing_gesture_count", now))
                        cursor.execute(sql, (userId))
                        conn.commit()
                        
                        print("drawing_gesture_count更新成功！")
                    except pymysql.MySQLError as e:
                        print(f"資料庫錯誤: {e}")

                elif left_hand_gesture == 3:  # 音量控制
                    distance = math.sqrt((thumb_tip.x - index_tip.x)**2 + (thumb_tip.y - index_tip.y)**2)
                    if distance > 0.1:
                        pyautogui.press('volumeup', presses=VOLUME_INCREMENT)
                        try:
                            now = datetime.now()
                            formatted_time = now.strftime('%Y-%m-%d %H:%M:%S')
                            cursor.execute("INSERT INTO user_activity (user_id, activity, activity_time)VALUES (%s, %s, %s);", (userId,"volume_increase_gesture_count", now))
                            sql = "UPDATE device_usage SET volume_increase_gesture_count = volume_increase_gesture_count + 1 WHERE user_id = %s"
                            cursor.execute(sql, (userId))
                            conn.commit()
                            print("volume_increase_gesture_count更新成功！")
                        except:
                            print("volume_increase_gesture_count更新錯誤")
                    else:
                        pyautogui.press('volumedown', presses=VOLUME_INCREMENT)
                        try:
                            now = datetime.now()
                            formatted_time = now.strftime('%Y-%m-%d %H:%M:%S')
                            cursor.execute("INSERT INTO user_activity (user_id, activity, activity_time)VALUES (%s, %s, %s);", (userId,"volume_decrease_gesture_count", now))
                            sql = "UPDATE device_usage SET volume_decrease_gesture_count = volume_decrease_gesture_count + 1 WHERE user_id = %s"
                            cursor.execute(sql, (userId))
                            conn.commit()
                            print("volume_decrease_gesture_count更新成功！")
                        except:
                            print("volume_decrease_gesture_count更新錯誤")

                elif left_hand_gesture == 4:  # 音乐控制
                    if x_distance > 0.1:
                        pyautogui.press('nexttrack')
                        try:
                            now = datetime.now()
                            formatted_time = now.strftime('%Y-%m-%d %H:%M:%S')
                            cursor.execute("INSERT INTO user_activity (user_id, activity, activity_time)VALUES (%s, %s, %s);", (userId,"next_music_gesture_count", now))
                            sql = "UPDATE device_usage SET next_music_gesture_count = next_music_gesture_count + 1 WHERE user_id = %s"
                            cursor.execute(sql, (userId))
                            conn.commit()
                            print("next_music_gesture_count更新成功！")
                        except:
                            print("next_music_gesture_count更新錯誤")
                    elif x_distance < -0.1:
                        pyautogui.press('prevtrack')
                        try:
                            now = datetime.now()
                            formatted_time = now.strftime('%Y-%m-%d %H:%M:%S')
                            cursor.execute("INSERT INTO user_activity (user_id, activity, activity_time)VALUES (%s, %s, %s);", (userId,"previous_music_gesture_count", now))
                            sql = "UPDATE device_usage SET previous_music_gesture_count = previous_music_gesture_count + 1 WHERE user_id = %s"
                            cursor.execute(sql, (userId))
                            conn.commit()
                            print("previous_music_gesture_count更新成功！")
                        except:
                            print("previous_music_gesture_count更新錯誤")
                        

                elif left_hand_gesture == 5:  # 网页滚动
                    if y_distance > 0.1:
                        pyautogui.scroll(-SCROLL_STEP)
                        try:
                            now = datetime.now()
                            formatted_time = now.strftime('%Y-%m-%d %H:%M:%S')
                            cursor.execute("INSERT INTO user_activity (user_id, activity, activity_time)VALUES (%s, %s, %s);", (userId,"scroll_up_gesture_count", now))
                            sql = "UPDATE device_usage SET scroll_up_gesture_count = scroll_up_gesture_count + 1 WHERE user_id = %s"
                            cursor.execute(sql, (userId))
                            conn.commit()
                            print("scroll_up_gesture_count更新成功！")
                        except:
                            print("scroll_up_gesture_count更新錯誤")
                    elif y_distance < -0.1:
                        pyautogui.scroll(SCROLL_STEP)
                        try:
                            now = datetime.now()
                            formatted_time = now.strftime('%Y-%m-%d %H:%M:%S')
                            cursor.execute("INSERT INTO user_activity (user_id, activity, activity_time)VALUES (%s, %s, %s);", (userId,"scroll_down_gesture_count", now))
                            sql = "UPDATE device_usage SET scroll_down_gesture_count = scroll_down_gesture_count + 1 WHERE user_id = %s"
                            cursor.execute(sql, (userId))
                            conn.commit()
                            print("scroll_down_gesture_count更新成功！")
                        except:
                            print("scroll_down_gesture_count更新錯誤")

                elif left_hand_gesture == 6:  # 简报翻页
                    if x_distance > 0.1:
                        pyautogui.press('right')
                        current_page += 1
                        try:
                            now = datetime.now()
                            formatted_time = now.strftime('%Y-%m-%d %H:%M:%S')
                            cursor.execute("INSERT INTO user_activity (user_id, activity, activity_time)VALUES (%s, %s, %s);", (userId,"next_slide_gesture_count", now))
                            sql = "UPDATE device_usage SET next_slide_gesture_count = next_slide_gesture_count + 1 WHERE user_id = %s"
                            cursor.execute(sql, (userId))
                            conn.commit()
                            print("next_slide_gesture_count更新成功！")
                        except:
                            print("next_slide_gesture_count更新錯誤")
                    elif x_distance < -0.1:
                        pyautogui.press('left')
                        current_page = max(1, current_page - 1)
                        try:
                            now = datetime.now()
                            formatted_time = now.strftime('%Y-%m-%d %H:%M:%S')
                            cursor.execute("INSERT INTO user_activity (user_id, activity, activity_time)VALUES (%s, %s, %s);", (userId,"previous_slide_gesture_count", now))
                            sql = "UPDATE device_usage SET previous_slide_gesture_count = previous_slide_gesture_count + 1 WHERE user_id = %s"
                            cursor.execute(sql, (userId))
                            conn.commit()
                            print("previous_slide_gesture_count更新成功！")
                        except:
                            print("previous_slide_gesture_count更新錯誤")
                
                elif left_hand_gesture == 7:  # 左手比"7"
                    # 计算新的鼠标位置
                    new_x = np.interp(index_tip.x, (0, 1), (0, wScr))
                    new_y = np.interp(index_tip.y, (0, 1), (0, hScr))
                    pyautogui.moveTo(new_x, new_y)
                    
                    '''
                    1. 左手判斷是否為8
                    2. 右手判斷user輸入的gesture
                    如手勢比出數字 1 對應 gesture = 1 
                    再由gesture找出user所輸入的ir code
                    '''
                elif left_hand_gesture == 9:
                    if right_hand_gesture in irCode:
  
                        address = irCode[right_hand_gesture]["address"]
                        command = irCode[right_hand_gesture]["command"]
                        print(address,command)
                        # 格式化為一個字串，準備傳送
                        message = f"{address}:{command}"
                        
                        # 傳送為 bytes 格式
                        ser.write(bytes(message, 'utf-8'))
                        print("send")
                        time.sleep(0.5)
                        
                        
                    
                

    # 显示手势检测结果
    if left_hand_gesture is not None:
        cv2.putText(frame, f'Left Hand Gesture: {left_hand_gesture}', (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 2)
    if results.multi_handedness:
        cv2.putText(frame, f'X Distance: {x_distance:.2f}', (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 2)
        cv2.putText(frame, f'Y Distance: {y_distance:.2f}', (10, 90), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 2)  # 添加 Y Distance 的显示

    # 显示摄像头画面
    cv2.imshow('Hand Gesture Control', frame)


    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# 释放资源
cap.release()
cv2.destroyAllWindows()
cursor.close()
conn.close()