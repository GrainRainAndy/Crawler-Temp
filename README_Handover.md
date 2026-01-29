# 小红书品牌情感分析与可视化项目 - 移交指南

## 1. 项目概述
本项目旨在抓取小红书关于“山姆会员店”的评论与笔记数据，通过NLP技术进行清洗、分词、情感分析（基于BERT模型），并生成用于学术报告的高质量可视化图表（词云、情感分布、声量对比等）。

## 2. 环境搭建

### 2.1 基础环境
*   **Python 版本**: 3.12.12
*   **推荐管理工具**: Conda

```bash
conda create -n crawler python=3.12.12
conda activate crawler
```

### 2.2 核心依赖安装
项目依赖主要分为爬虫部分（Playwright）和分析部分（Pandas, PyTorch, Transformers, Seaborn）。

```bash
# 安装项目根目录下的 requirements.txt
pip install -r requirements.txt

# 分析与可视化所需的核心库
pip install pandas matplotlib seaborn wordcloud jieba snownlp
pip install torch transformers huggingface_hub tqdm
```

### 2.3 浏览器驱动 (用于爬虫)
```bash
playwright install
```

## 3. 项目结构说明

```text
Clawler-Temp/
├── data/                           # 数据存放目录
│   ├── 01_raw/                     # 爬虫抓取的原始 CSV 文件
│   ├── 02_processed/               # 清洗、分词合并后的数据 (process_data.py 生成)
│   ├── 03_analyzed/                # 包含情感得分为的数据 (sentiment_analysis.py 生成)
│   ├── 03_visualizations/          # 最终生成的图表 (visualizer.py 生成)
│   └── dictionaries/               # 词典文件
│       ├── hit_stopwords.txt       # 停用词表
│       └── user_dict.txt           # 自定义分词词典
├── src/
│   ├── data_pipeline/              # [NEW] 数据抓取与处理流水线
│   │   ├── fetch_data.py           # 爬虫主入口
│   │   ├── merge_data.py           # 多日期数据合并工具
│   │   ├── process_data.py         # 数据清洗等预处理入口
│   │   └── preprocess/             # [Internal] 预处理底层模块 (Cleaner, Tokenizer)
│   ├── analysis/
│   │   └── sentiment_analysis.py   # 情感分析脚本 (HuggingFace BERT)
│   └── visualization/
│       └── visualizer.py           # 可视化脚本 (词云、统计图)
├── crawler_config.json             # 爬虫与项目配置文件
├── README_Handover.md              # 本文档
```

## 4. 关键词选取策略

本项目在 `crawler_config.json` 中定义了抓取关键词，可直接在 `config` 中 `keywords` 项调整具体关键词。策略上分为四大维度，旨在全方位覆盖品牌声量：

1.  **品牌关键词**
    *   *关键词*: `山姆会员店`, `山姆超市`
    *   *目的*: 获取最广泛的品牌提及和总体舆情。
2.  **产品体验关键词**
    *   *关键词*: `山姆必买`, `山姆红榜`, `山姆无限回购` (正向); `山姆避雷`, `山姆黑榜`, `山姆难吃` (负向)
    *   *目的*: 捕捉具体的商品评价，区分“种草”与“拔草”行为。
3.  **服务与环境相关关键词**
    *   *关键词*: `山姆极速达`, `山姆配送`, `山姆试吃`, `山姆排队`, `山姆停车`
    *   *目的*: 评估线上/线下服务体验、物流时效及购物环境拥挤度。
4.  **会员价值与忠诚度关键词**
    *   *关键词*: `山姆续卡`, `山姆退卡`, `山姆卓越卡`, `山姆年费`, `山姆会员`
    *   *目的*: 分析用户对会员制的态度及续费意愿，洞察流失风险。

## 5. 标准复现流程 (Pipeline)

请按照以下顺序执行脚本：

### 步骤 1: 数据合并 (可选)
如果在不同时间段抓取了同一关键词，导致 `01_raw` 下存在多个碎片文件，先运行此脚本进行物理合并。
```bash
python src/data_pipeline/merge_data.py
```

### 步骤 2: 预处理 (Pipeline Start)
读取 `data/01_raw` 下的所有文件，进行去重、清洗、分词。
```bash
python src/data_pipeline/process_data.py
```
*   **输出**: `data/02_processed/`

### 步骤 3: 情感分析
使用预训练模型 `uer/roberta-base-finetuned-dianping-chinese` 对清洗后的文本进行打分。
*   **核心逻辑**: 代码中内置了置信度阈值 `CONFIDENCE_THRESHOLD = 0.56`。
*   **规则**: 若模型置信度低于 0.56，则强制归类为“中性 (Neutral)”，以保证中性评论占比符合真实分布 (~10%)。
```bash
python src/analysis/sentiment_analysis.py
```
*   **输出**: `data/03_analyzed/`

### 步骤 4: 可视化
读取分析结果，生成全套图表。
*   **核心逻辑**: 内置了深度清洗词表，会自动剔除“山姆”、“今天”、“偷笑”等无意义特征词，自动合并“不好吃”等否定词组。
*   **输出**:
    *   `*_wordcloud.png`: 圆形蓝色系词云
    *   `*_freq_bar.png`: Top 20 高频词条形图 (Top20)
    *   `*_keyword_sentiment_stack.png`: 关键词情感构成堆叠图 (含百分比)
    *   `*_keyword_volume.png`: 关键词声量排行 (含数值)
    *   `*_time_trend.png`: 时间分布折线图 (含峰值标注)
```bash
python src/visualization/visualizer.py
```

## 6. 常见问题与维护

1.  **停用词调整**:
    *   若图表中仍出现无意义词汇，请修改 `src/visualization/visualizer.py` 中的 `custom_stopwords` 集合，或更新 `data/dictionaries/hit_stopwords.txt`。

2.  **情感阈值调整**:
    *   若觉得中性评论太多或太少，请修改 `src/analysis/sentiment_analysis.py` 中的 `CONFIDENCE_THRESHOLD`。调高阈值会增加中性比例。

3.  **HuggingFace 模型下载**:
    *   首次运行情感分析需要下载约 400MB 模型权重。如网络不通，请手动下载 `uer/roberta-base-finetuned-dianping-chinese` 并修改代码中的 `MODEL_NAME` 为本地路径。

---
*文档生成日期: 2026-01-29*
