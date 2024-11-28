import pymysql
from datetime import datetime, timedelta
import random

# 数据库配置
config = {
    'host': 'localhost',
    'user': 'root',
    'password': '',
    'database': 'project',
    'port': 3306
}

# 定义可能的活动类型及其比例
activity_weights = {
    'appliance_change': 0.15,  # 增加
    'drawing_gesture_count': 0.03,  # 减少
    'volume_increase_gesture_count': 0.075,  # 增加
    'volume_decrease_gesture_count': 0.08,  # 增加
    'next_music_gesture_count': 0.085,  # 减少
    'previous_music_gesture_count': 0.025,  # 减少
    'scroll_up_gesture_count': 0.15,  # 增加
    'scroll_down_gesture_count': 0.18,  # 增加
    'next_slide_gesture_count': 0.125,  # 保持较小
    'previous_slide_gesture_count': 0.04   # 保持较小
}

total_records = 42  # 总记录数

def generate_random_datetime():
    """生成指定范围内的随机时间"""
    start_date = datetime(2024, 11, 24)
    end_date = datetime(2024, 11, 24, 23, 59, 59)  # 设置到当天最后一秒
    
    start_timestamp = int(start_date.timestamp())
    end_timestamp = int(end_date.timestamp())
    
    # 生成随机时间戳
    random_timestamp = random.randint(start_timestamp, end_timestamp)
    
    # 转回 datetime
    return datetime.fromtimestamp(random_timestamp)

try:
    # 在循环外建立连接
    conn = pymysql.connect(**config)
    cursor = conn.cursor()
    
    # 根据权重计算每种活动的记录数量
    activity_counts = {
        activity: int(total_records * weight)
        for activity, weight in activity_weights.items()
    }
    
    # 生成记录
    for activity, count in activity_counts.items():
        for _ in range(count):
            # 生成随机时间
            activity_time = generate_random_datetime()
            
            # 插入数据到 user_activity
            cursor.execute(
                "INSERT INTO user_activity (user_id, activity, activity_time) VALUES (%s, %s, %s);",
                (2, activity, activity_time)
            )
            
            # 更新 device_usage 对应的活动计数
            cursor.execute(f"""
                INSERT INTO device_usage (user_id, {activity})
                VALUES (%s, 1)
                ON DUPLICATE KEY UPDATE {activity} = {activity} + 1;
            """, (2,))
        
        # 每个 activity 提交一次
        conn.commit()
        print(f"Inserted {count} records for activity: {activity}")
    
    print("Successfully inserted all records!")
    
except pymysql.Error as e:
    print(f"Database error: {e}")
except Exception as e:
    print(f"Error: {e}")
finally:
    # 确保关闭连接
    if 'conn' in locals():
        cursor.close()
        conn.close()
        print("\nDatabase connection closed.")
