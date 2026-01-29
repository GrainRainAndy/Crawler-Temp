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
    # (一) 词频统计与词云图绘制 (针对整体)
    # =========================================================================
    def plot_word_cloud_and_freq(self, df, prefix):
        print("\n### (一) 词频统计与词云图绘制")
        
        if 'tokens_str' not in df.columns:
            print("跳过: 缺少 tokens_str 列")
            return

        text_data = ' '.join(df['tokens_str'].fillna('').astype(str))
        
        # 使用统一方法进行深度清洗
        cleaned_words = self._clean_and_filter_words(text_data)
        if not cleaned_words: 
            print("跳过: 清洗后无有效词汇")
            return
            
        cleaned_text = ' '.join(cleaned_words)
        
        # 1. 绘制词云 (使用清洗后的文本)
        self._generate_wordcloud(cleaned_text, f"{prefix}_wordcloud.png")
        
        # 2. 绘制词频图 (传入清洗后的词列表)
        self._plot_frequency_bar(cleaned_words, f"{prefix}_freq_bar.png")

    def _clean_and_filter_words(self, text):
        # 0. 预处理：合并否定词（处理“好吃”vs“不好吃”）
        import re
        negation_patterns = [
            (r'不\s+(好吃|好喝|新鲜|划算|值得|推荐|行|错|贵|喜欢|爱吃|足|够|大|小|多|少)', r'不\1'),
            (r'没\s+(有|必要|人|货)', r'没\1')
        ]
        text_processed = text
        for pattern, repl in negation_patterns:
            text_processed = re.sub(pattern, repl, text_processed)

        words = text_processed.split()
        if not words: return []
        
        # 1. 加载停用词表
        stopwords = set()
        stopwords_path = os.path.join('data', 'dictionaries', 'hit_stopwords.txt')
        if os.path.exists(stopwords_path):
            with open(stopwords_path, 'r', encoding='utf-8') as f:
                stopwords.update([line.strip() for line in f])
        
        # 2. 添加自定义的“无用副词/语气词/高频动词”
        custom_stopwords = {
            '山姆', '话题', '超市', '会员', '山姆会员店', # 专有名词
            '真的', '非常', '特别', '超级', '比较', '有点', '一点', '一些', # 程度副词
            '就是', '还是', '只是', '当时', '已经', '可能', '确实', '其实', # 状态/时间副词
            '但是', '所以', '虽然', '因为', '不过', '如果不', '而且', # 连接词
            '一个', '一次', '一下', '一天', '一直', '一定', '一般', '一遍', # 数量/频率
            '这个', '那个', '这些', '那些', '这里', '那里', # 代词
            '有没有', '是什么', '是不是', '能不能', # 疑问词
            '感觉', '觉得', '认为', '知道', '看到', '听说', # 感官动词
            '去', '买', '吃', '拿', '做', '搞', '弄', '玩', '冲', # 高频动词(过于泛化)
            '好', '多', '少', '大', '小', '早', '晚', # 简单形容词
            '啊', '呀', '哦', '嗯', '呢', '吧', '嘛', '啦', '咯', '呗', '哇', # 语气词
            '都', '也', '还', '又', '只', '就', '才', '再', '很', '太', '更', '最', '不', '没', '非', # 基础副词
            '人', '家', '店', '东西', '朋友', '姐妹', '时候', '情况', '样子', # 泛化名词
            '今天', '明天', '后天', '昨天', '前天', '现在', '最近', '目前', '时间', # 时间/状态
            '偷笑', '捂脸', '害羞', '笑哭', '大笑', '呲牙', '流泪', '尴尬', '发呆', '微笑' # 表情转译 (新增)
        }
        stopwords.update(custom_stopwords)

        # 3. 过滤
        # 同时过滤单字
        return [w for w in words if w not in stopwords and len(w) > 1] 

    def _generate_wordcloud(self, text, filename):
        if not text.strip(): return
        
        # 创建圆形 Mask
        x, y = np.ogrid[:1000, :1000]
        mask = (x - 500) ** 2 + (y - 500) ** 2 > 480 ** 2
        mask = 255 * mask.astype(int)

        wc = WordCloud(
            font_path='msyh.ttc',
            width=1000, height=1000,
            background_color='white',
            max_words=200,
            mask=mask,
            contour_width=3,
            contour_color='#4c72b0',
            colormap='tab20',
            random_state=42,
            collocations=False, # 既然已经做了预处理，这里关掉 collcations 避免重复合并
            prefer_horizontal=0.9
        ).generate(text)
        
        output_path = os.path.join(self.output_dir, filename)
        
        plt.figure(figsize=(10, 10))
        plt.imshow(wc, interpolation='bilinear')
        plt.axis('off')
        plt.tight_layout(pad=0)
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        plt.close()
        print(f"  [√] 词云图已保存: {filename}")

    def _plot_frequency_bar(self, words, filename):
        if not words: return

        counter = Counter(words)
        top_20 = counter.most_common(20)

        
        df_freq = pd.DataFrame(top_20, columns=['word', 'count'])
        
        plt.figure(figsize=(12, 8))
        ax = sns.barplot(x='count', y='word', data=df_freq, palette='viridis', hue='word', legend=False)
        # 显式标注每一个数值
        # 由于使用了 hue='word'，Seaborn 会为每个条形创建一个独立的 container，必须遍历所有 container
        for container in ax.containers:
            ax.bar_label(container, label_type='edge', padding=3, fontsize=10)
            
        plt.title('Top 20 高频词统计 (整体)', fontsize=16)
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
    def plot_time_distribution(self, df, prefix):
        print("\n### (二) 评论时间分布可视化")
        
        # 转换时间
        if 'create_time' in df.columns:
            df['dt'] = pd.to_datetime(df['create_time'], unit='ms', errors='coerce')
        elif 'date' in df.columns:
            df['dt'] = pd.to_datetime(df['date'], errors='coerce')
        else:
            print("跳过: 未找到 create_time 或 date 时间列")
            return
            
        df = df.dropna(subset=['dt'])
        if df.empty: return

        # 按天统计
        daily_counts = df.groupby(df['dt'].dt.date).size().reset_index(name='count')
        daily_df = pd.DataFrame(daily_counts)
        daily_df['dt'] = pd.to_datetime(daily_df.iloc[:, 0])

        plt.figure(figsize=(14, 7))
        # 调整点的大小 (markersize) 和线宽
        ax = sns.lineplot(data=daily_df, x='dt', y='count', marker='o', markersize=5, linewidth=2, color='#4c72b0')
        
        # 标注数值: 避免所有点都标导致重叠，采取“间隔 + 峰值”策略
        # 1. 找出最大值
        max_val = daily_df['count'].max()
        # 2. 只有当点数不是太多时才尝试标注，或者间隔标注
        step = max(1, len(daily_df) // 15)  # 保证大约标 15 个点左右
        
        for i in range(len(daily_df)):
            row = daily_df.iloc[i]
            x_val = row['dt']
            y_val = row['count']
            
            # 标记条件: 是最大值 OR 是间隔点
            if y_val == max_val or i % step == 0:
                ax.text(x_val, y_val + max_val * 0.01, f'{int(y_val)}', 
                        ha='center', va='bottom', fontsize=9, color='#333333')

        plt.title('评论/笔记发布随时间变化趋势', fontsize=16)
        plt.xlabel('日期')
        plt.ylabel('数量')
        plt.grid(True, linestyle='--', alpha=0.6)
        plt.xticks(rotation=45)
        
        filename = f"{prefix}_time_trend.png"
        plt.tight_layout()
        plt.savefig(os.path.join(self.output_dir, filename), dpi=300)
        plt.close()
        print(f"  [√] 时间分布图已保存: {filename}")

    # =========================================================================
    # (三) 情感倾向分布可视化 (整体 + 分关键词对比)
    # =========================================================================
    def plot_sentiment_distribution(self, df, prefix):
        print("\n### (三) 情感倾向分布可视化")
        
        if 'sentiment_label' not in df.columns:
            print("跳过: 未找到 sentiment_label 列")
            return

        # 1. 整体饼图
        counts = df['sentiment_label'].value_counts()
        plt.figure(figsize=(8, 8))
        colors = {'Positive': '#ff9999', 'Negative': '#66b3ff', 'Neutral': '#99ff99'}
        pie_colors = [colors.get(l, 'gray') for l in counts.index]
        
        plt.pie(counts, labels=counts.index, autopct='%1.1f%%', startangle=90, colors=pie_colors, 
                wedgeprops={'edgecolor': 'white', 'linewidth': 2})
        plt.title('整体情感倾向占比', fontsize=16)
        plt.savefig(os.path.join(self.output_dir, f"{prefix}_sentiment_pie.png"), dpi=300)
        plt.close()
        print(f"  [√] 整体情感饼图已保存")

        # 2. 整体小提琴图
        if 'sentiment_score' in df.columns:
            plt.figure(figsize=(10, 6))
            sns.violinplot(y=df['sentiment_score'], color='#1f77b4')
            plt.title('整体情感得分密度分布', fontsize=16)
            plt.ylabel('情感得分 (0=负面, 1=正面)')
            plt.savefig(os.path.join(self.output_dir, f"{prefix}_sentiment_violin.png"), dpi=300)
            plt.close()
            print(f"  [√] 整体情感密度图已保存")

        # 3. [新增] 分关键词的情感对比堆叠图
        if 'keyword' in df.columns:
            self._plot_keyword_sentiment_comparison(df, prefix)

    def _plot_keyword_sentiment_comparison(self, df, prefix):
        """
        绘制不同关键词下的情感分布对比（堆叠柱状图）
        """
        try:
            # 过滤掉 keyword 为 unknown 的
            df_k = df[df['keyword'] != 'unknown'].copy()
            if df_k.empty: return

            # 统计每个 keyword 下各情感的比例
            # crosstab: 行=keyword, 列=sentiment_label
            ct = pd.crosstab(df_k['keyword'], df_k['sentiment_label'], normalize='index')
            
            # 确保列顺序
            desired_order = ['Negative', 'Neutral', 'Positive']
            ct = ct.reindex(columns=[c for c in desired_order if c in ct.columns], fill_value=0)
            
            # 绘图
            ax = ct.plot(kind='bar', stacked=True, figsize=(14, 8), 
                         color=['#66b3ff', '#99ff99', '#ff9999']) # 对应 Neg, Neu, Pos
            
            # 标注数值 (百分比)
            for c in ax.containers:
                # 过滤掉 0 值，避免标签重叠
                labels = [f'{v.get_height():.1%}' if v.get_height() > 0.02 else '' for v in c]
                ax.bar_label(c, labels=labels, label_type='center', fontsize=9)

            plt.title('不同关键词下的情感倾向分布对比', fontsize=16)
            plt.xlabel('关键词')
            plt.ylabel('占比')
            plt.legend(title='情感', bbox_to_anchor=(1.05, 1), loc='upper left')
            plt.xticks(rotation=45, ha='right')
            plt.tight_layout()
            
            filename = f"{prefix}_keyword_sentiment_stack.png"
            plt.savefig(os.path.join(self.output_dir, filename), dpi=300)
            plt.close()
            print(f"  [√] 关键词情感对比图已保存: {filename}")
            
        except Exception as e:
            print(f"绘制关键词对比图失败: {e}")

    # =========================================================================
    # (四) [新增] 关键词声量统计
    # =========================================================================
    def plot_keyword_volume(self, df, prefix):
        print("\n### (四) 关键词数据量统计")
        if 'keyword' not in df.columns:
            return

        df_k = df[df['keyword'] != 'unknown']
        if df_k.empty: return
        
        counts = df_k['keyword'].value_counts()
        
        plt.figure(figsize=(12, 6))
        ax = sns.barplot(x=counts.index, y=counts.values, palette='magma', hue=counts.index, legend=False)
        # 标注具体数值，位于条形顶端外部
        for container in ax.containers:
            ax.bar_label(container, label_type='edge', padding=1, fontsize=10)
        
        plt.title('各关键词爬取数据量对比', fontsize=16)
        plt.xlabel('关键词')
        plt.ylabel('数据条数')
        plt.xticks(rotation=45, ha='right')
        plt.tight_layout()
        
        filename = f"{prefix}_keyword_volume.png"
        plt.savefig(os.path.join(self.output_dir, filename), dpi=300)
        plt.close()
        print(f"  [√] 关键词声量图已保存: {filename}")

def main():
    viz = Visualizer()
    input_dir = os.path.join('data', '03_analyzed')
    
    if not os.path.exists(input_dir):
        print(f"输入目录 {input_dir} 不存在")
        return

    files = [f for f in os.listdir(input_dir) if f.endswith('.csv')]
    
    for file in files:
        file_path = os.path.join(input_dir, file)
        
        # 只处理合并后的全量文件，避免处理碎片文件
        if 'processed_all' not in file:
            print(f"\n跳过非合并文件: {file} (建议先运行 run_preprocess.py 生成合并数据)")
            continue

        clean_name = file.replace('analyzed_', '').replace('processed_', '').replace('.csv', '')
        
        print("\n" + "="*50)
        print(f"开始可视化任务: {clean_name}")
        print("="*50)
        
        try:
            df = pd.read_csv(file_path, encoding='utf-8-sig')
            
            # 1. 词云与词频
            viz.plot_word_cloud_and_freq(df, clean_name)
            
            # 2. 时间分布
            viz.plot_time_distribution(df, clean_name)
            
            # 3. 情感分布 (含关键词对比)
            viz.plot_sentiment_distribution(df, clean_name)
            
            # 4. 关键词声量
            viz.plot_keyword_volume(df, clean_name)
            
        except Exception as e:
            print(f"处理 {file} 时发生错误: {e}")

if __name__ == "__main__":
    main()
