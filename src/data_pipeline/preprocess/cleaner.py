import re
import html

def clean_text(text: str) -> str:
    """
    对文本进行清洗：
    1. 去除 HTML 标签
    2. 去除 Emoji 表情
    3. 去除特殊符号，仅保留中文、部分标点（可选）
    
    Args:
        text (str): 原始文本
        
    Returns:
        str: 清洗后的文本
    """
    if not isinstance(text, str):
        return ""
        
    # 1. 去除 HTML 标签
    text = html.unescape(text)
    text = re.sub(r'<[^>]+>', '', text)
    
    # 2. 去除 URL
    text = re.sub(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', '', text)
    
    # 3. 仅保留中文
    # 说明：根据你的需求“仅保留中文”，这里使用正则 [^\u4e00-\u9fa5] 匹配非中文字符并替换为空格
    # 如果后续发现需要保留这里的 "Member's Mark" 等英文品牌名，可以调整正则为 [^\u4e00-\u9fa5a-zA-Z0-9]
    pattern = re.compile(r'[^\u4e00-\u9fa5]')
    text = re.sub(pattern, ' ', text)
    
    # 4. 去除多余空格
    text = re.sub(r'\s+', ' ', text).strip()
    
    return text
