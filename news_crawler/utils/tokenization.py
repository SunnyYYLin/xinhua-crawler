# File: xinhua-crawler/news_crawler/utils/tokenization.py

import re
import regex
import jieba

# Precompile regex patterns for performance
CN_PUNCTUATION_PATTERN = regex.compile(r'\p{P}')
EN_PUNCTUATION_PATTERN = re.compile(r'[^\w\s]')
SENTENCE_ENDINGS_CN = re.compile(r'[。！？]')
SENTENCE_ENDINGS_EN = re.compile(
    r'(?<!\w\.\w.)(?<![A-Z][a-z]\.)(?<=\.|\?|\!)(?=\s|$)'
)
NON_CN_PATTERN = regex.compile(r'[^\p{Han}]')
NON_EN_PATTERN = re.compile(r'[^a-zA-Z]')

def tokenize_cn(text: str, min_len: int = 5, only_cnchr: bool=False) -> list[list[str]]:
    """
    Tokenize Chinese text into a list of tokenized sentences.
    
    Args:
        text (str): The Chinese text to tokenize.
        min_len (int): Minimum number of tokens required for a sentence.
        
    Returns:
        List[List[str]]: Tokenized sentences.
    """
    sentences = split_sentences_cn(text)
    
    tokenized_sentences = []
    for sentence in sentences:
        tokens = jieba.lcut(sentence)
        tokens = [CN_PUNCTUATION_PATTERN.sub('', token) for token in tokens]
        if only_cnchr:
            tokens = [token for token in tokens if not NON_CN_PATTERN.search(token)]
        tokens = [token for token in tokens if token]
        if len(tokens) >= min_len:
            tokenized_sentences.append(tokens)
    
    return tokenized_sentences

def tokenize_en(text: str, min_len: int = 5) -> list[list[str]]:
    """
    Tokenize English text into a list of tokenized sentences.
    
    Args:
        text (str): The English text to tokenize.
        min_len (int): Minimum number of tokens required for a sentence.
        
    Returns:
        List[List[str]]: Tokenized sentences.
    """
    sentences = split_sentences_en(text)
    
    tokenized_sentences = []
    for sentence in sentences:
        tokens = sentence.split()
        tokens = [EN_PUNCTUATION_PATTERN.sub('', token).lower() for token in tokens]
        tokens = [token for token in tokens if token]
        if len(tokens) < min_len:
            continue
        # Filter out sentences with excessive numeric content
        num_tokens = sum(token.isdigit() for token in tokens)
        if num_tokens > len(tokens) // 2:
            continue
        tokenized_sentences.append(tokens)
    
    return tokenized_sentences

def split_sentences_cn(text: str) -> list[str]:
    """
    Split Chinese text into sentences based on punctuation.
    
    Args:
        text (str): The Chinese text to split.
        
    Returns:
        List[str]: List of sentences.
    """
    sentences = SENTENCE_ENDINGS_CN.split(text)
    sentences = [s.strip() for s in sentences if s.strip()]
    return sentences

def split_sentences_en(text: str) -> list[str]:
    """
    Split English text into sentences based on punctuation.
    
    Args:
        text (str): The English text to split.
        
    Returns:
        List[str]: List of sentences.
    """
    sentences = SENTENCE_ENDINGS_EN.split(text)
    sentences = [s.strip() for s in sentences if s.strip()]
    return sentences
