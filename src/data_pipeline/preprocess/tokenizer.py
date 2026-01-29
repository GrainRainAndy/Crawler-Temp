import jieba
import os

class Tokenizer:
    def __init__(self, dict_path='data/dictionaries/user_dict.txt', stopwords_path='data/dictionaries/hit_stopwords.txt'):
        self.dict_path = dict_path
        self.stopwords_path = stopwords_path
        self.stopwords = set()
        
        # 初始化
        self._load_user_dict()
        self._load_stopwords()
        
    def _load_user_dict(self):
        """加载自定义词典"""
        if os.path.exists(self.dict_path):
            jieba.load_userdict(self.dict_path)
            print(f"已加载自定义词典: {self.dict_path}")
        else:
            print(f"Warning: 自定义词典未找到: {self.dict_path}")

    def _load_stopwords(self):
        """加载停用词表"""
        if os.path.exists(self.stopwords_path):
            with open(self.stopwords_path, 'r', encoding='utf-8') as f:
                for line in f:
                    self.stopwords.add(line.strip())
            print(f"已加载停用词表，共 {len(self.stopwords)} 个词")
        else:
            print(f"Warning: 停用词表未找到: {self.stopwords_path}")
            
    def tokenize(self, text: str) -> list[str]:
        """
        分词并去除停用词
        
        Args:
            text (str): 清洗后的文本
            
        Returns:
            list[str]: 分词结果列表
        """
        if not text:
            return []
            
        # 精确模式分词
        words = jieba.cut(text, cut_all=False)
        
        # 去除停用词和空字符
        result = [word for word in words if word not in self.stopwords and word.strip()]
        
        return result

# 单例实例，方便直接调用
_tokenizer_instance = None

def get_tokenizer():
    global _tokenizer_instance
    if _tokenizer_instance is None:
        _tokenizer_instance = Tokenizer()
    return _tokenizer_instance
