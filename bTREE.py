# 示例应用
import sys
import time
from datetime import datetime, timedelta
from src.MESGLOGGER.Logger import Logger

def main():
    logger = Logger(output_dir="logs", max_chunk_size=1024 * 1024)  # 每个日志分片最大1MB

    # 模拟记录一些日志消息
    for i in range(10):
        message_data = f"Test message {i}".encode('utf-8')
        logger.log(message_data)
        time.sleep(1)

    # 获取当前时间
    now = datetime.now()

    # 获取过去5秒内的日志消息
    start_time = now - timedelta(seconds=5)
    logs = logger.get_logs(start_time)

    # 打印获取到的日志消息
    for log_message in logs:
        print(f"Timestamp: {log_message.timestamp}, Message: {log_message.message_data.decode('utf-8')}")

if __name__ == "__main__":
    main()