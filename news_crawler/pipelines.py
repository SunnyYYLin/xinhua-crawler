# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
import json
import os

class NewsPipeline:
    def __init__(self, output_dir):
        self.output_dir = output_dir
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)
        
        self.cache = open(os.path.join(self.output_dir, 'data_cache.jsonl'), 'w', encoding='utf-8')
        self.file = open(os.path.join(self.output_dir, 'data.json'), 'w', encoding='utf-8')
        self.news_list = []

    @classmethod
    def from_crawler(cls, crawler):
        output_dir = crawler.settings.get('OUTPUT_DIR', '../data')
        return cls(output_dir)

    def process_item(self, item, spider):
        self.news_list.append(dict(item))
        self.cache.write(json.dumps(dict(item), ensure_ascii=False, indent=4) + '\n')
        return item

    def close_spider(self, spider):
        json.dump(self.news_list, self.file, ensure_ascii=False, indent=4)
        self.file.close()