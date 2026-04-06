"""
文档分类模块 - 基于朴素贝叶斯算法
用于自动对学习资料进行分类

AI方法：朴素贝叶斯分类器（传统机器学习算法）
"""

import os
import re
import json
import math
import pickle
from typing import List, Dict, Tuple
from collections import Counter, defaultdict


class NaiveBayesClassifier:
    """
    朴素贝叶斯文本分类器
    
    算法原理：
    - 基于贝叶斯定理，计算 P(类别|文档) ∝ P(文档|类别) × P(类别)
    - 假设特征（词）之间相互独立（朴素假设）
    - 使用拉普拉斯平滑处理未登录词
    
    应用场景：
    - 自动分类学习资料（数学/英语/政治/专业课等）
    - 识别文档主题
    - 文档标签推荐
    """
    
    def __init__(self, alpha=1.0):
        """
        初始化分类器
        
        参数：
            alpha: 拉普拉斯平滑参数，默认为1.0（拉普拉斯平滑）
        """
        self.alpha = alpha  # 平滑参数
        self.classes = set()  # 类别集合
        self.class_counts = Counter()  # 每个类别的文档数
        self.word_counts = defaultdict(Counter)  # 每个类别的词频
        self.total_words = defaultdict(int)  # 每个类别的总词数
        self.vocab = set()  # 词汇表
        self.class_priors = {}  # 类别先验概率
        self.word_probs = {}  # 词的条件概率
        
    def _tokenize(self, text: str) -> List[str]:
        """
        分词处理
        
        使用简单的空格分词 + 中文单字分词
        
        参数：
            text: 输入文本
            
        返回：
            分词列表
        """
        # 转换为小写并提取词
        text = text.lower()
        
        # 提取中文词汇（单字或连续中文）
        chinese_chars = re.findall(r'[\u4e00-\u9fff]+', text)
        
        # 提取英文单词
        english_words = re.findall(r'[a-z]+', text)
        
        # 提取数字
        numbers = re.findall(r'\d+', text)
        
        # 合并所有词
        words = []
        
        # 处理中文：每个词拆分成字或保留2-4字词
        for ch_word in chinese_chars:
            # 添加整词
            if 2 <= len(ch_word) <= 4:
                words.append(ch_word)
            # 添加单字
            words.extend(list(ch_word))
        
        words.extend(english_words)
        words.extend(numbers)
        
        return words
    
    def _extract_features(self, text: str) -> Counter:
        """
        从文本中提取特征（词频）
        
        参数：
            text: 输入文本
            
        返回：
            词频统计
        """
        words = self._tokenize(text)
        return Counter(words)
    
    def fit(self, texts: List[str], labels: List[str]):
        """
        训练分类器
        
        参数：
            texts: 训练文档列表
            labels: 对应类别标签列表
        """
        print("=" * 60)
        print("训练朴素贝叶斯分类器")
        print("=" * 60)
        
        # 统计每个类别的文档
        for text, label in zip(texts, labels):
            self.classes.add(label)
            self.class_counts[label] += 1
            
            # 提取特征
            features = self._extract_features(text)
            
            # 统计词频
            for word, count in features.items():
                self.word_counts[label][word] += count
                self.total_words[label] += count
                self.vocab.add(word)
        
        # 计算先验概率 P(类别)
        total_docs = sum(self.class_counts.values())
        for c in self.classes:
            self.class_priors[c] = math.log(self.class_counts[c] / total_docs)
        
        # 计算条件概率 P(词|类别)
        vocab_size = len(self.vocab)
        for c in self.classes:
            self.word_probs[c] = {}
            total = self.total_words[c]
            for word in self.vocab:
                # 拉普拉斯平滑
                count = self.word_counts[c][word]
                prob = math.log((count + self.alpha) / (total + self.alpha * vocab_size))
                self.word_probs[c][word] = prob
        
        print(f"训练完成:")
        print(f"  - 类别数: {len(self.classes)}")
        print(f"  - 词汇表大小: {vocab_size}")
        print(f"  - 训练文档数: {total_docs}")
        for c in sorted(self.classes):
            print(f"  - 类别 '{c}': {self.class_counts[c]} 篇文档")
        print("=" * 60)
    
    def predict_single(self, text: str) -> Tuple[str, Dict[str, float]]:
        """
        对单个文档进行分类
        
        参数：
            text: 待分类文档
            
        返回：
            (预测类别, 各类别概率字典)
        """
        features = self._extract_features(text)
        scores = {}
        
        for c in self.classes:
            # 初始化为类别先验概率
            score = self.class_priors[c]
            
            # 累加词的条件概率
            for word, count in features.items():
                if word in self.word_probs[c]:
                    score += self.word_probs[c][word] * count
                else:
                    # 未登录词，使用平滑后的概率
                    vocab_size = len(self.vocab)
                    total = self.total_words[c]
                    smoothed_prob = math.log(self.alpha / (total + self.alpha * vocab_size))
                    score += smoothed_prob * count
            
            scores[c] = score
        
        # 选择概率最大的类别
        predicted = max(scores, key=scores.get)
        
        # 转换为概率（归一化）
        # 使用softmax转换
        max_score = max(scores.values())
        exp_scores = {c: math.exp(s - max_score) for c, s in scores.items()}
        total_exp = sum(exp_scores.values())
        probs = {c: exp_scores[c] / total_exp for c in self.classes}
        
        return predicted, probs
    
    def predict(self, texts: List[str]) -> List[Tuple[str, Dict[str, float]]]:
        """
        批量预测
        
        参数：
            texts: 文档列表
            
        返回：
            预测结果列表
        """
        results = []
        for text in texts:
            pred, probs = self.predict_single(text)
            results.append((pred, probs))
        return results
    
    def save(self, path: str):
        """
        保存模型到文件
        
        参数：
            path: 保存路径
        """
        model_data = {
            'alpha': self.alpha,
            'classes': list(self.classes),
            'class_counts': dict(self.class_counts),
            'word_counts': {k: dict(v) for k, v in self.word_counts.items()},
            'total_words': dict(self.total_words),
            'vocab': list(self.vocab),
            'class_priors': self.class_priors,
            'word_probs': self.word_probs
        }
        
        with open(path, 'wb') as f:
            pickle.dump(model_data, f)
        
        print(f"模型已保存: {path}")
    
    def load(self, path: str):
        """
        从文件加载模型
        
        参数：
            path: 模型文件路径
        """
        with open(path, 'rb') as f:
            model_data = pickle.load(f)
        
        self.alpha = model_data['alpha']
        self.classes = set(model_data['classes'])
        self.class_counts = Counter(model_data['class_counts'])
        self.word_counts = defaultdict(Counter, 
                                       {k: Counter(v) for k, v in model_data['word_counts'].items()})
        self.total_words = defaultdict(int, model_data['total_words'])
        self.vocab = set(model_data['vocab'])
        self.class_priors = model_data['class_priors']
        self.word_probs = model_data['word_probs']
        
        print(f"模型已加载: {path}")
        print(f"  - 类别数: {len(self.classes)}")
        print(f"  - 词汇表大小: {len(self.vocab)}")


class DocumentClassifier:
    """
    文档分类器（集成朴素贝叶斯）
    
    预定义类别：
    - 数学：高等数学、线性代数、概率论等
    - 英语：词汇、语法、阅读等
    - 政治：马原、毛概、时政等
    - 专业课：计算机、电子、机械等专业内容
    - 其他：通用内容
    """
    
    # 类别关键词（用于生成训练数据）
    CATEGORY_KEYWORDS = {
        '数学': ['函数', '积分', '微分', '矩阵', '向量', '概率', '统计', 
                '极限', '导数', '线性代数', '高等数学', '微积分',
                'math', 'calculus', 'algebra', 'matrix', 'probability'],
        
        '英语': ['单词', '语法', '阅读', '写作', '听力', '翻译', '作文',
                '词汇', '四六级', '雅思', '托福', '考研英语',
                'english', 'vocabulary', 'grammar', 'reading', 'translation'],
        
        '政治': ['马克思主义', '毛泽东思想', '邓小平理论', '新时代中国特色社会主义思想',
                '哲学', '政治经济学', '科学社会主义', '时政', '热点',
                'politics', 'socialism', 'marxism', 'economy'],
        
        '计算机': ['编程', '算法', '数据结构', '操作系统', '计算机网络',
                 '数据库', '人工智能', '机器学习', '深度学习', '代码',
                 'computer', 'programming', 'algorithm', 'data structure',
                 'os', 'network', 'database', 'ai', 'ml'],
        
        '其他': []
    }
    
    def __init__(self):
        self.classifier = NaiveBayesClassifier(alpha=1.0)
        self.is_trained = False
        
    def generate_training_data(self) -> Tuple[List[str], List[str]]:
        """
        生成训练数据
        
        基于预定义的关键词生成模拟训练文档
        """
        texts = []
        labels = []
        
        # 为每个类别生成训练样本
        for category, keywords in self.CATEGORY_KEYWORDS.items():
            if not keywords:
                continue
            
            # 生成多个训练样本
            for i in range(20):
                # 随机组合关键词
                import random
                selected = random.sample(keywords, min(5, len(keywords)))
                # 添加一些通用词
                text = ' '.join(selected)
                text += ' 这是' + category + '相关的学习内容。'
                text += '需要掌握核心概念和重点知识。'
                
                texts.append(text)
                labels.append(category)
        
        return texts, labels
    
    def train(self, texts: List[str] = None, labels: List[str] = None):
        """
        训练分类器
        
        参数：
            texts: 训练文本列表，如果为None则使用自动生成数据
            labels: 对应标签列表
        """
        if texts is None:
            print("使用预设关键词生成训练数据...")
            texts, labels = self.generate_training_data()
        
        self.classifier.fit(texts, labels)
        self.is_trained = True
        
    def classify(self, text: str) -> Dict:
        """
        对文档进行分类
        
        参数：
            text: 待分类的文档文本
            
        返回：
            包含分类结果的字典
        """
        if not self.is_trained:
            # 如果未训练，先训练
            self.train()
        
        predicted, probs = self.classifier.predict_single(text)
        
        # 格式化概率
        sorted_probs = sorted(probs.items(), key=lambda x: x[1], reverse=True)
        
        return {
            'category': predicted,
            'confidence': probs[predicted],
            'all_probabilities': dict(sorted_probs),
            'top_categories': [c for c, p in sorted_probs[:3]]
        }
    
    def batch_classify(self, documents: List[Dict]) -> List[Dict]:
        """
        批量分类文档
        
        参数：
            documents: 文档列表，每个文档是包含'text'和'doc_id'的字典
            
        返回：
            分类结果列表
        """
        results = []
        for doc in documents:
            result = self.classify(doc['text'])
            result['doc_id'] = doc.get('doc_id', 'unknown')
            results.append(result)
        return results
    
    def save_model(self, path: str):
        """保存模型"""
        self.classifier.save(path)
    
    def load_model(self, path: str):
        """加载模型"""
        self.classifier.load(path)
        self.is_trained = True


# ============ 使用示例和测试 ============

def demo():
    """演示文档分类功能"""
    print("\n" + "=" * 60)
    print("文档分类器演示")
    print("=" * 60)
    
    # 创建分类器
    classifier = DocumentClassifier()
    
    # 训练（使用自动生成数据）
    classifier.train()
    
    # 测试文档
    test_docs = [
        "这个函数很重要，需要理解导数和积分的概念。",
        "英语阅读理解需要掌握词汇和语法。",
        "马克思主义哲学基本原理是唯物论和辩证法。",
        "Python是一种编程语言，常用于人工智能开发。",
        "这是一篇普通的文章，没有明确的专业内容。"
    ]
    
    print("\n测试分类:")
    print("-" * 60)
    for doc in test_docs:
        result = classifier.classify(doc)
        print(f"\n文档: {doc[:30]}...")
        print(f"  预测类别: {result['category']}")
        print(f"  置信度: {result['confidence']:.2%}")
        print(f"  各类别概率:")
        for cat, prob in list(result['all_probabilities'].items())[:3]:
            print(f"    {cat}: {prob:.2%}")
    
    print("\n" + "=" * 60)
    
    # 保存和加载测试
    classifier.save_model("classifier_model.pkl")
    
    # 创建新分类器并加载
    new_classifier = DocumentClassifier()
    new_classifier.load_model("classifier_model.pkl")
    
    # 验证加载成功
    result = new_classifier.classify("线性代数和矩阵运算")
    print(f"\n加载模型后测试:")
    print(f"  文档: 线性代数和矩阵运算")
    print(f"  预测类别: {result['category']}")
    print(f"  置信度: {result['confidence']:.2%}")
    
    print("\n" + "=" * 60)


if __name__ == "__main__":
    demo()