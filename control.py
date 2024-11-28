from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
import pymysql
import serial
import time
config = {
    'host': 'localhost',  
    'user': 'root',
    'password': '',   
    'database': 'project',
    'port': 3306  
}

irr = [0,1,2,3,4,5]
def receive():
    ser.write(bytes(str(irr[0]), 'utf-8')) 
    response = ser.readline().decode('utf-8').strip()
    while response != "complete": 
        response = ser.readline().decode('utf-8').strip()
        print(response)
    
def turn_on_off():
    ser.write(bytes(str(irr[1]), 'utf-8'))
    print("開關")
    response = ser.readline().decode('utf-8').strip()
    while response != "complete": 
        response = ser.readline().decode('utf-8').strip()
        print(response)
def increase_speed():
    ser.write(bytes(str(irr[2]), 'utf-8'))
    print("增加")
    response = ser.readline().decode('utf-8').strip()
    while response != "complete": 
        response = ser.readline().decode('utf-8').strip()
        print(response)
def decrease_speed():
    ser.write(bytes(str(irr[3]), 'utf-8'))
    print("減少")
    response = ser.readline().decode('utf-8').strip()
    while response != "complete": 
        response = ser.readline().decode('utf-8').strip()
        print(response)

def shake():
    ser.write(bytes(str(irr[4]), 'utf-8'))
    print("擺頭")
    response = ser.readline().decode('utf-8').strip()
    while response != "complete": 
        response = ser.readline().decode('utf-8').strip()
        print(response)
def clear():
    ser.write(bytes(str(irr[5]), 'utf-8'))
    print("清除")

try:
    ser = serial.Serial('COM5', 9600, timeout=1) 
    time.sleep(2)
except Exception as e:
    print("An error occurred:", e)
    
app = Flask(__name__)
CORS(app)  
@app.route('/control', methods=['POST'])  # 修改为 POST 方法
def control():
    data = request.get_json()  # 获取前端发送的 JSON 数据
    action = data.get('action')

    response = {'message': ''}

    if action == 'turn_on_off':
        response['message'] = 'turn_on_off'
        turn_on_off()
        
    elif action == 'shake':
        response['message'] = 'shake'
        try:
            shake()
        except:
            response['message'] = 'error'
    elif action == 'increase_speed':
        response['message'] = 'increase_speed'
        increase_speed()
    elif action == 'decrease_speed':
        decrease_speed()
        response['message'] = 'decrease_speed'
    elif action == 'camera_on':
        response['message'] = 'camara_on'
    elif action == 'camera_off':
        response['message'] = 'camara_off'
    elif action == 'receive':
        response['message'] = 'camara_off'
    else:
        return jsonify({'message': 'Invalid action'}), 400

    return jsonify(response)  # 返回响应数据

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=8081)