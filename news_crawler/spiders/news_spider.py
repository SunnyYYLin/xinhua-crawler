import scrapy
from scrapy import Request
from ..items import NewsItem
from bs4 import BeautifulSoup
import json
import random
import re
import jieba

TIME_PATTERN = '%Y-%m-%d %H:%M:%S'
SEARCH_PATTERN = 'https://so.news.cn/getNews?lang={lang}&curPage={page}\
&searchFields={only_title}&sortField={by_relativity}&keyword={keyword}'

# 默认参数
DEFAULT_LANGUAGE = 'cn'
DEFAULT_MAX_PAGES = 50
DEFAULT_NEWS_BATCH_SIZE = 100
DEFAULT_ONLY_TITLE = 0
DEFAULT_BY_RELATIVITY = 1

class NewsSpider(scrapy.Spider):
    """
    NewsSpider 是一个 Scrapy 爬虫类，用于从 news.cn 和 so.news.cn 网站上抓取新闻数据。
    属性:
        name (str): 爬虫名称。
        allowed_domains (list): 允许爬取的域名列表。
        start_keyword (str): 初始关键词。
        language (str): 爬取的语言（'cn' 或 'en'）。
        max_pages (int): 最大爬取页数。
        news_batch_size (int): 每批处理的新闻数量。
        only_title (int): 是否仅搜索标题。
        by_relativity (int): 是否按相关性排序。
        visited_urls (set): 已访问的 URL 集合。
        news_queue (list): 新闻队列。
    方法:
        __init__(self, start_keyword, language, max_pages, news_batch_size, only_title, by_relativity, *args, **kwargs):
            初始化 NewsSpider 实例。
        start_requests(self):
            开始爬取请求，使用初始关键词。
        search(self, page, keyword):
            根据关键词和页码生成搜索请求。
        parse_search(self, response):
            解析搜索结果页面，提取新闻信息并加入队列。
        process_news_queue(self):
            处理新闻队列中的新闻，生成新闻详情请求。
        _parse_news_cn(self, response):
            解析中文新闻详情页面，提取新闻内容。
        _parse_news_en(self, response):
            解析英文新闻详情页面，提取新闻内容。
        _gen_keyword_cn(self, title):
            根据中文标题生成关键词。
        _gen_keyword_en(self, title):
            根据英文标题生成关键词。
        is_news(soup):
            静态方法，判断页面是否为新闻页面。
    """
    
    name = 'news_spider'
    allowed_domains = ['news.cn', 'so.news.cn']
    
    def __init__(self, start_keyword='1', language=DEFAULT_LANGUAGE, max_pages=DEFAULT_MAX_PAGES,
                 news_batch_size=DEFAULT_NEWS_BATCH_SIZE, only_title=DEFAULT_ONLY_TITLE,
                 by_relativity=DEFAULT_BY_RELATIVITY, *args, **kwargs):
        super(NewsSpider, self).__init__(*args, **kwargs)
        
        # 初始化参数
        self.start_keyword = start_keyword
        self.language = language
        self.max_pages = int(max_pages)
        self.news_batch_size = int(news_batch_size)
        self.only_title = int(only_title)
        self.by_relativity = int(by_relativity)
        
        if self.language == 'cn':
            self.parse_news = self._parse_news_cn
            self.gen_keyword = self._gen_keyword_cn
        elif self.language == 'en':
            self.parse_news = self._parse_news_en
            self.gen_keyword = self._gen_keyword_en
        else:
            raise ValueError(f"Unsupported language: {self.language}")

        self.visited_urls = set()
        self.news_queue = []

    def start_requests(self):
        # 使用初始关键词 '1' 开始爬取
        keyword = self.start_keyword
        for page in range(1, self.max_pages+1):
            yield from self.search(page, keyword)
            
    def search(self, page, keyword):
        url = SEARCH_PATTERN.format(
            lang=self.language,
            page=page,
            only_title=self.only_title,
            by_relativity=self.by_relativity,
            keyword=keyword
        )
        yield Request(url, 
                       callback=self.parse_search, 
                       meta={'keyword': keyword, 'page': page},
                       priority=-page)

    def parse_search(self, response):
        keyword = response.meta['keyword']
        page = response.meta['page']
        self.logger.info(f"Searching for {keyword} Page {page}")
        item = None
        try:
            data = json.loads(response.text)
            news_list = data.get('content', {}).get('results', [])
            if not news_list:
                self.logger.warning(f"No news found for keyword '{keyword}' on page {page}.")
                return
            for news in news_list:
                url = news.get('url')
                if not url or url in self.visited_urls:
                    continue
                self.visited_urls.add(url)
                title = re.sub(r'<.*?>', '', news.get('title', ''))
                item = NewsItem()
                item['title'] = title.replace('&nbsp', ' ').replace(';', '').strip()
                item['time'] = news.get('pubtime')
                item['site'] = news.get('sitename')
                item['url'] = url
                self.news_queue.append(item)  # 将新闻加入队列
                
            # 如果队列大小超过一定数量，处理队列中的新闻
            if len(self.news_queue) >= self.news_batch_size:
                yield from self.process_news_queue()

                if item and item.get('title'):
                    title = item['title']
                    keyword = self.gen_keyword(title)
                else:
                    self.logger.warning("No item found to extract keyword from.")
                for page in range(1, self.max_pages+1):
                    yield from self.search(page, keyword)
                    
        except Exception as e:
            self.logger.error(f"Error parsing search response: {e}")

    def process_news_queue(self):
        while self.news_queue:
            news_item = self.news_queue.pop(0)
            yield Request(news_item['url'], 
                          callback=self.parse_news, 
                          meta={'item': news_item})
            
    def _parse_news_cn(self, response):
        item = response.meta['item']
        soup = BeautifulSoup(response.text, 'html.parser')
        if self.is_news(soup):
            detail = soup.find('div', id='detail')
            paragraphs = detail.find_all('p')
            item['content'] = '\n'.join([p.text.strip() for p in paragraphs])
            self.logger.info(f"Collected {item['title']}")
            yield item
        else:
            self.logger.warning(f"Not a news page: {item['url']}")
    
    def _parse_news_en(self, response):
        item = response.meta['item']
        soup = BeautifulSoup(response.text, 'html.parser')
        if self.is_news(soup):
            detail = soup.find('div', id='detail')
            paragraphs = detail.find_all('p')
            item['content'] = '\n'.join([p.text.strip() for p in paragraphs])
            self.logger.info(f"Collected {item['title']}")
            yield item
        else:
            self.logger.warning(f"Not a news page: {item['url']}")
            
    def _gen_keyword_cn(self, title: str):
        return random.choice(jieba.lcut(title))
    
    def _gen_keyword_en(self, title: str):
        return random.choice(title.split(' '))

    @staticmethod
    def is_news(soup):
        detail = soup.find('div', id='detail')
        return bool(detail)