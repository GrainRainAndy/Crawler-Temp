import os
import glob
import re
import pandas as pd

def merge_raw_data():
    raw_dir = os.path.join("data", "01_raw")
    
    # 正则匹配文件名: search_comments_2026-01-25_山姆超市.csv
    # 提取: 类型(comments/contents), 日期, 关键词
    pattern = re.compile(r"search_(comments|contents)_(\d{4}-\d{2}-\d{2})_(.+)\.csv")
    
    files = glob.glob(os.path.join(raw_dir, "*.csv"))
    groups = {}

    # 1. 分组
    for f in files:
        filename = os.path.basename(f)
        match = pattern.match(filename)
        if match:
            dtype, date, keyword = match.groups()
            key = (dtype, keyword)
            if key not in groups:
                groups[key] = []
            
            groups[key].append({
                'date': date,
                'path': f,
                'filename': filename
            })

    # 2. 合并
    for (dtype, keyword), file_list in groups.items():
        # 按日期排序，确保拼接顺序
        file_list.sort(key=lambda x: x['date'])
        
        if len(file_list) < 2:
            continue
            
        print(f"正在合并 [{dtype} - {keyword}] 的 {len(file_list)} 个文件...")

        # 确定目标文件名（使用最早的日期）
        earliest_date = file_list[0]['date']
        target_filename = f"search_{dtype}_{earliest_date}_{keyword}.csv"
        target_path = os.path.join(raw_dir, target_filename)
        
        dfs = []
        for file_info in file_list:
            try:
                # 尝试读取，处理编码
                try:
                    df = pd.read_csv(file_info['path'], encoding='utf-8-sig')
                except UnicodeDecodeError:
                    df = pd.read_csv(file_info['path'], encoding='gbk')
                
                dfs.append(df)
                print(f"  读取: {file_info['filename']} ({len(df)} 条)")
            except Exception as e:
                print(f"  [Error] 读取失败 {file_info['filename']}: {e}")
        
        if dfs:
            # 拼接数据 (保留所有条目，不删除)
            merged_df = pd.concat(dfs, ignore_index=True)
            
            # 保存到目标路径
            # 注意：先读取全部到内存再写入，避免读写冲突
            merged_df.to_csv(target_path, index=False, encoding='utf-8-sig')
            print(f"  -> 合并并保存为: {target_filename} (总计 {len(merged_df)} 条)")
            
            # 删除旧文件 (如果是合并生成的新文件覆盖了旧文件中的一个，则不再单独删除该文件)
            # 只有当源文件路径 != 目标路径时，才需要删除源文件
            # 但在这里，target_path 必然等于 file_list[0]['path']，因为它就是以最早日期命名的
            for file_info in file_list:
                if file_info['path'] != target_path:
                    try:
                        os.remove(file_info['path'])
                        print(f"  已删除旧分片: {file_info['filename']}")
                    except Exception as e:
                        print(f"  [Error] 删除失败 {file_info['filename']}: {e}")
            
            print("-" * 50)

if __name__ == "__main__":
    merge_raw_data()
