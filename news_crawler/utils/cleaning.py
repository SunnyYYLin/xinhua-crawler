import re

def clean_cn(text: str) -> str:
    text = re.sub(r'\s+', ' ', text.strip())    # 去除多余的空格和换行符
    # 替换中文标点为标准形式
    text = re.sub(r'[！!]', '！', text)  # 统一感叹号
    text = re.sub(r'[，,]', '，', text)   # 统一逗号
    text = re.sub(r'[；;]', '；', text)   # 统一分号
    text = re.sub(r'[：:]', '：', text)   # 统一冒号
    text = re.sub(r'[？?]', '？', text)  # 统一问号
    text = re.sub(r'[\u3000]', ' ', text)  # 中文全角空格替换为半角空格
    text = re.sub(r'[“”‘’]', '', text)    # 去除引号
    text = re.sub(r'[^，。？！：；\u4e00-\u9fa50-9]', '', text)  # 保留中文字符、标点和阿拉伯数字
    return text

def clean_en(text: str) -> str:
    text = re.sub(r'\s+', ' ', text.strip())    # 去除多余的空格和换行符
    text = re.sub(r'[\"\'`]', '', text)    # 去除双引号、单引号、反引号
    text = re.sub(r'[^a-zA-Z0-9\s.,;!?-]', '', text)  # 保留英文字符、标点和阿拉伯数字
    return text