import subprocess
import pandas as pd

class GPUManager:
    def __init__(self, total_gpus):
        self.total_gpus = total_gpus
        self.gpus_allocation = [0] * self.total_gpus  # 0 表示未分配, 1 表示已分配
        self.gpus_status = [0] * self.total_gpus  # 0 表示空闲, 1 表示被占用
        self.update_gpu_status()  # 更新 GPU 状态

    def update_gpu_status(self):
        """查询并更新 GPU 实际空闲状态"""
        gpu_info = self.get_gpu_status()
        for i in range(self.total_gpus):
            if gpu_info.loc[i, 'is_running']:
                self.gpus_status[i] = 1
            else:
                self.gpus_status[i] = 0
    
    def get_gpu_status(self, meomory_threshold=50, utilization_threshold=20):
        """使用 nvidia-smi 查询 GPU 实际状态"""
        result = subprocess.run(['nvidia-smi', '--query-gpu=index,name,utilization.gpu,memory.used,memory.total', '--format=csv,noheader,nounits'],
                                stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        gpu_status = result.stdout.decode('utf-8').strip().split('\n')
        gpu_info = pd.DataFrame(columns=['id', 'gpu_utilization(%)', 'memory_used(MB)', 'memory_total(MB)', 'is_running', 'allocated'])
        for i, gpu in enumerate(gpu_status):
            info = gpu.split(', ')
            gpu_info.loc[i] = {
                'id': int(info[0]),
                'gpu_utilization(%)': int(info[2]),
                'memory_used(MB)': int(info[3]),
                'memory_total(MB)': int(info[4]),
                'is_running': int(info[2]) > utilization_threshold or int(info[3]) / int(info[4]) > meomory_threshold,
                'allocated': self.gpus_allocation[i],
            }
        return gpu_info

    def allocate_gpus(self, n_gpus):
        """分配 GPU, 如果有足够空闲 GPU, 则分配"""
        gpus_free = [(a==0 and b==0) for a, b in zip(self.gpus_allocation, self.gpus_status)]
        if sum(gpus_free) >= n_gpus:
            allocated_gpus = []
            for i in range(self.total_gpus):
                if n_gpus == 0:
                    break
                if gpus_free[i]:  # 如果 GPU 空闲
                    self.gpus_allocation[i] = 1  # 占用 GPU
                    allocated_gpus.append(i)
                    n_gpus -= 1
            return allocated_gpus
        else:
            return None

    def release_gpus(self, allocated_gpus):
        """释放 GPU"""
        for gpu in allocated_gpus:
            self.gpus_allocation[gpu] = 0  # 释放 GPU
        return len(allocated_gpus)
    
    def get_info(self):
        return {
            'total_gpus': self.total_gpus,
            'gpus_allocation': self.gpus_allocation,
            'gpus_status': self.gpus_status
        }


if __name__ == '__main__':
    gpu_manager = GPUManager(total_gpus=4)
    print(gpu_manager.get_info())
    # 模拟查询 GPU 状态
    print(gpu_manager.get_gpu_status())
    # 模拟 GPU 分配
    gpu_manager.update_gpu_status()
    allocated_gpus = gpu_manager.allocate_gpus(2)
    print(f"Allocated GPUs: {allocated_gpus}")
    print(gpu_manager.get_info())
    # 模拟 GPU 释放
    gpu_manager.release_gpus(allocated_gpus)
    print(gpu_manager.get_info())