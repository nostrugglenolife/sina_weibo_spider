# -*- coding: utf-8 -*-
BOT_NAME = ['tweetsSpider', 'informationSpider']

SPIDER_MODULES = ['sina_spider.spiders']
NEWSPIDER_MODULE = 'sina_spider.spiders'

DOWNLOADER_MIDDLEWARES = {
    "sina_spider.middleware.UserAgentMiddleware": 401,
    "sina_spider.middleware.CookiesMiddleware": 402,
}
ITEM_PIPELINES = {"sina_spider.pipelines.MongoDBPipleline": 100}

SCHEDULER = 'scrapy_redis.scheduler.Scheduler'
DUPEFILTER_CLASS = 'scrapy_redis.dupefilter.RFPDupeFilter'
SCHEDULER_PERSIST = True
SCHEDULER_QUEUE_CLASS = 'scrapy_redis.queue.SpiderPriorityQueue'
# 可选的先进先出排序
# SCHEDULER_QUEUE_CLASS = 'scrapy_redis.queue.SpiderQueue'
REDIE_URL = None
# REDIS_HOST = '192.168.1.199'
REDIS_HOST = '127.0.0.1'
REDIS_PORT = 6379

DOWNLOAD_DELAY = 3  # 间隔时间
# COMMANDS_MODULE = 'sina_spider.commands'
# LOG_LEVEL = 'INFO'  # 日志级别
# CONCURRENT_REQUESTS = 1
# CONCURRENT_ITEMS = 1
# CONCURRENT_REQUESTS_PER_IP = 1
