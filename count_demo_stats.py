import os
import glob
import pandas as pd

def count_stats():
    # 目标目录
    raw_dir = os.path.join("demo", "01_raw")
    
    if not os.path.exists(raw_dir):
        print(f"Directory not found: {raw_dir}")
        return

    files = glob.glob(os.path.join(raw_dir, "*.csv"))
    
    total_comments = 0
    total_contents = 0
    file_count = 0
    
    print(f"Scanning directory: {raw_dir}")
    print("-" * 50)
    
    for f in files:
        filename = os.path.basename(f)
        try:
            # 读取CSV，仅读取一列以加快速度，处理大文件
            df = pd.read_csv(f, usecols=[0]) 
            count = len(df)
            
            if "comments" in filename:
                total_comments += count
                # print(f"[Comment] {filename}: {count}")
            elif "contents" in filename:
                total_contents += count
                # print(f"[Content] {filename}: {count}")
            else:
                print(f"[Unknown] {filename}: {count}")
                
            file_count += 1
        except Exception as e:
            print(f"Error reading {filename}: {e}")

    print("-" * 50)
    print(f"Total Files Scanned: {file_count}")
    print(f"Total Posts (Contents): {total_contents}")
    print(f"Total Comments: {total_comments}")
    print(f"Grand Total Records: {total_contents + total_comments}")

if __name__ == "__main__":
    count_stats()
