import psutil
import time
import os
import requests
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from datetime import datetime

#CONFIGURATIONS
try:
    with open('telegram_token.txt','r') as f:
        TOKEN = f.read().strip()

    with open('telegram_id.txt', 'r') as f:
        CHAT_ID = f.read().strip()
except FileNotFoundError:
    print('[EROOR] Configuration files (telegram_token.txt / telegram_id.txt) not found.')

CPU_THRESHOLD = 80.0
RAM_THRESHOLD = 75.0
ALERT_COOLDOWN = 60
MAX_HISTORY = 3600

cpu_history, ram_history, time_history, disk_history = [], [], [], []
last_cpu_alert, last_ram_alert = 0, 0

#FUNCTIONS
def send_telegram_alert(message):
    '''Sends a notification to the configured Telegram Bot.'''
    url = f'https://api.telegram.org/bot{TOKEN}/sendMessage'
    payload = {
        'chat_id': CHAT_ID,
        'text': message
    }

    try:
        requests.post(url, data=payload, timeout=5)
    except Exception as e:
        print(f'[ERROR] Alert delivery failed: {e}')

def clear_console():
    '''Clears the terminal screen based on the OS.'''
    os.system('cls' if os.name == 'nt' else 'clear')

def log_to_csv(data):
    """Appends system metrics to a persistent CSV file."""
    file_exists = os.path.isfile('system_log.csv')
    with open('system_log.csv', 'a') as f:
        if not file_exists:
            f.write('timestamp,cpu_pct,ram_pct,disk_pct\n')
        f.write(f"{data['time']},{data['cpu']},{data['ram']},{data['disk']}\n")

#MAIN LOOP
try:
    print('>>> Titan Sentinel Service: ACTIVE')
    print('>>> Monitoring system resources. . . Press Ctrl+C to stop.')

    while True:
        cpu = psutil.cpu_percent(interval=1)
        memory = psutil.virtual_memory()

        ram = memory.percent
        total_ram = round(memory.total / (1024**3), 2)
        used_ram = round(memory.used / (1024**3), 2)
        free_ram = round(memory.available / (1024**3), 2)
        disk = psutil.disk_usage('/').percent
        current_time = datetime.now().strftime('%H:%M:%S')

        #Data Persistence
        cpu_history.append(cpu)
        ram_history.append(ram)
        time_history.append(current_time)
        disk_history.append(disk)
        
        #keep history within MAX_HISTORY limit
        if len(cpu_history) > MAX_HISTORY:
            for buffer in [cpu_history, ram_history, time_history, disk_history]:
                buffer.pop(0)

        # Real-time logging
        log_to_csv({'time': current_time, 'cpu': cpu, 'ram': ram, 'disk': disk})

        #UI
        clear_console()
        print('TITAN SENTINEL | STATUS: RUNNING | {current_time}')
        print('-' * 50)
        print(f'CPU: {cpu}%')
        print(f'RAM: {ram}% ({used_ram}GB / {total_ram}GB)')
        print(f'Disk: {disk}%')
        print('-' * 50)
        print(f'CPU_Threshold: {CPU_THRESHOLD}%')
        print(f'RAM_Threshold: {RAM_THRESHOLD}%')

        now = time.time()

        #CPU ALERT
        if cpu > CPU_THRESHOLD and (now - last_cpu_alert > ALERT_COOLDOWN):
            send_telegram_alert(f' CPU ALERT\nValue: {cpu}%\nTime: {current_time}')
            last_cpu_alert = now

        if ram > RAM_THRESHOLD and (now - last_ram_alert > ALERT_COOLDOWN):
            send_telegram_alert(f' RAM ALERT\nValue: {ram}%\nTime: {current_time}')
            last_ram_alert = now

except KeyboardInterrupt:
    print('\n[!] Shutting down Sentinel')

    if cpu_history:
        print('>>> Generating performance report...')
        plt.figure(figsize=(10, 6))

    # Metrics plotting
        plt.plot(cpu_history, label='CPU Usage %', color='#3498db', linewidth=1.5)
        plt.plot(ram_history, label='RAM Usage %', color='#e67e22', linewidth=1.5)
        
        # Static Threshold Lines
        plt.axhline(y=CPU_THRESHOLD, color='red', linestyle='--', alpha=0.5, label='CPU Threshold')
        plt.axhline(y=RAM_THRESHOLD, color='darkred', linestyle='--', alpha=0.5, label='RAM Threshold')

  
        plt.title('System Performance Analysis: Titan Sentinel', fontsize=14)
        plt.xlabel('Sampling Points (seconds)')
        plt.ylabel('Percentage (%)')
        plt.ylim(0, 105) 
        plt.legend(loc='upper right')
        plt.grid(True, linestyle=':', alpha=0.6)
        
        plt.savefig('system_report.png')
        print('>>> Report saved: system_report.png')
    
    print('>>> Logs persisted in system_log.csv')
    print('>>> Exit complete.')
    








        
