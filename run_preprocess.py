import pandas as pd
import os
import sys

# 将 src 加入 sys.path 以便导入模块
sys.path.append(os.path.join(os.getcwd(), 'src'))

from preprocess.cleaner import clean_text
from preprocess.tokenizer import get_tokenizer

def process_file(file_path, output_dir):
    print(f"正在处理文件: {file_path}")
    
    try:
        # 读取 CSV，尝试不同的编码
        try:
            df = pd.read_csv(file_path, encoding='utf-8-sig')
        except UnicodeDecodeError:
            df = pd.read_csv(file_path, encoding='gbk')
            
        print(f"读取到 {len(df)} 行数据")
        
        # 确定需要处理的列
        # MediaCrawler 的输出列名通常是 'desc' (帖子内容) 或 'content' (评论内容)
        target_col = None
        if 'desc' in df.columns:
            target_col = 'desc'
        elif 'content' in df.columns:
            target_col = 'content'
            
        if not target_col:
            print(f"Warning: 在文件 {file_path} 中未找到文本列 (desc 或 content)，跳过处理。")
            return

        # 1. 清洗
        print("执行清洗...")
        df['cleaned_text'] = df[target_col].astype(str).apply(clean_text)
        
        # 2. 分词
        print("执行分词...")
        tokenizer = get_tokenizer()
        df['tokens'] = df['cleaned_text'].apply(tokenizer.tokenize)
        
        # 3. 保存
        filename = os.path.basename(file_path)
        output_path = os.path.join(output_dir, f"processed_{filename}")
        
        # 将 list 转为空格分隔的字符串保存，方便查看
        df['tokens_str'] = df['tokens'].apply(lambda x: ' '.join(x))
        
        df.to_csv(output_path, index=False, encoding='utf-8-sig')
        print(f"处理完成，保存至: {output_path}")
        
        # 打印示例
        print("\n--- 预处理效果示例 (前 3 行) ---")
        print(df[[target_col, 'cleaned_text', 'tokens']].head(3).to_markdown(index=False))
        print("-" * 50 + "\n")

    except Exception as e:
        print(f"处理文件 {file_path} 时出错: {e}")

def main():
    raw_dir = os.path.join('data', '01_raw')
    processed_dir = os.path.join('data', '02_processed')
    
    os.makedirs(processed_dir, exist_ok=True)
    
    # 获取所有 CSV 文件
    files = [f for f in os.listdir(raw_dir) if f.endswith('.csv')]
    
    if not files:
        print(f"在 {raw_dir} 下未找到 CSV 文件。")
        return
        
    for file in files:
        file_path = os.path.join(raw_dir, file)
        process_file(file_path, processed_dir)

if __name__ == "__main__":
    main()
