from flask import Flask, request, jsonify
import pymysql
from flask_cors import CORS
import serial
import time
app = Flask(__name__)
CORS(app)  

config = {
    'host': 'localhost',  
    'user': 'root',
    'password': '',   
    'database': 'project',
    'port': 3306  
}
#Arduino連接COM5
try:
    ser = serial.Serial('COM5', 9600, timeout=1) 
    time.sleep(2)
except:
    print("error")
try:#access database測試
    conn = pymysql.connect(**config)
    cursor = conn.cursor()
    cursor.execute("SELECT DATABASE();")
    db_name = cursor.fetchone()
    time.sleep(1)
    conn.close()
    cursor.close()
   
except pymysql.MySQLError as e:
    print(f"資料庫錯誤: {e}")
except Exception as e:
    print(f"其他錯誤: {e}")    



#登入後讀取userid並return ir code
@app.route('/get_ir_data', methods=['POST'])
def get_ir_data():
    data = request.get_json()
    userId = data.get('userId')
    print(userId)
    try:
        conn = pymysql.connect(**config)
        cursor = conn.cursor()
        cursor.execute("SELECT ir_code_id, ir_code_name, gesture FROM ir_codes WHERE  user_id=%s", (userId,))#讓php做初始化載入user存入的資料
        result = cursor.fetchall()  
    except pymysql.MySQLError as e:
        print(f"資料庫錯誤: {e}")
    finally:
        cursor.close()
        conn.close()
    return jsonify(result)

#所有按鈕控制
@app.route('/control', methods=['POST'])
def control():
        data = request.get_json()
        action = data.get('action')
        irCode={}
        userId = None
        irId = None
        #若data type為dict表示按下操作的按鈕如"開關"，js則傳送userId, irId
        if isinstance(action, dict):
            userId = int(action['userId'])  
            irId = int(action['irId']) 
            print(userId, irId)
            conn = pymysql.connect(**config)
            cursor = conn.cursor()
            cursor.execute("SELECT ir_code_id, address, command FROM ir_codes WHERE user_id=%s", (userId,))
            result = cursor.fetchall()
            print(result)
            #從資料庫取出
            irCode = {
                ir_code_id: {'address': address, 'command': command}
                for ir_code_id, address, command in result
            }
            print(irCode)
            
        print(type(action))
        response = {'message': ''}
        print("action",action)

        #action == 0啟動arduino接收紅外線
        if action == 0:
            ser.write("receive_ir_data".encode('utf-8'))
            arResponse = ser.readline().decode('utf-8').strip()
            while arResponse != "complete": #讀到"complete"後結束loop
                arResponse = ser.readline().decode('utf-8').strip()
                if ":" in arResponse:
                    index = arResponse.index(":")  
                    print(f"index: {index}")#從serial回傳值中找到":"
                    address = arResponse[:index] #":"前方為address
                    command = arResponse[index + 1:] 
                
            print(f"Address: {address}, Command: {command}")
            return jsonify({'address': address, 'command': command}), 200#回傳至js顯示讀到的ir code
        
        #若action為非0，從irCode之中找到對應id發射紅外線編碼            
        if irId in irCode:
            # 將 address 和 command 轉換為字串格式
            address = irCode[irId]['address']
            command = irCode[irId]['command']
            
            # 格式化為一個字串，準備傳送
            message = f"{address}:{command}"
            
            # 傳送為 bytes 格式
            ser.write(bytes(message, 'utf-8'))
            print(f"發送的資料: {message}")
            response['message'] = '操作成功'
            return jsonify(response), 200
   



#更新IR
@app.route('/update_ir_data', methods=['POST'])
def update_ir_data():
    data = request.get_json()
    item = data.get('item') 
    response = {'message': ''}
    try:
        conn = pymysql.connect(**config)
        cursor = conn.cursor()
        if(len(item)==1):#刪除database的ir code
            print("刪除", item)
            cursor.execute("DELETE FROM ir_codes WHERE ir_code_id=%s;", (item[0],))
        else:#新增database ir code
            print(item)
            cursor.execute(
                "INSERT INTO ir_codes (ir_code_name, gesture, address, command, user_id) VALUES (%s, %s, %s, %s, %s);",
                (item[0], item[1], item[2], item[3], item[4])
            )
    
        conn.commit() 
        response['message'] = '操作成功'
        return jsonify(response), 200
    except pymysql.MySQLError as e:
        print(f"資料庫錯誤: {e}")
        response['message'] = '操作失敗'
        return jsonify(response), 500
    finally:
        cursor.close()
        conn.close()
        
    
if __name__ == '__main__':
    app.run(host='127.0.0.1', port=8082)
ser.close()