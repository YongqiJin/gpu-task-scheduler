import time
import torch

def gpu_task():
    # 确保设备有可用的 GPU
    if torch.cuda.is_available():
        # 创建一个大的随机张量
        tensor = torch.randn(20000, 20000, device='cuda')
        # 执行一些计算
        for _ in range(100):
            tensor = tensor @ tensor
            if torch.cuda.current_stream().query():
                break
        del tensor  # 释放显存
    
def main(during):
    t0 = time.time()
    while time.time() - t0 < during:  # 每个 GPU 的任务最多运行 30 秒
        gpu_task()

if __name__ == "__main__":
    # args
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--during", "-d", type=int, default=30)
    args = parser.parse_args()
    main(args.during)
