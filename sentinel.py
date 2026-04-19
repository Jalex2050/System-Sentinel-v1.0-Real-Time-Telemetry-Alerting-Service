import psutil
import time
import os
import requests
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from datetime import datetime

#CONFIGURATIONS
with open('telegram_token.txt','r') as f:
    TOKEN = f.read().strip()

with open('telegram_id.txt', 'r') as f:
    CHAT_ID = f.read().strip()

CPU_THRESHOLD = 80.0
RAM_THRESHOLD = 75.0

ALERT_COOLDOWN = 60
MAX_HISTORY = 3600

cpu_history = []
ram_history = []
time_history = []
disk_history = []

last_cpu_alert = 0
last_ram_alert = 0

#FUNCTIONS
def send_telegram_alert(message):
    '''Send alert via Telegram'''
    url = f'https://api.telegram.org/bot{token}/sendMessage'
    payload = {
        'chat_id': CHAT_ID,
        'text': message
    }

    try:
        request.post(url, data=payload, timeout=5)
    except Exception as e:
        print(f'[ERROR] Network issue: {e}')

def clear_console():
    '''Clear terminar cross-plataform'''
    os.system('cls' if os.name == 'nt' else 'clear')

#MAIN LOOP
try:
    print('Sentinel Service: Active.')
    print('Press Ctrl+C to stop and generate report')

    while True:
        cpu = psutil.cpu_percent(interval=None)
        memory = psutil.virtual_memory()

        ram = memory.percent
        total_ram = round(memory.total / (1024**3), 2)
        used_ram = round(memory.used / (1024**3), 2)
        free_ram = round(memory.available / (1024**3), 2)
        
        disk = psutil.disk_usage('/').percent

        current_time = datetime.now().strftime('%H:%M:%S')

        #Store History
        cpu_history.append(cpu)
        ram_history.append(ram)
        time_history.append(current_time)
        disk_history.append(disk)
        
        if len(cpu_history) > MAX_HISTORY:
            cpu_history.pop(0)
            ram_history.pop(0)
            time_history.pop(0)

        #UI
        clear_console()
        print('TITAN SERVER MONITOR')
        print('-' * 40)
        print(f'Time: {current_time}')
        print(f'CPU: {cpu}%')
        print(f'RAM: {ram}% ({used_ram}GB / {total_ram}GB)')
        print(f'Disk: {disk}%')
        print('-' * 40)
        print(f'CPU_Threshold: {CPU_THRESHOLD}%')
        print(f'RAM_Threshold: {RAM_THRESHOLD}%')

        now = time.time()

        #CPU ALERT
        if cpu > CPU_THRESHOLD:
            if now - last_cpu_alert > ALERT_COOLDOWN:
                send_telegram_alert(f'CPU ALERT\nCPU: {cpu}%\nTime: {current_time}')
                last_cpu_alert = now

        #RAM ALERT
        if ram > RAM_THRESHOLD:
            if now - last_ram_alert > ALERT_COOLDOWN:
                send_telegram_alert(f'RAM ALERT\nRAM: {ram}% ({used_ram}GB / {total_ram}GB) \nTime: {current_time}')
                last_ram_alert = now
                
        time.sleep(1)

except KeyboardInterrupt:
    print('\n[!] Shutting down Sentinel')
    print('Generating performance report. . .')

    #GRAPH
    plt.figure()
    plt.plot(cpu_history, label='CPU %')
    plt.plot(ram_history, label='RAM %')
    plt.plot(disk_history, label='Disk %')

    plt.title('System Performance History')
    plt.xlabel('Time (seconds)')
    plt.ylabel('usage %')
    plt.legend()
    plt.grid(True)

    plt.savefig('system_report.png')

    print("Report saved as 'system_report.png'")

    #save log
    with open('system_log.csv', 'w') as f:
        f.write('time,cpu,ram, disk\n')
        for t, c, r, d in zip(time_history, cpu_history, ram_history, disk_history):
            f.write(f'{t},{c},{r},{d}\n')

    print("Log saved as'system_log.csv'")
    








        
