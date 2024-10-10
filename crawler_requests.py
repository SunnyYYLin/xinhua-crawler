import json
import os
import requests
from bs4 import BeautifulSoup
from datetime import datetime
from queue import Queue
import jieba
import random
import re

TIME_PATTERN = '%Y-%m-%d %H:%M:%S'
SEARCH_PATTERN = 'https://so.news.cn/getNews?lang={lang}&curPage={page}&\
searchFields={only_title}&sortField={by_relativity}&keyword={keyword}'
MAX_PAGES = 20

class News:
    """News类，用于存储新闻的相关信息。

    Attrs:
        title (str): 新闻标题。
        content (str): 新闻内容。
        editor (str): 编辑者。
        site (str): 新闻来源网站。
        time (str): 新闻发布时间。
        url (str): 新闻链接。
    """
    def __init__(self, *, title=None, content=None, editor=None, site=None, time=None, url=None) -> None:
        self.title = title
        self.content = content
        self.editor = editor
        self.site = site
        self.time = time
        self.url = url

class NewsCrawler:
    """NewsCrawler类用于抓取新闻数据。
    Attrs:
        to_visit (Queue[News]): 待访问的新闻队列。
        data (list[News]): 已抓取的新闻数据列表。
        visited_urls (set[str]): 已访问的新闻URL集合。
        language (str): 抓取新闻的语言。
        max_news (int): 最大抓取新闻数量。
        init_keyword (str): 初始搜索关键词。
    Methods:
        __init__(self, language, max_news, init_keyword='1'):初始化NewsCrawler实例。
        crawl(self):
            开始抓取新闻数据。
        search(self, keyword: str):
            根据关键词搜索新闻。
        parse_search(self, response: requests.Response) -> list[str]|None:
            解析搜索结果，返回新闻列表。
        is_news(soup: BeautifulSoup) -> bool:
            判断页面内容是否为新闻。
        get_news(self, soup: BeautifulSoup, news: News) -> News:
            从页面内容中提取新闻详细信息。
        save_data(self, foldername: str) -> None:
            将抓取的数据保存到指定文件夹。
        load_data(self, foldername: str) -> None:
            从指定文件夹加载已保存的数据。
    """
    def __init__(self, language, max_news, init_keyword='1') -> None:
        self.to_visit: Queue[News] = Queue()
        self.data: list[News] = []
        self.visited_urls: set[str] = set()
        self.language = language
        self.max_news = max_news
        self.init_keyword = init_keyword
        
    def crawl(self):
        self.search(self.init_keyword)
        while True:
            news = self.to_visit.get()
            try:
                response = requests.get(news.url, timeout=3)
                soup = BeautifulSoup(response.text, 'html.parser')
                if self.is_news(soup):
                    news = self.get_news(soup, news)
                self.visited_urls.add(news.url)
                while self.to_visit.empty():
                    keyword = random.choice(jieba.lcut(news.title))
                    self.search(keyword)
                if len(self.data) >= self.max_news:
                    break
            except TimeoutError as e:
                print(f"Timeout: {e} News: {news['title']}")
        
    def search(self, keyword: str):
        page = 1
        while page < MAX_PAGES:
            response = requests.get(SEARCH_PATTERN.format(lang=self.language, 
                                                          page=page,
                                                          only_title='title',
                                                          by_relativity='relativity',
                                                          keyword=keyword))
            print(f"Searching for {keyword} Page {page}")
            news_list = self.parse_search(response)
            if not news_list:
                break
            for news in news_list:
                self.to_visit.put(news)
            page += 1
            
    def parse_search(self, response: requests.Response) -> list[str]|None:
        news_list = []
        try:
            data = response.json()
            for news in data['content']['results']:
                title = re.sub(r'<.*?>', '', news['title'])
                news = News(title=title, 
                            time=news['pubtime'],
                            site=news['sitename'],
                            url=news['url'])
                if news.url in self.visited_urls:
                    continue
                news_list.append(news)
            return news_list
        except Exception as e:
            print(e)
            return None
        
    @staticmethod
    def is_news(soup: BeautifulSoup) -> bool:
        title = soup.find('span', class_='title')
        detail = soup.find('div', id='detail')
        if title and detail:
            return True
        else:
            return False
            
    def get_news(self, soup: BeautifulSoup, news: News) -> News:
        detail = soup.find('div', id='detail')
        paragraphs = detail.find_all('p')
        news.content = '\n'.join([p.text.strip() for p in paragraphs])
        editor = soup.find('span', class_='editor')
        news.editor = editor.text.strip() if editor else None
        self.data.append(news)
        print(f"Totoal: {len(self.data)} Collected {news.title}")
        return news
    
    def save_data(self, foldername: str) -> None:
        data_path = os.path.join(foldername, 'data.json')
        with open(data_path, 'w', encoding='utf-8') as f:
            json.dump([news.__dict__ for news in self.data],
                      f, ensure_ascii=False, indent=4)
            
    def load_data(self, foldername: str) -> None:
        data_path = os.path.join(foldername, 'data.json')
        try:
            with open(data_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                self.data = [News(**news) for news in data]
        except Exception as e:
            print(f"Failed to load data: {e}")