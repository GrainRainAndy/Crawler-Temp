import pandas as pd
import os
import sys
from snownlp import SnowNLP

def analyze_sentiment(text):
    """
    使用 SnowNLP 计算情感分数
    范围 [0, 1]，越接近 1 越正面，越接近 0 越负面
    """
    if not isinstance(text, str) or not text.strip():
        return 0.5 # 中性缺省值
    
    try:
        s = SnowNLP(text)
        return s.sentiments
    except:
        return 0.5

def categorize_sentiment(score):
    """
    根据分数进行分类
    """
    if score >= 0.6:
        return 'Positive' # 正面
    elif score <= 0.4:
        return 'Negative' # 负面
    else:
        return 'Neutral' # 中性

def main():
    # 读取预处理后的数据 (包含清洗后的文本)
    input_dir = os.path.join('data', '02_processed')
    output_dir = os.path.join('data', '03_analyzed')
    os.makedirs(output_dir, exist_ok=True)
    
    # 查找评论数据 (通常情感分析主要针对评论或笔记正文)
    files = [f for f in os.listdir(input_dir) if f.endswith('.csv')]
    
    for file in files:
        if 'comments' not in file and 'contents' not in file:
            continue
            
        print(f"正在进行情感分析: {file}")
        file_path = os.path.join(input_dir, file)
        
        try:
            df = pd.read_csv(file_path, encoding='utf-8-sig')
            
            # 优先使用 cleaned_text，如果没有则用 content/desc
            target_col = 'cleaned_text'
            if target_col not in df.columns:
                target_col = 'desc' if 'desc' in df.columns else 'content'
            
            if target_col not in df.columns:
                print(f"  跳过: 未找到文本列")
                continue

            # 1. 计算情感得分 (Sentiment Score)
            print("  计算情感得分...")
            # 填充空值
            df[target_col] = df[target_col].fillna('')
            df['sentiment_score'] = df[target_col].apply(analyze_sentiment)
            
            # 2. 情感分类 (Sentiment Label)
            df['sentiment_label'] = df['sentiment_score'].apply(categorize_sentiment)
            
            # 3. 结果保存
            output_path = os.path.join(output_dir, f"analyzed_{file}")
            
            # 为了可视化方便，我们把原始数据中的 create_time 也带上
            # 但 processed 数据可能只保留了部分列？
            # 检查一下 processed 数据的生成逻辑: run_preprocess.py 读取 raw，增加了 columns，然后保存。
            # 所以 processed 数据里应该还保留着 raw 的所有列，包括 create_time。
            
            df.to_csv(output_path, index=False, encoding='utf-8-sig')
            print(f"  分析完成，已保存至 {output_path}")
            
            # 打印统计概览
            print("  情感分布:")
            print(df['sentiment_label'].value_counts())
            print("-" * 30)
            
        except Exception as e:
            print(f"  处理失败: {e}")

if __name__ == "__main__":
    main()
