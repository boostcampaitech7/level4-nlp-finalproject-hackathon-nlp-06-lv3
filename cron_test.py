#!/usr/bin/env python3
import datetime

# 로그 파일 경로
log_file_path = "/data/ephemeral/level4-nlp-finalproject-hackathon-nlp-06-lv3/cron_test_log.txt"

# 현재 시간 기록
with open(log_file_path, "a") as f:
    f.write(f"Script ran at: {datetime.datetime.now()}\n")
