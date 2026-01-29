import pandas as pd
import os
import sys
from tqdm import tqdm
from transformers import pipeline

# 全局配置
# 使用 uer/roberta-base-finetuned-dianping-chinese
MODEL_NAME = "uer/roberta-base-finetuned-dianping-chinese"
# 置信度阈值：低于此值的预测将被归类为 Neutral
# 基于 determine_threshold.py 测算，0.56 对应约 8% 的中性占比
CONFIDENCE_THRESHOLD = 0.56

print(f"正在初始化 Hugging Face 模型: {MODEL_NAME}...")
# ... (省略中间代码) ...

def analyze_sentiment_hf(text):
    """
    使用 Hugging Face 模型进行预测
    返回: (model_label, model_conf, calibrated_label, calibrated_score)
    """
    if not isinstance(text, str) or not text.strip():
        # 空文本默认处理
        return 'Neutral', 0.5, 'Neutral', 0.5
    
    text = text[:500]
    
    try:
        result = sentiment_pipeline(text, truncation=True, max_length=512)[0]
        
        # 1. 获取原始模型输出 (Raw Data)
        # raw_label 通常是 'positive (stars 4, 5)' 或 'negative (stars 1, 2, 3)'
        raw_output_label = str(result['label']).lower()
        raw_conf = float(result['score']) # 置信度 0.5 - 1.0
        
        # 简化原始标签
        if 'positive' in raw_output_label:
            model_label = 'Positive'
        elif 'negative' in raw_output_label:
            model_label = 'Negative'
        else:
            model_label = 'Neutral' # 极少情况
            
        # 2. 应用阈值校正 (Calibration)
        calibrated_label = model_label
        
        # 核心逻辑：如果模型确信度低于阈值，则视为中性
        if raw_conf < CONFIDENCE_THRESHOLD:
            calibrated_label = 'Neutral'
            
        # 3. 计算用于绘图的可视化得分 (0=Negative, 1=Positive)
        # 如果是 Neutral，得分为 0.5
        # 如果是 Positive，得分为 raw_conf (0.56 ~ 1.0)
        # 如果是 Negative，得分为 1 - raw_conf (0.0 ~ 0.44)
        if calibrated_label == 'Neutral':
            calibrated_score = 0.5
        elif calibrated_label == 'Positive':
            calibrated_score = raw_conf
        else: # Negative
            calibrated_score = 1 - raw_conf
            
        return model_label, raw_conf, calibrated_label, calibrated_score

    except Exception as e:
        return 'Neutral', 0.5, 'Neutral', 0.5

def main():
    # 读取预处理后的数据
    input_dir = os.path.join('data', '02_processed')
    output_dir = os.path.join('data', '03_analyzed')
    os.makedirs(output_dir, exist_ok=True)
    
    files = [f for f in os.listdir(input_dir) if f.endswith('.csv')]
    
    for file in files:
        if 'comments' not in file and 'contents' not in file:
            continue
            
        print(f"\n正在处理文件: {file}")
        file_path = os.path.join(input_dir, file)
        
        try:
            df = pd.read_csv(file_path, encoding='utf-8-sig')
            
            target_col = 'cleaned_text'
            if target_col not in df.columns:
                target_col = 'desc' if 'desc' in df.columns else 'content'
            
            if target_col not in df.columns:
                print(f"  跳过: 未找到文本列")
                continue

            print(f"  开始分析 {len(df)} 条数据 (基于阈值 {CONFIDENCE_THRESHOLD} 进行校正)...")
            
            tqdm.pandas(desc="Processing")
            
            df[target_col] = df[target_col].fillna('')
            
            # 批量分析
            results = df[target_col].progress_apply(analyze_sentiment_hf)
            
            # 保存四列数据：2列原始，2列校正
            # 原始模型输出
            df['model_label'] = results.apply(lambda x: x[0])
            df['model_confidence'] = results.apply(lambda x: x[1])
            
            # 校正后的用于展示的数据 (Visualizer 默认读取这两列)
            df['sentiment_label'] = results.apply(lambda x: x[2])
            df['sentiment_score'] = results.apply(lambda x: x[3])
            
            output_path = os.path.join(output_dir, f"analyzed_{file}")
            df.to_csv(output_path, index=False, encoding='utf-8-sig')
            print(f"  已保存: {output_path}")
            
            print("  校正后情感分布 (Corrected Distribution):")
            print(df['sentiment_label'].value_counts())
            
        except Exception as e:
            print(f"  处理文件 {file} 失败: {e}")

if __name__ == "__main__":
    main()
