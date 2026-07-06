# -*- coding: utf-8 -*-
"""
koreanize_matplotlib 로컬 대체 모듈
설명: 외부 라이브러리 설치 없이 맑은 고딕(Malgun Gothic)을 Matplotlib 기본 한글 폰트로 설정합니다.
"""

import matplotlib.pyplot as plt
import platform

system_os = platform.system()
if system_os == 'Windows':
    font_name = 'Malgun Gothic'
elif system_os == 'Darwin':
    font_name = 'AppleGothic'
else:
    font_name = 'NanumGothic'

# Matplotlib 글로벌 폰트 및 유니버스 마이너스 기호 설정
plt.rcParams['font.family'] = font_name
plt.rcParams['axes.unicode_minus'] = False

print(f"[koreanize_matplotlib] 한글 폰트를 '{font_name}'(으)로 설정 완료했습니다.")
