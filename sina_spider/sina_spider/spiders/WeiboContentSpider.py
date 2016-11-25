# encoding=utf-8
import re
import time
# from scrapy_redis.spiders import RedisSpider
from sina_spider.spiders.m_spiders import RedisSpider
from scrapy.http import Request
from sina_spider.items import InformationItem, ContentsItem


# 获取用户的基本资料和所有微博内容
class Spider(RedisSpider):
    name = "WeiboContentSpider"
    host = "http://weibo.cn"
    redis_key = "tweetsSpider:my_focus_urls"

    def parse(self, response):
        info_url = response.xpath("//div[@class='ut']/a[text()='资料']/@href").extract()[0]
        yield Request(url=self.host + info_url, callback=self.parse_info)
        url = response.xpath("//div[@class='pms']/a[text()='原创']/@href").extract()[0]
        yield Request(url=self.host + url, callback=self.parse_content)

    # 解析用户的个人资料
    def parse_info(self, response):
        info_dict = {}
        info_dict['url'] = response.url
        basic_info_div_text = response.xpath("//div[text()='基本信息']/following-sibling::div[1]").extract()[0]
        if basic_info_div_text:
            basic_info_li = basic_info_div_text.replace('<div class="c">', '').replace('</div>', '').strip(
                    "<br>").split("<br>")
            if "标签" in basic_info_div_text:
                from lxml import etree
                dom = etree.HTML(basic_info_li[-1])
                labels_li = dom.xpath('string(.)').replace("更多>>", "").split(":")
                k = labels_li[0]
                v = labels_li[1].strip()
                info_dict[k] = v
                basic_info_li = basic_info_li[:-1]  # 去掉最后一个元素
                pass
            for string in basic_info_li:
                if ":" in string:
                    new_l = string.split(":")
                    k = new_l[0]
                    v = new_l[1].strip()
                    info_dict[k] = v
                elif "：" in string:
                    new_l = string.split("：")
                    k = new_l[0]
                    v = new_l[1].strip()
                    info_dict[k] = v

        edu_div_text = response.xpath("//div[text()='学习经历']/following-sibling::div[1]/text()").extract()
        if edu_div_text:
            edu_infos = edu_div_text[0].replace("<br/>", " ")
            info_dict["学习经历"] = edu_infos.replace("&nbsp;", " ")

        work_div_text = response.xpath("//div[text()='工作经历']/following-sibling::div[1]/text()").extract()
        if work_div_text:
            work_infos = work_div_text[0].replace("<br/>", " ")
            info_dict["工作经历"] = work_infos.replace("&nbsp;", " ")
        info = InformationItem()
        info['informations'] = info_dict
        yield info

    # 解析微博正文内容
    def parse_content(self, response):
        content_items = ContentsItem()
        content_dict = {}
        content_divs = response.xpath("//div[@class='c' and @id]")
        if content_divs:
            for content_div in content_divs:
                content = ""
                for string in content_div.xpath("div[1]/span//text()").extract():
                    content += string
                content_dict['内容'] = content
                others = content_div.xpath("string(.)").extract()[0]
                content_dict['点赞数'] = re.search(r'赞\[(\d+)]', others).group(1) if re.search(r'赞\[(\d+)]', others) else None
                content_dict['转发数'] = re.search(r'转发\[(\d+)]', others).group(1) if re.search(r'赞\[(\d+)]', others) else None
                content_dict['评论数'] = re.search(r'评论\[(\d+)]', others).group(1) if re.search(r'赞\[(\d+)]', others) else None
                time_and_platform = response.xpath("//span[@class='ct']/text()").extract()[0]
                last_item = time_and_platform.split("来自")[-1]
                content_dict['发布工具'] = last_item
                d_time = time_and_platform.split("来自")[0]
                # 统一格式化日期
                if "今天" in d_time:
                    d_time = d_time.replace("今天", "%s" % time.strftime("%Y-%m-%d", time.localtime()))
                elif not re.match(r"\d+-\d+-\d+", d_time):
                    d_time = time.strftime("%Y", time.localtime()) + "-" + d_time
                content_dict['时间'] = d_time
                content_dict['昵称'] = response.xpath("//div[@class='ut']/span[1]/text()[1]").extract()[0].split("&nbsp;")[0]
                content_dict['weibo_id'] = response.url.replace("http://weibo.cn/", "").split("?")[0]
                content_items['contents'] = content_dict
                yield content_items
        # 获取下一页的链接,没有代表到了最后一页
        result = response.xpath("//div[@id='pagelist']/form/div/a/@href").extract()
        if result:
            yield Request(url=self.host + result, callback=self.parse_content)
