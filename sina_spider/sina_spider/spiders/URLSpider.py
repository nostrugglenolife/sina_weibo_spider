# encoding=utf-8

from redis import Redis
# from scrapy_redis.spiders import RedisSpider
from scrapy.spiders import Spider

from sina_spider.spiders.m_spiders import RedisSpider
from scrapy.http import Request


class Spider(RedisSpider):
    name = "UrlSpider"
    host = "http://weibo.cn"
    redis_key = "tweetsSpider:my_focus_urls"
    # start_urls = "http://weibo.cn/"
    my_focus_urls = []
    r = Redis()

    # 获取指向用户关注页面的url,第二轮开始变成获取指向该用户粉丝页面链接
    def parse(self, response):
        to_focus_url = response.xpath("//div[@class='tip2']/a[2]/@href").extract()[0]
        yield Request(url=self.host + to_focus_url, callback=self.parse_my_focus_urls)

    # 获取用户关注的所有的人的url,第二轮开始变成获取该用户粉丝
    def parse_my_focus_urls(self, response):
        self.my_focus_urls += response.xpath("//table//td[1]/a/@href").extract()
        result = response.xpath("//div[@id='pagelist']/form/div/a/@href").extract()
        if result:
            yield Request(url=self.host + result, callback=self.parse_my_focus_urls)
        else:
            for my_focus_url in self.my_focus_urls:
                self.r.lpush("tweetsSpider:my_focus_urls", my_focus_url)