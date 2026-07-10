import os
import sys
import tempfile

print("Python version:", sys.version)

# 기존에 존재하는 워크스페이스 내 scratch/tmp 디렉토리 사용 (makedirs 생략)
agent_temp = os.path.abspath("scratch/tmp")
print("Target directory:", agent_temp)

# 1. 일반 파일 쓰기 테스트
test_path = os.path.join(agent_temp, "test_write.txt")
try:
    with open(test_path, "w", encoding="utf-8") as f:
        f.write("Hello World")
    print(f"일반 파일 쓰기 성공: {test_path}")
    if os.path.exists(test_path):
        os.remove(test_path)
except Exception as e:
    print(f"일반 파일 쓰기 실패: {e}")

# 2. 환경변수 및 tempfile 설정
os.environ['TEMP'] = agent_temp
os.environ['TMP'] = agent_temp
tempfile.tempdir = agent_temp

try:
    tfile = tempfile.mktemp(prefix="playwright_")
    print(f"tempfile.mktemp() 성공: {tfile}")
except Exception as e:
    print(f"tempfile.mktemp() 실패: {e}")
