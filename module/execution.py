import os
import subprocess


class Execution:
    def __init__(self, task_id, command, work_dir, allocated_gpus, log_file, main_dir=None):
        self.task_id = task_id
        self.command = command
        self.work_dir = work_dir
        self.main_dir = main_dir
        self.allocated_gpus = allocated_gpus  # 分配的 GPU 列表
        self.log_file = log_file

    def execute(self):
        try:
            # 设置 CUDA_VISIBLE_DEVICES 环境变量, 指定任务使用的 GPU
            gpus_str = ",".join(map(str, self.allocated_gpus))  # 例如 "0,1"
            os.environ["CUDA_VISIBLE_DEVICES"] = gpus_str
            cwd = os.path.join(self.main_dir, self.work_dir)
            command = f"source ~/.bashrc && {self.command}"
            result = subprocess.run(command, shell=True, check=True, text=True, capture_output=True, cwd=cwd)
            print(result.stdout)
            return result
        except subprocess.CalledProcessError as e:
            return e

if __name__ == '__main__':
    execution = Execution(task_id=1, command="python test.py", work_dir="./task", allocated_gpus=[0], log_file="./log/test.log", main_dir="../")
    execution.execute()