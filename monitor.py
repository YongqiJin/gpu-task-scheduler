from flask import Flask, render_template, jsonify
import csv
import subprocess
import pandas as pd

app = Flask(__name__)

tasks = []

def get_gpu_status(memory_threshold=50, utilization_threshold=20):
    """使用 nvidia-smi 查询 GPU 实际状态"""
    result = subprocess.run(['nvidia-smi', '--query-gpu=index,name,utilization.gpu,memory.used,memory.total', '--format=csv,noheader,nounits'],
                            stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    gpu_status = result.stdout.decode('utf-8').strip().split('\n')
    gpu_info = pd.DataFrame(columns=['id', 'gpu_utilization(%)', 'memory_used(MB)', 'memory_total(MB)', 'is_running'])

    for i, gpu in enumerate(gpu_status):
        info = gpu.split(', ')
        gpu_info.loc[i] = {
            'id': int(info[0]),
            'gpu_utilization(%)': int(info[2]),
            'memory_used(MB)': int(info[3]),
            'memory_total(MB)': int(info[4]),
            'is_running': int(info[2]) > utilization_threshold or int(info[3]) / int(info[4]) > memory_threshold
        }
    return gpu_info

# 读取任务队列函数
def read_queue(queue_file):
    global tasks
    tasks = []
    with open(queue_file, newline='') as csvfile:
        reader = csv.reader(csvfile)
        next(reader, None)  # 跳过表头
        for row in reader:
            if row:  # 忽略空行
                task_id, task_name, command, work_dir, n_gpus, execution, notify, status, allocated_gpus, start_time, end_time = row
                task_id, task_name, command, work_dir, n_gpus, execution, notify, status, allocated_gpus, start_time, end_time = row
                tasks.append({
                    'task_id': task_id,
                    'task_name': task_name,
                    'command': command,
                    'work_dir': work_dir,
                    'n_gpus': int(n_gpus),
                    'execution': execution,
                    'notify': notify,
                    'status': status,
                    'allocated_gpus': allocated_gpus,
                    'start_time': start_time,
                    'end_time': end_time,
                })

# 路由渲染任务数据
@app.route('/', methods=['GET'])
def get_tasks(queue_file="./queue.csv"):
    read_queue(queue_file)  # 每次请求更新任务状态
    gpu_status = get_gpu_status()  # 获取当前 GPU 状态
    return render_template('monitor.html', tasks=tasks, gpu_status=gpu_status)

# 新增路由提供任务队列和GPU状态数据
@app.route('/update_data', methods=['GET'])
def update_data(queue_file="./queue.csv"):
    read_queue(queue_file)  # 每次请求更新任务状态
    gpu_status = get_gpu_status()  # 获取当前 GPU 状态
    data = {
        "tasks": tasks,
        "gpu_status": gpu_status.to_dict(orient='records')
    }
    return jsonify(data)

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000)