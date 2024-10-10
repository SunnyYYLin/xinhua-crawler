# File: xinhua-crawler/news_crawler/pipelines.py

from .utils.cleaning import clean_cn, clean_en
import json
import os

class NewsPipeline:
    def __init__(self, output_dir, language, keep_punc):
        self.output_dir = output_dir
        self.language = language
        self.keep_punc = keep_punc
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)
        
        self.cache = open(os.path.join(self.output_dir, 'data_cache.jsonl'), 'w', encoding='utf-8')
        self.file = open(os.path.join(self.output_dir, 'data.json'), 'w', encoding='utf-8')
        self.news_list = []

    @classmethod
    def from_crawler(cls, crawler):
        # 从 crawler 的 settings 和 spider 中获取输出目录和语言
        output_dir = crawler.settings.get('OUTPUT_DIR', '../data')
        language = crawler.spider.language
        keep_punc = crawler.settings.get('KEEP_PUNC', 'true')
        keep_punc = keep_punc.lower() == 'true'
        return cls(output_dir, language, keep_punc)

    def process_item(self, item, spider):
        # 直接使用 self.language 来选择清洗函数
        content = item.get('content', '')
        if self.language == 'cn':
            content = clean_cn(content, self.keep_punc)
        elif self.language == 'en':
            content = clean_en(content, self.keep_punc)
        else:
            raise ValueError(f'Unsupported language: {self.language}')

        if content:
            # 更新 item 的内容
            item['content'] = content
            # 将 item 添加到新闻列表并缓存
            self.news_list.append(dict(item))
            self.cache.write(json.dumps(dict(item), ensure_ascii=False, indent=4) + '\n')
            return item
        else:
            # 如果内容为空，则忽略该 item
            spider.logger.warning(f'Empty content for {item["url"]}')
            return None

    def close_spider(self, spider):
        # 在关闭爬虫时，将新闻列表保存到最终文件
        json.dump(self.news_list, self.file, ensure_ascii=False, indent=4)
        # 删除缓存文件
        os.remove(os.path.join(self.output_dir, 'data_cache.jsonl'))
        
        self.file.close()
        self.cache.close()