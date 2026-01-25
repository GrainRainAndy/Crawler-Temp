import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from wordcloud import WordCloud
import os
import sys
import numpy as np
from collections import Counter
from datetime import datetime

# 设置中文字体
plt.rcParams['font.sans-serif'] = ['SimHei', 'Microsoft YaHei']
plt.rcParams['axes.unicode_minus'] = False
# 设置绘图风格
sns.set_style("whitegrid", {"font.sans-serif": ['SimHei', 'Microsoft YaHei']})

class Visualizer:
    def __init__(self):
        self.output_dir = os.path.join('data', '03_visualizations')
        os.makedirs(self.output_dir, exist_ok=True)

    # =========================================================================
    # (一) 词频统计与词云图绘制
    # =========================================================================
    def plot_word_cloud_and_freq(self, file_path, prefix):
        print("\n### (一) 词频统计与词云图绘制")
        print(f"处理文件: {os.path.basename(file_path)}")
        
        try:
            df = pd.read_csv(file_path, encoding='utf-8-sig')
            if 'tokens_str' not in df.columns:
                print("跳过: 缺少 tokens_str 列，请检查预处理步骤")
                return

            df['tokens_str'] = df['tokens_str'].fillna('')
            text_data = ' '.join(df['tokens_str'].astype(str))
            
            # 1. 绘制词云
            self._generate_wordcloud(text_data, f"{prefix}_wordcloud.png")
            
            # 2. 绘制词频图
            self._plot_frequency_bar(text_data, f"{prefix}_freq_bar.png")
            
        except Exception as e:
            print(f"词云/词频绘制失败: {e}")

    def _generate_wordcloud(self, text, filename):
        if not text.strip(): return
        
        # 创建圆形 Mask (使用 numpy 生成 1000x1000 的圆形遮罩)
        x, y = np.ogrid[:1000, :1000]
        # (x - center_x)^2 + (y - center_y)^2 > radius^2
        mask = (x - 500) ** 2 + (y - 500) ** 2 > 480 ** 2
        mask = 255 * mask.astype(int)

        wc = WordCloud(
            font_path='msyh.ttc',
            width=1000, height=1000,
            background_color='white',
            max_words=200,
            mask=mask,               # 应用圆形遮罩
            contour_width=3,         # 添加轮廓线
            contour_color='#4c72b0', # 轮廓线颜色 (使用 seaborn 经典深蓝)
            colormap='tab20',        # 使用更多彩的配色方案
            random_state=42,         # 固定随机种子
            collocations=False,
            prefer_horizontal=0.9    # 90% 的词水平排列，更易读
        ).generate(text)
        
        output_path = os.path.join(self.output_dir, filename)
        
        plt.figure(figsize=(10, 10)) # 正方形画布
        plt.imshow(wc, interpolation='bilinear')
        plt.axis('off')
        plt.tight_layout(pad=0)
        plt.savefig(output_path, dpi=300, bbox_inches='tight') # 去除白边
        plt.close()
        print(f"  [√] 美化版词云图已保存: {filename}")

    def _plot_frequency_bar(self, text, filename):
        words = text.split()
        if not words: return
        
        counter = Counter(words)
        top_20 = counter.most_common(20)
        
        df_freq = pd.DataFrame(top_20, columns=['word', 'count'])
        
        plt.figure(figsize=(12, 8))
        ax = sns.barplot(x='count', y='word', data=df_freq, palette='viridis')
        ax.bar_label(ax.containers[0])
        plt.title('Top 20 高频词统计', fontsize=16)
        plt.xlabel('出现频次')
        plt.ylabel('关键词')
        
        output_path = os.path.join(self.output_dir, filename)
        plt.tight_layout()
        plt.savefig(output_path, dpi=300)
        plt.close()
        print(f"  [√] 词频统计图已保存: {filename}")

    # =========================================================================
    # (二) 评论时间分布可视化
    # =========================================================================
    def plot_time_distribution(self, file_path, prefix):
        print("\n### (二) 评论时间分布可视化")
        print(f"处理文件: {os.path.basename(file_path)}")
        
        try:
            df = pd.read_csv(file_path, encoding='utf-8-sig')
            
            # MediaCrawler 的 create_time 通常是毫秒级时间戳
            if 'create_time' not in df.columns:
                print("Create_time column not found.")
                # 尝试 date 列 (部分平台是 date)
                if 'date' in df.columns:
                    # 假定已经是日期格式字符串
                    df['dt'] = pd.to_datetime(df['date'], errors='coerce')
                else:
                    print("跳过: 未找到 create_time 或 date 时间列")
                    return
            else:
                # 转换毫秒时间戳
                df['dt'] = pd.to_datetime(df['create_time'], unit='ms', errors='coerce')

            # 去除转换失败的行
            df = df.dropna(subset=['dt'])
            
            if df.empty:
                print("没有有效的时间数据")
                return

            # 按天统计
            daily_counts = df.groupby(df['dt'].dt.date).size()
            daily_df = daily_counts.reset_index(name='count')
            daily_df['dt'] = pd.to_datetime(daily_df['dt']) # 确保是datetime类型以便绘图

            plt.figure(figsize=(14, 7))
            sns.lineplot(data=daily_df, x='dt', y='count', marker='o', linewidth=2.5, color='#4c72b0')
            plt.title('评论/笔记发布随时间变化趋势', fontsize=16)
            plt.xlabel('日期')
            plt.ylabel('数量')
            plt.grid(True, linestyle='--', alpha=0.6)
            plt.xticks(rotation=45)
            
            filename = f"{prefix}_time_trend.png"
            output_path = os.path.join(self.output_dir, filename)
            plt.tight_layout()
            plt.savefig(output_path, dpi=300)
            plt.close()
            print(f"  [√] 时间分布图已保存: {filename}")
            
            # 如果有小时分布，也可以画一下 (热力图或柱状图)
            # 按小时统计
            df['hour'] = df['dt'].dt.hour
            hour_counts = df['hour'].value_counts().sort_index()
            
            plt.figure(figsize=(10, 6))
            sns.barplot(x=hour_counts.index, y=hour_counts.values, color='#55a868')
            plt.title('全天发布时段分布 (24小时制)', fontsize=16)
            plt.xlabel('小时 (0-23)')
            plt.ylabel('数量')
            
            filename_hour = f"{prefix}_hour_dist.png"
            output_path_hour = os.path.join(self.output_dir, filename_hour)
            plt.tight_layout()
            plt.savefig(output_path_hour, dpi=300)
            plt.close()
            print(f"  [√] 时段分布图已保存: {filename_hour}")

        except Exception as e:
            print(f"时间分布绘制失败: {e}")

    # =========================================================================
    # (三) 情感倾向分布可视化
    # =========================================================================
    def plot_sentiment_distribution(self, file_path, prefix):
        print("\n### (三) 情感倾向分布可视化")
        print(f"处理文件: {os.path.basename(file_path)}")
        
        try:
            df = pd.read_csv(file_path, encoding='utf-8-sig')
            
            if 'sentiment_label' not in df.columns:
                print("跳过: 未找到 sentiment_label 列，请先运行 src/analysis/sentiment_analysis.py")
                return

            counts = df['sentiment_label'].value_counts()
            
            # 1. 饼图 (Pie Chart)
            plt.figure(figsize=(8, 8))
            colors = {'Positive': '#ff9999', 'Negative': '#66b3ff', 'Neutral': '#99ff99'}
            # 匹配颜色，如果出现 label 不在 keys 中则使用默认
            pie_colors = [colors.get(l, 'gray') for l in counts.index]
            
            plt.pie(counts, labels=counts.index, autopct='%1.1f%%', startangle=90, colors=pie_colors, 
                    wedgeprops={'edgecolor': 'white', 'linewidth': 2})
            plt.title('情感倾向占比', fontsize=16)
            
            filename_pie = f"{prefix}_sentiment_pie.png"
            output_path_pie = os.path.join(self.output_dir, filename_pie)
            plt.savefig(output_path_pie, dpi=300)
            plt.close()
            print(f"  [√] 情感饼图已保存: {filename_pie}")
            
            # 2. 小提琴图 (Violin Plot) - 如果有 score
            if 'sentiment_score' in df.columns:
                plt.figure(figsize=(10, 6))
                sns.violinplot(y=df['sentiment_score'], color='#1f77b4')
                plt.title('情感得分密度分布 (Violin Plot)', fontsize=16)
                plt.ylabel('情感得分 (0=负面, 1=正面)')
                plt.yticks([0, 0.5, 1.0])
                
                filename_violin = f"{prefix}_sentiment_violin.png"
                output_path_violin = os.path.join(self.output_dir, filename_violin)
                plt.savefig(output_path_violin, dpi=300)
                plt.close()
                print(f"  [√] 情感密度图已保存: {filename_violin}")

        except Exception as e:
            print(f"情感分布绘制失败: {e}")

def main():
    viz = Visualizer()
    
    # 我们使用 analyzed 目录下的数据，因为它包含了所有需要的字段 (清洗后的文本 + 原始时间 + 情感标签)
    input_dir = os.path.join('data', '03_analyzed')
    if not os.path.exists(input_dir):
        print(f"输入目录 {input_dir} 不存在，请先运行 sentiment_analysis.py")
        return

    files = [f for f in os.listdir(input_dir) if f.endswith('.csv')]
    
    for file in files:
        file_path = os.path.join(input_dir, file)
        
        # 提取前缀，去除 'analyzed_' 和 'processed_'
        clean_name = file.replace('analyzed_', '').replace('processed_', '').replace('.csv', '')
        
        print("\n" + "="*50)
        print(f"开始可视化任务: {clean_name}")
        print("="*50)

        # 1. 词云与词频 (对应 clean_text/tokens_str)
        # 注意: sentiment_analysis.py 生成的文件里应该保留了 tokens_str 列。
        # 我们来检查一下，如果没有，可能需要 merge 或者重新生成。
        # 假设 sentiment_analysis.py 是读取 processed 数据并在此基础上增加列保存的，所以应该有 tokens_str。
        viz.plot_word_cloud_and_freq(file_path, clean_name)
        
        # 2. 时间分布 (对应 create_time)
        viz.plot_time_distribution(file_path, clean_name)
        
        # 3. 情感分布 (对应 sentiment_label/score)
        viz.plot_sentiment_distribution(file_path, clean_name)

if __name__ == "__main__":
    main()
