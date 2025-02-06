import os
import subprocess

import yaml

yaml_path = "./batch_serving_schedule.yaml"
with open(yaml_path, "r") as file:
    config = yaml.safe_load(file)

cron_time = config["schedule"]
run_file_relative_path = config["run_file_path"]
python_relative_path = config["python_path"]

# 상대 경로로 입력 받은 경로를 절대경로로 바꿔준다
run_file_absolute_path = os.path.abspath(run_file_relative_path)
python_absolute_path = os.path.abspath(python_relative_path)

# 크론탭에 새 작업 추가
update_command = f'echo "{cron_time} {python_absolute_path} {run_file_absolute_path}" | crontab -'
subprocess.run(update_command, shell=True, check=True)
print("-" * 25)
print(
    f"Crontab updated:\nUpdated Cron Expression: {cron_time}\nPython Path: {python_absolute_path}\nFile Path: {run_file_absolute_path}"
)
print("-" * 25)
