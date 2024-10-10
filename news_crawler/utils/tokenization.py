import re
import regex
import jieba

def tokenize_cn(news: str, min_len: int=5) -> list[list[str]]:
    sentences = split_sentences_cn(news)
    
    # 对每个句子进行分词
    tokenized_sentences = []
    for sentence in sentences:
        tokens = jieba.lcut(sentence)  # 使用 jieba 进行分词
        # 使用 re.sub 删除所有标点符号，匹配 Unicode 标点类 \p{P}
        tokens = [regex.sub(r'\p{P}', '', token) for token in tokens]
        tokens = [token for token in tokens if token]  # 保留非空词
        if len(tokens) < min_len:
            continue
        tokenized_sentences.append(tokens)
    
    return tokenized_sentences

def tokenize_en(news: str, min_len: int=5) -> list[list[str]]:
    sentences = split_sentences_en(news)
    
    # 对每个句子进行分词
    tokenized_sentences = []
    for sentence in sentences:
        tokens = sentence.split()
        # 删除所有的标点符号
        tokens = [re.sub(r'[^\w\s]', '', token) for token in tokens]
        tokens = [token.lower() for token in tokens if token]  # 保留非空词并转小写
        if len(tokens) < min_len:
            continue
        nums = [token for token in tokens if token.isdigit()]
        if len(nums) > len(tokens) // 2:
            continue
        tokenized_sentences.append(tokens)
    
    return tokenized_sentences

def split_sentences_cn(text: str) -> list[str]:
    # 使用正则表达式匹配句子的结束符号：句号、问号、感叹号
    sentence_endings = r'[。！？]'
    sentences = re.split(sentence_endings, text)
    
    # 去掉每个句子的前后空白字符，并过滤掉空字符串
    sentences = [s.strip() for s in sentences if s.strip()]
    
    return sentences

def split_sentences_en(text: str) -> list[str]:
    # 使用正则表达式匹配句子结束符：句号、问号、感叹号，后面可能跟着引号或括号
    sentence_endings = r'(?<!\w\.\w.)(?<![A-Z][a-z]\.)(?<=\.|\?|\!)(?=\s|$)'
    sentences = re.split(sentence_endings, text)
    
    # 去掉每个句子的前后空白字符
    sentences = [s.strip() for s in sentences if s.strip()]
    
    return sentences
