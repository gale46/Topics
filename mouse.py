import cv2
import mediapipe as mp
import pyautogui
import time

# 初始化MediaPipe手勢檢測
mp_hands = mp.solutions.hands
hands = mp_hands.Hands(max_num_hands=1)  # 設定只檢測一隻手

# 設定螢幕的寬度和高度以進行滑鼠移動
screen_width, screen_height = pyautogui.size()

# 開啟攝像頭，並進行初始化
cap = cv2.VideoCapture(0)
time.sleep(2)  # 等待攝像頭初始化

def is_finger_bent(tip, pip):
    """ 判斷手指是否彎曲，TIP 是否位於 PIP 下方 """
    return tip.y > pip.y  # 如果 TIP 的 y 座標大於 PIP，手指被視為彎曲

while True:
    success, image = cap.read()  # 讀取攝像頭影像
    if not success:
        break  # 如果讀取失敗，退出迴圈

    # 將影像轉換為RGB格式，因為MediaPipe需要RGB格式
    image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    results = hands.process(image_rgb)  # 執行手勢檢測

    if results.multi_hand_landmarks:
        for hand_landmarks in results.multi_hand_landmarks:
            # 提取手指節點的座標
            thumb_tip = hand_landmarks.landmark[mp_hands.HandLandmark.THUMB_TIP]  # 姆指末端座標
            index_finger_tip = hand_landmarks.landmark[mp_hands.HandLandmark.INDEX_FINGER_TIP]  # 食指末端座標
            index_finger_pip = hand_landmarks.landmark[mp_hands.HandLandmark.INDEX_FINGER_PIP]  # 食指近端關節
            middle_finger_tip = hand_landmarks.landmark[mp_hands.HandLandmark.MIDDLE_FINGER_TIP]  # 中指末端座標
            middle_finger_pip = hand_landmarks.landmark[mp_hands.HandLandmark.MIDDLE_FINGER_PIP]  # 中指近端關節

            # 計算食指的座標轉換到螢幕上的位置，用於移動滑鼠
            x = int(index_finger_tip.x * screen_width)
            y = int(index_finger_tip.y * screen_height)

            # 滑鼠移動到食指的座標位置
            pyautogui.moveTo(x, y)

            # 設定食指和中指的顏色
            index_color = (0, 255, 0)  # 預設為綠色
            middle_color = (0, 255, 0)  # 預設為綠色

            # 判斷食指是否彎曲，彎曲則按下左鍵
            if is_finger_bent(index_finger_tip, index_finger_pip):
                pyautogui.mouseDown()  # 按下滑鼠左鍵
                pyautogui.mouseUp()
                index_color = (0, 0, 255)  # 左鍵按下時，食指變紅色
            else:
                pyautogui.mouseUp()  # 釋放滑鼠左鍵

            # 判斷中指是否彎曲，彎曲則按下右鍵
            if is_finger_bent(middle_finger_tip, middle_finger_pip):
                pyautogui.rightClick()  # 右鍵點擊
                middle_color = (0, 0, 255)  # 右鍵按下時，中指變紅色

            # 根據手指節點的顏色來進行繪製
            for idx, landmark in enumerate(hand_landmarks.landmark):
                h, w, _ = image.shape
                cx, cy = int(landmark.x * w), int(landmark.y * h)

                if idx == mp_hands.HandLandmark.INDEX_FINGER_TIP:  # 食指
                    color = index_color
                elif idx == mp_hands.HandLandmark.MIDDLE_FINGER_TIP:  # 中指
                    color = middle_color
                else:
                    color = (0, 255, 0)  # 其他節點保持綠色

                # 繪製節點
                cv2.circle(image, (cx, cy), 10, color, cv2.FILLED)

            # 繪製手部連接線
            mp.solutions.drawing_utils.draw_landmarks(image, hand_landmarks, mp_hands.HAND_CONNECTIONS)

    # 顯示影像
    cv2.imshow("MediaPipe Hand Tracking", image)

    # 按下 'q' 鍵退出程式
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# 釋放資源
cap.release()
cv2.destroyAllWindows()
