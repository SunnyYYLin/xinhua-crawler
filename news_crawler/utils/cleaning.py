import re
from typing import Pattern

# 预编译正则表达式模式
WHITESPACE_PATTERN: Pattern = re.compile(r'\s+')
CN_PUNCTUATION_UNIFY_PATTERNS = [
    (re.compile(r'[！!]'), '！'),
    (re.compile(r'[，,]'), '，'),
    (re.compile(r'[；;]'), '；'),
    (re.compile(r'[：:]'), '：'),
    (re.compile(r'[？?]'), '？'),
]
CN_FULLWIDTH_SPACE_PATTERN: Pattern = re.compile(r'\u3000')
CN_QUOTES_PATTERN: Pattern = re.compile(r'[“”‘’]')
CN_ALLOWED_CHARS_PATTERN: Pattern = re.compile(r'[^，。？！：；\u4e00-\u9fa50-9]')
EN_QUOTES_PATTERN: Pattern = re.compile(r'[\"\'`]')
EN_ALLOWED_CHARS_PATTERN: Pattern = re.compile(r'[^a-zA-Z0-9\s.,;!?-]')
NUMERIC_PATTERN: Pattern = re.compile(r'\d')  # 用于匹配数字字符的正则表达式

# 设置数字占比的阈值（百分比）
NUMERIC_THRESHOLD = 0.1

def is_numeric_ratio_exceed(text: str, threshold: float = NUMERIC_THRESHOLD) -> bool:
    """
    判断文本中的数字占比是否超过指定阈值。
    
    Args:
        text (str): 要检查的文本。
        threshold (float): 数字占比的阈值。
    
    Returns:
        bool: 如果数字占比超过阈值，则返回 True。
    """
    if not text:
        return False
    
    num_digits = len(NUMERIC_PATTERN.findall(text))
    total_chars = len(text)
    
    if total_chars == 0:
        return False
    
    return (num_digits / total_chars) > threshold

def clean_cn(text: str, keep_punc: bool=True) -> str:
    """
    清洗中文文本，规范标点符号，去除不需要的字符，并修剪空格。
    
    Args:
        text (str): 要清洗的中文文本。
        
    Returns:
        str: 清洗后的中文文本。如果数字占比超过指定阈值，返回空字符串。
    """
    text = text.strip()
    text = WHITESPACE_PATTERN.sub(' ', text)
    
    for pattern, replacement in CN_PUNCTUATION_UNIFY_PATTERNS:
        text = pattern.sub(replacement, text)
    
    text = CN_FULLWIDTH_SPACE_PATTERN.sub(' ', text)
    text = CN_QUOTES_PATTERN.sub('', text)
    text = CN_ALLOWED_CHARS_PATTERN.sub('', text)
    
    # 去掉最后一个句号后的内容
    text = '。'.join(text.split('。')[:-1]) + '。'
    
    # 检查数字占比，如果超过阈值，则返回空字符串
    if is_numeric_ratio_exceed(text):
        return ''
    
    if not keep_punc:
        text = ''.join([char for char in text if char not in '，。？！：；…\u3000'])
    
    return text

def clean_en(text: str, keep_punc: bool=True) -> str:
    """
    清洗英文文本，去除不需要的字符，规范空格，并修剪空格。
    
    Args:
        text (str): 要清洗的英文文本。
        
    Returns:
        str: 清洗后的英文文本。如果数字占比超过指定阈值，返回空字符串。
    """
    text = text.strip()
    text = WHITESPACE_PATTERN.sub(' ', text)
    
    text = EN_QUOTES_PATTERN.sub('', text)
    text = EN_ALLOWED_CHARS_PATTERN.sub('', text)
    
    # 去掉最后一个句号后的内容
    text = '. '.join(text.split('. ')[:-1]) + '. '
    
    # 检查数字占比，如果超过阈值，则返回空字符串
    if is_numeric_ratio_exceed(text):
        return ''
    
    if not keep_punc:
        text = ''.join([char for char in text if char not in ',.!?;: '])
    
    return text