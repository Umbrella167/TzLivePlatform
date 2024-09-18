import os
import pickle
from datetime import datetime
from pympler import asizeof
import bisect

##213213231232
class Logger:
    def __init__(self, output_dir="logs"):
        self.output_dir = output_dir
        now = datetime.now()
        if not os.path.exists(output_dir):
            os.mkdir(output_dir)
        self.log_pack_dir = (
            now.strftime("Rec_%Y-%m-%d_%H-%M-%S-") + f"{now.microsecond}"
        )
        self.log_file_path = os.path.join(self.output_dir, self.log_pack_dir)
        if not os.path.exists(self.log_file_path):
            os.mkdir(self.log_file_path)
        # 日志列表
        self.log_list = []
        # 文件大小
        self.file_size = 0
        # 当前文件索引
        self.current_file_index = 0
        # 消息索引
        self.msg_index = 0
        # 消息总数
        self.msg_count = 0
        # 文件结束时间戳
        self.file_end_timestamp = 0

    def save_to_disk(self):
        file_name = f"{self.current_file_index}_{self.file_end_timestamp}.log"
        file_path = os.path.join(self.log_file_path, file_name)
        with open(file_path, "wb") as f:
            pickle.dump(self.log_list, f)
        self.log_list.clear()  # 清空日志列表
        self.msg_index = 0
        self.file_size = 0
        self.current_file_index += 1

    def log(self, log_message, timestamp, chunking_size_mb=1):

        # 创建单条数据
        data_dict = {
            "index": self.msg_index,
            "count": self.msg_count,
            "timestamp": timestamp,
            "message": log_message,
        }

        # 更新消息索引
        self.msg_index += 1
        self.msg_count += 1

        # 计算文件大小
        self.file_size += asizeof.asizeof(data_dict) / (1024 * 1024)

        # 添加到日志列表
        self.log_list.append(data_dict)

        # 记录末尾时间戳
        self.file_end_timestamp = timestamp

        # 存储日志到磁盘
        if self.file_size > chunking_size_mb:
            self.save_to_disk()
            
            


class LogPlayer:
    def __init__(self, logger: Logger):
        self._logger = logger
        self.log_dir = self._logger.log_file_path
        # 排序后的日志文件列表
        self.sorted_filenames = None

        # 当前选中的时间戳对应的文件
        self.select_file = None

        # 当前选中的时间戳对应的信息
        self.now_msg = None

    def read_log_file(self, file_path):
        with open(file_path, "rb") as f:
            log_list = pickle.load(f)
        return log_list

    def list_log_file(self, directory_path):
        try:
            # 使用 os.listdir() 方法列出目录中的所有文件和文件夹
            log_file = os.listdir(directory_path)
            return log_file
        except Exception as e:
            print(f"An error occurred: {e}")
            return []

    def read_log_msg(self, timestamp):
        # 获取日志文件列表
        log_file = self.list_log_file(self.log_dir)

        # 如果没有日志文件，则到内存中寻找最接近的日志
        if not log_file:
            closest_msg = self.get_closest_msg(self._logger.log_list, timestamp)
            self.now_msg = closest_msg
            return closest_msg

        # 根据索引排序文件
        sorted_filenames = sorted(log_file, key=lambda x: int(x.split("_")[0]))
        self.sorted_filenames = sorted_filenames

        # 检查最后一个文件的时间戳是否早于给定的时间戳
        last_file_end_timestamp = int(sorted_filenames[-1].split("_")[1].split(".")[0])
        if last_file_end_timestamp < timestamp:
            return self.get_closest_msg(self._logger.log_list, timestamp)

        # 查找包含指定时间戳的文件
        for filename in sorted_filenames:
            file_end_timestamp = int(filename.split("_")[1].split(".")[0])
            if file_end_timestamp >= timestamp:
                self.select_file = filename
                break

        if not self.select_file:
            return None

        # 读取日志文件中的内容
        file_path = os.path.join(self.log_dir, self.select_file)
        log_list = self.read_log_file(file_path)

        return self.get_closest_msg(log_list, timestamp)

    def get_last_msg(self):
        return self._logger.log_list[-1]

    def get_closest_msg(self, log_list, timestamp):
        if not log_list:
            return None

        timestamps = [msg["timestamp"] for msg in log_list]

        pos = bisect.bisect_left(timestamps, timestamp)

        if pos == 0:
            closest_msg = log_list[0]
        elif pos == len(timestamps):
            closest_msg = log_list[-1]
        else:
            before = timestamps[pos - 1]
            after = timestamps[pos]
            if after - timestamp < timestamp - before:
                closest_msg = log_list[pos]
            else:
                closest_msg = log_list[pos - 1]
        self.now_msg = closest_msg
        return closest_msg

    def get_next_msg(self):
        if self.now_msg is None:
            return None

        log_file = self.list_log_file(self.log_dir)
        msg_index = self.now_msg["index"]
        msg_timestamp = self.now_msg["timestamp"]

        if not log_file:
            # 内存中日志列表为空，则直接返回当前消息
            len_list = self._logger.log_list[-1]["index"]
            msg_index = min(msg_index + 1, len_list)
            self.now_msg = self._logger.log_list[msg_index]
            return self.now_msg

        # 排序文件名
        self.sorted_filenames = sorted(log_file, key=lambda x: int(x.split("_")[0]))
        last_file_end_timestamp = int(
            self.sorted_filenames[-1].split("_")[1].split(".")[0]
        )

        if last_file_end_timestamp < msg_timestamp:
            # 如果最后一个文件的时间戳小于当前消息的时间戳，则从内存中获取下一个消息
            len_list = self._logger.log_list[-1]["index"]
            msg_index = min(msg_index + 1, len_list)
            self.now_msg = self._logger.log_list[msg_index]
            self.select_file = None
            return self.now_msg

        # 找到包含当前时间戳的文件
        for filename in self.sorted_filenames:
            file_end_timestamp = int(filename.split("_")[1].split(".")[0])
            if file_end_timestamp >= msg_timestamp:
                self.select_file = filename
                break

        # 读取文件中的日志
        file_path = os.path.join(self.log_dir, self.select_file)
        log_list = self.read_log_file(file_path)

        if msg_index + 1 < len(log_list):
            # 获取下一个消息
            self.now_msg = log_list[msg_index + 1]
        else:
            # 如果当前文件已经读完，切换到下一个文件
            if self.select_file == self.sorted_filenames[-1]:
                # 如果是最后一个文件，则循环回到内存中的第一个消息
                self.select_file = None
                if self._logger.log_list:
                    self.now_msg = self._logger.log_list[0]
            else:
                # 切换到下一个文件
                file_index = int(self.select_file.split("_")[0]) + 1
                self.select_file = self.sorted_filenames[file_index]
                file_path = os.path.join(self.log_dir, self.select_file)
                log_list = self.read_log_file(file_path)
                self.now_msg = log_list[0]

        return self.now_msg

    def get_previous_msg(self):
        if self.now_msg is None:
            return None

        log_file = self.list_log_file(self.log_dir)
        msg_index = self.now_msg["index"]
        msg_timestamp = self.now_msg["timestamp"]

        if not log_file:
            # If there are no log files on disk, navigate through the in-memory log list
            if msg_index > 0:
                self.now_msg = self._logger.log_list[msg_index - 1]
            else:
                # If we're at the start of the in-memory log list, return the first message
                self.now_msg = self._logger.log_list[0]
            return self.now_msg

        # Sort the filenames by index
        self.sorted_filenames = sorted(log_file, key=lambda x: int(x.split("_")[0]))

        # If the current message is from in-memory logs and there's a previous message available
        if msg_timestamp > int(self.sorted_filenames[-1].split("_")[1].split(".")[0]):
            if msg_index > 0:
                self.now_msg = self._logger.log_list[msg_index - 1]
            else:
                self.now_msg = self._logger.log_list[0]
            self.select_file = None
            return self.now_msg

        # Find the file containing the current timestamp
        for filename in self.sorted_filenames:
            file_end_timestamp = int(filename.split("_")[1].split(".")[0])
            if file_end_timestamp >= msg_timestamp:
                self.select_file = filename
                break

        # Read logs from the selected file
        file_path = os.path.join(self.log_dir, self.select_file)
        log_list = self.read_log_file(file_path)

        if msg_index > 0:
            # Get the previous message within the same file
            self.now_msg = log_list[msg_index - 1]
        else:
            # If we're at the start of the current file, move to the previous file
            file_index = int(self.select_file.split("_")[0]) - 1
            if file_index >= 0:
                self.select_file = self.sorted_filenames[file_index]
                file_path = os.path.join(self.log_dir, self.select_file)
                log_list = self.read_log_file(file_path)
                self.now_msg = log_list[-1]  # Get the last message of the previous file
            else:
                # If we're at the first file, return the first message
                self.now_msg = log_list[0]

        return self.now_msg
log = Logger()
logPlayer = LogPlayer(log)
