# GPU Task Scheduler

## Introduction

This is a lightweight GPU task scheduler for a single-node multi-GPU server. 

## Functions

- **Task Queue Management**: Maintains a queue of tasks to be executed, with details such as task ID, command, working directory, number of GPUs required, and execution status. Supports adding, removing, and modifying tasks while the system is running.
- **GPU Resource Allocation**: Dynamically allocates available GPUs to tasks based on their requirements and current GPU utilization.
- **Task Execution**: Executes tasks in the queue, setting the appropriate environment variables for GPU usage.
- **Status Monitoring**: Monitors the status of tasks and GPUs, updating the task queue and logging the execution details.
- **Notification System**: Sends notifications via email upon task completion or failure.
- **Web Interface**: Provides a web interface to view the current task queue and GPU status.

## Usage

### Prerequisites

- Python 3.x
- Required Python packages (install using `pip install -r requirements.txt`)

### Task Queue File

The task queue is managed in a CSV file (`<your_csv_name>.csv`). The file should have the following columns:

```csv
task_id,task_name,command,work_dir,n_gpus,execution,notify,status,allocated_gpus,start_time,end_time
1,Task 1,python test.py -d 30,./task,1,Yes,Yes,,,,
2,Task 2,python test.py -d 20,./task,2,No,No,,,,
3,Task 3,python test.py -d 20,./task,2,Yes,Yes,,,,
```

**Note**: You can add, remove, or modify tasks in the CSV file while the system is running. The system will automatically update the task queue based on the changes.

### Running the Task System
```sh
python system.py -n <your_csv_name> [-m <max_concurrent_tasks> -i <interval>]
```

### Monitoring

The `monitor.py` script provides a web interface to monitor the task queue and GPU status. 
```sh
python monitor.py
```

### Notification

The system sends email notifications using the `smtplib` library. Configure the email settings via environment variables. See `module/notify.py` for details.

## Contribution

Feel free to contribute to this project by forking and creating a pull request with your changes. If you have any questions or suggestions, please open an issue for discussion.
