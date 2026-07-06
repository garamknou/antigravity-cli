# -*- coding: utf-8 -*-
import pandas as pd
import os

def preview_data():
    file_path = os.path.join("yes24", "data", "yes24_bestseller.csv")
    if not os.path.exists(file_path):
        print(f"파일을 찾을 수 없습니다: {file_path}")
        return
        
    df = pd.read_csv(file_path, encoding="utf-8-sig")
    
    print("--- 1. 데이터 기본 정보 ---")
    print(f"데이터 크기 (행, 열): {df.shape}")
    print("\n--- 2. 컬럼별 정보 및 결측치 ---")
    print(df.info())
    print("\n결측치 개수:")
    print(df.isnull().sum())
    
    print("\n--- 3. 수치형 컬럼 기술 통계 요약 ---")
    # 판매가, 정가, 할인율(%), 리뷰건수, 리뷰총점, 판매지수 수치형 변환 후 요약
    df_numeric = df.copy()
    
    # 타입 클리닝
    df_numeric["판매가"] = pd.to_numeric(df_numeric["판매가"], errors="coerce")
    df_numeric["정가"] = pd.to_numeric(df_numeric["정가"], errors="coerce")
    df_numeric["할인율(%)"] = pd.to_numeric(df_numeric["할인율(%)"], errors="coerce")
    df_numeric["리뷰건수"] = pd.to_numeric(df_numeric["리뷰건수"], errors="coerce")
    df_numeric["리뷰총점"] = pd.to_numeric(df_numeric["리뷰총점"], errors="coerce")
    df_numeric["판매지수"] = pd.to_numeric(df_numeric["판매지수"], errors="coerce")
    
    print(df_numeric[["판매가", "정가", "할인율(%)", "리뷰건수", "리뷰총점", "판매지수"]].describe())
    
    print("\n--- 4. 범주형 데이터 빈도 (Top 5) ---")
    print("\n[출판사]")
    print(df["출판사"].value_counts().head(5))
    print("\n[저자]")
    print(df["저자"].value_counts().head(5))
    
    print("\n--- 5. 데이터 샘플 (첫 3행) ---")
    print(df.head(3))

if __name__ == "__main__":
    preview_data()
