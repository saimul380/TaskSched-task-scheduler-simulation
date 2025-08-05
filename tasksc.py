import threading
import time
import random
import queue
import matplotlib.pyplot as plt
from collections import defaultdict

# Task definition
class Task:
    def __init__(self, name, burst_time, priority):
        self.name = name
        self.burst_time = burst_time
        self.priority = priority
        self.arrival_time = time.time()

    def __repr__(self):
        return f"{self.name}(BT={self.burst_time}, P={self.priority})"

# Shared log for Gantt chart
execution_log = []
log_lock = threading.Lock()

# Systems and Queues
systems = {
    'airport': {'queue': queue.PriorityQueue(), 'algo': 'priority', 'icon': '✈️'},
    'bus': {'queue': queue.Queue(), 'algo': 'fcfs', 'icon': '🚌'},
    'amusement': {'queue': [], 'algo': 'rr', 'icon': '🎢', 'quantum': 3},
    'ride': {'queue': [], 'algo': 'sjf', 'icon': '🚗'}
}

# Helper function: log execution
def log_task_execution(system, task, start_time, duration):
    with log_lock:
        execution_log.append({
            'System': system,
            'Task': task.name,
            'Start': start_time,
            'Duration': duration
        })

# Dispatcher: generate tasks randomly
def dispatcher(stop_event):
    names = ['AI999', 'BG321', 'EK202', 'Bus 102', 'Bus 77', 'Ride A', 'Ride C', 'Visitor Anna', 'Visitor Lee']
    while not stop_event.is_set():
        system = random.choice(list(systems.keys()))
        name = random.choice(names)
        task = Task(
            name=f"{name}#{random.randint(1, 100)}",
            burst_time=random.randint(2, 6),
            priority=random.randint(1, 5)
        )

        if systems[system]['algo'] == 'priority':
            systems[system]['queue'].put((task.priority, time.time(), task))
        elif systems[system]['algo'] == 'fcfs':
            systems[system]['queue'].put(task)
        else:
            systems[system]['queue'].append(task)

        print(f"[New Task] {task.name}(BT={task.burst_time}, P={task.priority}) added to {system}")
        time.sleep(random.uniform(0.5, 1.5))

# System Handlers
def airport_handler(stop_event):
    while not stop_event.is_set():
        if not systems['airport']['queue'].empty():
            _, _, task = systems['airport']['queue'].get()
            print(f"[Airport {systems['airport']['icon']}] Handling {task}")
            start = time.time()
            time.sleep(task.burst_time)
            log_task_execution('Airport', task, start, task.burst_time)

def bus_handler(stop_event):
    while not stop_event.is_set():
        if not systems['bus']['queue'].empty():
            task = systems['bus']['queue'].get()
            print(f"[Bus Stop {systems['bus']['icon']}] Departing {task}")
            start = time.time()
            time.sleep(task.burst_time)
            log_task_execution('Bus', task, start, task.burst_time)

def amusement_handler(stop_event):
    while not stop_event.is_set():
        if systems['amusement']['queue']:
            task = systems['amusement']['queue'].pop(0)
            quantum = systems['amusement']['quantum']
            time_to_run = min(task.burst_time, quantum)
            print(f"[Amusement Park {systems['amusement']['icon']}] Running {task.name} for {time_to_run} units")
            start = time.time()
            time.sleep(time_to_run)
            log_task_execution('Amusement', task, start, time_to_run)
            task.burst_time -= time_to_run
            if task.burst_time > 0:
                systems['amusement']['queue'].append(task)

def ride_handler(stop_event):
    while not stop_event.is_set():
        if systems['ride']['queue']:
            systems['ride']['queue'].sort(key=lambda t: t.burst_time)
            task = systems['ride']['queue'].pop(0)
            print(f"[Ride Share {systems['ride']['icon']}] Serving {task}")
            start = time.time()
            time.sleep(task.burst_time)
            log_task_execution('Ride Share', task, start, task.burst_time)

# Gantt Chart Function
def show_gantt_chart():
    color_map = {
        'Airport': 'skyblue',
        'Bus': 'lightgreen',
        'Amusement': 'gold',
        'Ride Share': 'salmon'
    }

    fig, ax = plt.subplots(figsize=(12, 6))
    start_time = min(log['Start'] for log in execution_log)

    for i, log in enumerate(execution_log):
        relative_start = log['Start'] - start_time
        ax.barh(log['Task'], log['Duration'], left=relative_start, color=color_map[log['System']], edgecolor='black')
        ax.text(relative_start + log['Duration']/2, i, log['Task'], va='center', ha='center', fontsize=7, color='black')

    ax.set_xlabel("Time (seconds)")
    ax.set_title("TaskSched Execution Timeline")
    plt.tight_layout()
    plt.show()

# Main Runner
def run_system():
    stop_event = threading.Event()

    threads = [
        threading.Thread(target=dispatcher, args=(stop_event,)),
        threading.Thread(target=airport_handler, args=(stop_event,)),
        threading.Thread(target=bus_handler, args=(stop_event,)),
        threading.Thread(target=amusement_handler, args=(stop_event,)),
        threading.Thread(target=ride_handler, args=(stop_event,))
    ]

    for t in threads:
        t.start()

    # Let it run for 30 seconds
    try:
        time.sleep(30)
    finally:
        stop_event.set()
        for t in threads:
            t.join()
        print("✅ Execution finished. Generating Gantt chart...")
        show_gantt_chart()

# Run everything
if __name__ == "__main__":
    run_system()
