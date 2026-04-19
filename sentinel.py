import psutil
import time
import os
import requests
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from datetime import datetime

# ================= CONFIG =================
CPU_THRESHOLD = 80.0
RAM_THRESHOLD = 75.0
DISK_THRESHOLD = 85.0
ALERT_COOLDOWN = 60
MAX_HISTORY = 3600

cpu_history, ram_history, disk_history, time_history = [], [], [], []
last_cpu_alert, last_ram_alert = 0, 0

TOKEN = None
CHAT_ID = None

# Load Telegram config safely
try:
    with open('telegram_token.txt','r') as f:
        TOKEN = f.read().strip()

    with open('telegram_id.txt', 'r') as f:
        CHAT_ID = f.read().strip()
except FileNotFoundError:
    print('[WARNING] Telegram config not found. Alerts disabled.')

# ================= FUNCTIONS =================
def send_telegram_alert(message):
    """Send alert to Telegram (if configured)"""
    if not TOKEN or not CHAT_ID:
        return

    url = f'https://api.telegram.org/bot{TOKEN}/sendMessage'
    payload = {
        'chat_id': CHAT_ID,
        'text': message
    }

    try:
        requests.post(url, data=payload, timeout=5)
    except Exception as e:
        print(f'[ERROR] Alert failed: {e}')

def clear_console():
    """Better screen clear (no flicker)"""
    print("\033c", end="")

def log_to_csv(data):
    """Save metrics persistently"""
    file_exists = os.path.isfile('system_log.csv')

    with open('system_log.csv', 'a') as f:
        if not file_exists:
            f.write('timestamp,cpu_pct,ram_pct,disk_pct\n')

        f.write(f"{data['time']},{data['cpu']},{data['ram']},{data['disk']}\n")

def get_metrics():
    """Collect system metrics"""
    cpu = psutil.cpu_percent(interval=1)
    memory = psutil.virtual_memory()
    disk = psutil.disk_usage('/')

    return {
        'cpu': cpu,
        'ram': memory.percent,
        'disk': disk.percent,
        'used_ram': round(memory.used / (1024**3), 2),
        'total_ram': round(memory.total / (1024**3), 2)
    }

# ================= MAIN LOOP =================
try:
    print('>>> Titan Sentinel Service: ACTIVE')
    print('>>> Monitoring system resources... Press Ctrl+C to stop.')

    while True:
        metrics = get_metrics()
        current_time = datetime.now().strftime('%H:%M:%S')

        cpu = metrics['cpu']
        ram = metrics['ram']
        disk = metrics['disk']
        used_ram = metrics['used_ram']
        total_ram = metrics['total_ram']

        # Store history
        cpu_history.append(cpu)
        ram_history.append(ram)
        disk_history.append(disk)
        time_history.append(current_time)

        # Limit memory usage
        if len(cpu_history) > MAX_HISTORY:
            for buffer in [cpu_history, ram_history, disk_history, time_history]:
                buffer.pop(0)

        # Save log
        log_to_csv({
            'time': current_time,
            'cpu': cpu,
            'ram': ram,
            'disk': disk
        })

        # UI
        clear_console()
        print(f'TITAN SENTINEL | STATUS: RUNNING | {current_time}')
        print('-' * 50)
        print(f'CPU:  {cpu}%')
        print(f'RAM:  {ram}% ({used_ram}GB / {total_ram}GB)')
        print(f'Disk: {disk}%')
        print('-' * 50)
        print(f'CPU Threshold:  {CPU_THRESHOLD}%')
        print(f'RAM Threshold:  {RAM_THRESHOLD}%')
        print(f'Disk Threshold: {DISK_THRESHOLD}%')

        now = time.time()

        # CPU ALERT
        if cpu > CPU_THRESHOLD and (now - last_cpu_alert > ALERT_COOLDOWN):
            send_telegram_alert(f'🚨 CPU ALERT\nValue: {cpu}%\nTime: {current_time}')
            last_cpu_alert = now

        # RAM ALERT
        if ram > RAM_THRESHOLD and (now - last_ram_alert > ALERT_COOLDOWN):
            send_telegram_alert(f'🚨 RAM ALERT\nValue: {ram}%\nTime: {current_time}')
            last_ram_alert = now

except KeyboardInterrupt:
    print('\n[!] Shutting down Titan Sentinel...')

    if cpu_history:
        print('>>> Generating performance report...')

        plt.figure(figsize=(10, 6))

        # Data lines
        plt.plot(cpu_history, label='CPU %', linewidth=1.5)
        plt.plot(ram_history, label='RAM %', linewidth=1.5)
        plt.plot(disk_history, label='Disk %', linewidth=1.5)

        # Threshold lines
        plt.axhline(y=CPU_THRESHOLD, linestyle='--', alpha=0.6, label='CPU Threshold')
        plt.axhline(y=RAM_THRESHOLD, linestyle='--', alpha=0.6, label='RAM Threshold')
        plt.axhline(y=DISK_THRESHOLD, linestyle='--', alpha=0.6, label='Disk Threshold')

        # Labels
        plt.title('Titan Sentinel | System Performance Report')
        plt.xlabel('Time (seconds)')
        plt.ylabel('Usage %')
        plt.ylim(0, 105)
        plt.legend()
        plt.grid(True, linestyle=':', alpha=0.6)

        plt.savefig('system_report.png')
        print('>>> Report saved: system_report.png')

    print('>>> Logs saved: system_log.csv')
    print('>>> Shutdown complete.')







        
