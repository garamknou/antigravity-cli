# -*- coding: utf-8 -*-
"""
analysis_raw.log 파일에서 SVG 파일과 report.md 보고서를 파싱하여
yes24/ 폴더 바로 아래에 저장(복원)하는 헬퍼 스크립트
"""
import os
import re

def main():
    log_file = "yes24/analysis_raw.log"
    output_dir = "yes24"
    
    if not os.path.exists(log_file):
        print(f"로그 파일을 찾을 수 없습니다: {log_file}")
        return
        
    print(f"[파싱 시작] {log_file} 분석 및 복원을 시작합니다.")
    
    current_file = None
    current_writer = None
    in_report = False
    report_content = []
    
    with open(log_file, "r", encoding="utf-8") as f:
        for line in f:
            # SVG 시작 탐색
            svg_start_match = re.match(r"===SVG_START_(.*)===", line.strip())
            if svg_start_match:
                filename = svg_start_match.group(1)
                filepath = os.path.join(output_dir, filename)
                current_file = filepath
                current_writer = open(filepath, "w", encoding="utf-8")
                print(f"[복원 중] {filename} 작성을 시작합니다.")
                continue
                
            # SVG 종료 탐색
            svg_end_match = re.match(r"===SVG_END_(.*)===", line.strip())
            if svg_end_match:
                if current_writer:
                    current_writer.close()
                    print(f"[복원 완료] {current_file} 저장 완료")
                current_file = None
                current_writer = None
                continue
                
            # 리포트 시작 탐색
            if line.strip() == "===REPORT_START===":
                in_report = True
                print("[복원 중] report.md 작성을 시작합니다.")
                continue
                
            # 리포트 종료 탐색
            if line.strip() == "===REPORT_END===":
                in_report = False
                report_path = os.path.join(output_dir, "report.md")
                with open(report_path, "w", encoding="utf-8") as rf:
                    rf.writelines(report_content)
                print(f"[복원 완료] report.md 저장 완료")
                continue
                
            # 파일 기록 중이면 작성
            if current_writer:
                current_writer.write(line)
            elif in_report:
                report_content.append(line)
                
    print("[파싱 종료] 모든 파일 복원이 완료되었습니다.")

if __name__ == "__main__":
    main()
