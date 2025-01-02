import csv
import threading
import time
from datetime import datetime
import GPUtil
import logging
from filelock import FileLock
import subprocess
import pytz

from module.gpu_manager import GPUManager
from module.execution import Execution
from module.log import init_logging

    
class System:
    def __init__(self, queue_file, log_file, main_dir=None, max_concurrent_tasks=8, interval=10, total_gpus=None):
        self.queue_file = queue_file
        self.lock_file = queue_file + ".lock"
        self.log_file = log_file
        self.main_dir = main_dir
        self.max_concurrent_tasks = max_concurrent_tasks
        self.active_tasks = 0
        self.interval = interval
        self.lock = threading.Lock()
        self.total_gpus = len(GPUtil.getGPUs()) if total_gpus is None else total_gpus
        self.gpu_manager = GPUManager(total_gpus=total_gpus)
        init_logging(log_file)
        
    def read_queue(self):
        tasks = []
        with open(self.queue_file, newline='') as csvfile:
            reader = csv.reader(csvfile)
            next(reader, None)  # 跳过表头
            for row in reader:
                if row:  # 忽略空行
                    row = [item.strip() for item in row]
                    task_id, task_name, command, work_dir, n_gpus, execution, notify, status, allocated_gpus, start_time, end_time = row
                    tasks.append({
                        'task_id': task_id,
                        'task_name': task_name,
                        'command': command,
                        'work_dir': work_dir,
                        'n_gpus': int(n_gpus),
                        'notify': notify == 'Yes',
                        'execution': execution == 'Yes',
                        'status': status,
                        'allocated_gpus': allocated_gpus,
                        'end_time': end_time if end_time else None,
                        'start_time': start_time if start_time else None
                    })
        return tasks

    def write_queue(self, tasks=[]):
        with open(self.queue_file, mode='w', newline='') as csvfile:
            writer = csv.writer(csvfile)
            # 写入表头
            writer.writerow(['task_id', 'task_name', 'command', 'work_dir', 'n_gpus', 'execution', 'notify', 'status', 'allocated_gpus', 'start_time', 'end_time'])
            for task in tasks:
                writer.writerow([task['task_id'], task['task_name'], task['command'], task['work_dir'], task['n_gpus'], 
                                'Yes' if task['execution'] else 'No', 'Yes' if task['notify'] else 'No',
                                task['status'], task['allocated_gpus'], task['start_time'], task['end_time']])

    def run_task(self, task_id, command, work_dir, allocated_gpus, notify):
        with self.lock:
            self.active_tasks += 1
            execution = Execution(task_id, command, work_dir, allocated_gpus, log_file=self.log_file, main_dir=self.main_dir)
            gpus_str = ",".join(map(str, allocated_gpus))
            logging.info(f"Allocated on GPUs {gpus_str}", extra={'task_id': task_id})
            thread = threading.Thread(target=self.execute_task, args=(execution, allocated_gpus, task_id, notify))
            thread.start()

    def execute_task(self, execution, allocated_gpus, task_id, notify):
        timezone = pytz.timezone('Asia/Shanghai')
        start_time = datetime.now(timezone).strftime('%Y-%m-%d %H:%M:%S')
        gpus_str = ",".join(map(str, allocated_gpus))
        self.update_task_status(task_id, "Running", gpus_str=gpus_str, start_time=start_time)  # 更新任务状态为Running
        
        logging.info(f"Start on GPUs {gpus_str}", extra={'task_id': task_id})
        result = execution.execute()
        
        end_time = datetime.now(timezone).strftime('%Y-%m-%d %H:%M:%S')
        if isinstance(result, subprocess.CompletedProcess):
            self.update_task_status(task_id, "Succeed", end_time=end_time)  # 更新任务状态为Succeed
            logging.info(f"Completed successfully.", extra={'task_id': task_id})
            if notify:
                pass  # 发送通知 [TODO]
        else:
            self.update_task_status(task_id, "Failed", end_time=end_time)  # 更新任务状态为Failed
            logging.error(f"Failed. Error:\n{result.stderr}", extra={'task_id': task_id})
            if notify:
                pass  # 发送通知 [TODO]
        with self.lock:
            self.active_tasks -= 1
        self.gpu_manager.release_gpus(allocated_gpus)
        logging.info(f"Released GPUs {gpus_str}", extra={'task_id': task_id})

    def update_task_status(self, task_id, status, gpus_str=None, start_time=None, end_time=None):
        tasks = self.read_queue()
        for task in tasks:
            if task['task_id'] == task_id:
                task['status'] = status
                task['allocated_gpus'] = gpus_str if gpus_str else task['allocated_gpus']
                task['start_time'] = start_time if start_time else task['start_time']
                task['end_time'] = end_time if end_time else task['end_time']
                break
        self.write_queue(tasks)

    def start(self):
        while True:
            if self.active_tasks < self.max_concurrent_tasks:
                tasks = self.read_queue()
                task_to_execute = next((task for task in tasks if task['execution'] and task['status'] == ''), None)
                if task_to_execute:
                    task_id = task_to_execute['task_id']
                    command = task_to_execute['command']
                    work_dir = task_to_execute['work_dir']
                    n_gpus = task_to_execute['n_gpus']
                    notify = task_to_execute['notify']
                    allocated_gpus = self.gpu_manager.allocate_gpus(n_gpus)
                    if allocated_gpus:
                        self.run_task(task_id, command, work_dir, allocated_gpus, notify)
            time.sleep(self.interval)  # 每5秒检查一次队列


if __name__ == "__main__":
    name="test"
    total_gpus = len(GPUtil.getGPUs())
    system = System(queue_file=f"./{name}.csv", 
                    log_file=f"./log/{name}.log", 
                    main_dir="/mnt/vepfs/fs_users/yongqi",
                    max_concurrent_tasks=8, 
                    interval=5, 
                    total_gpus=total_gpus)
    system.start()
    