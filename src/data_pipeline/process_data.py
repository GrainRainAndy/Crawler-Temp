import pandas as pd
import os
import sys
import glob

# 将 src 加入 sys.path 以便导入模块
sys.path.append(os.path.join(os.getcwd(), 'src'))

from data_pipeline.preprocess.cleaner import clean_text
from data_pipeline.preprocess.tokenizer import get_tokenizer

def extract_keyword_from_filename(filename):
    """
    文件名格式: search_comments_2026-01-25_山姆必买.csv
    提取: 山姆必买
    """
    try:
        # 去掉扩展名
        name_no_ext = os.path.splitext(filename)[0]
        # 按照 '_' 分割
        parts = name_no_ext.split('_')
        # 假设最后一部分是关键词
        # 如果格式严格遵守 fetch_data.py 的定义，最后一部分即为 keywords
        if len(parts) >= 4:
            return parts[-1]
        else:
            return "unknown"
    except:
        return "unknown"

def process_and_merge(input_dir, output_dir, file_pattern, output_filename, target_col_names):
    """
    合并指定模式的所有 CSV 文件，进行清洗分词，并保存为一个总文件
    """
    all_files = glob.glob(os.path.join(input_dir, file_pattern))
    if not all_files:
        print(f"在 {input_dir} 未找到匹配 {file_pattern} 的文件")
        return

    print(f"正在合并 {len(all_files)} 个文件 (模式: {file_pattern})...")
    
    df_list = []
    
    for file_path in all_files:
        try:
            # 尝试不同编码读取
            try:
                df = pd.read_csv(file_path, encoding='utf-8-sig')
            except UnicodeDecodeError:
                df = pd.read_csv(file_path, encoding='gbk')
            
            # 提取关键词并添加列
            filename = os.path.basename(file_path)
            keyword = extract_keyword_from_filename(filename)
            df['keyword'] = keyword
            
            df_list.append(df)
        except Exception as e:
            print(f"读取文件 {file_path} 失败: {e}")

    if not df_list:
        return

    # 合并 DataFrame
    merged_df = pd.concat(df_list, ignore_index=True)
    print(f"合并完成，共 {len(merged_df)} 行数据")

    # 确定目标文本列
    # target_col_names 是一个列表，如 ['desc', 'content']，优先匹配存在的
    target_col = None
    for col in target_col_names:
        if col in merged_df.columns:
            target_col = col
            break
            
    if target_col:
        print(f"正在对列 '{target_col}' 进行清洗和分词...")
        # 1. 清洗
        # 填充 NaN 防止报错
        merged_df[target_col] = merged_df[target_col].fillna('')
        merged_df['cleaned_text'] = merged_df[target_col].astype(str).apply(clean_text)
        
        # 2. 分词
        tokenizer = get_tokenizer()
        merged_df['tokens'] = merged_df['cleaned_text'].apply(tokenizer.tokenize)
        merged_df['tokens_str'] = merged_df['tokens'].apply(lambda x: ' '.join(x))
    else:
        print("Warning: 未找到文本列，仅合并数据，不进行NLP处理")

    # 保存
    output_path = os.path.join(output_dir, output_filename)
    merged_df.to_csv(output_path, index=False, encoding='utf-8-sig')
    print(f"保存合并后的文件至: {output_path}")

def main():
    raw_dir = os.path.join('data', '01_raw')
    processed_dir = os.path.join('data', '02_processed')
    os.makedirs(processed_dir, exist_ok=True)
    
    # 1. 处理所有 search_comments_*.csv
    process_and_merge(
        input_dir=raw_dir,
        output_dir=processed_dir,
        file_pattern="search_comments_*.csv",
        output_filename="processed_all_comments.csv",
        target_col_names=['content']
    )
    
    print("-" * 30)

    # 2. 处理所有 search_contents_*.csv
    # 注意: MediaCrawler 导出的笔记内容列名可能是 'desc'
    process_and_merge(
        input_dir=raw_dir,
        output_dir=processed_dir,
        file_pattern="search_contents_*.csv",
        output_filename="processed_all_contents.csv",
        target_col_names=['desc', 'description', 'content']
    )

if __name__ == "__main__":
    main()
