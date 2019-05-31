from selenium import webdriver
from selenium.webdriver.support.wait import WebDriverWait
import time
from lxml import etree
import json
#
# brower = webdriver.Chrome()
# brower.get("http://www.baidu.com/")
# # data = brower.find_element_by_id("wrapper").text
# print(brower.title)
# # brower.save_screenshot('baidu.png')
# brower.find_element_by_id("kw").send_keys("美女")
# # time.sleep(5)
# brower.find_element_by_id("su").click()
# time.sleep(5)
# brower.save_screenshot('meinu.png')
# print(brower.page_source)


class DouYu(object):
    def __init__(self):
        self.start_url="https://www.douyu.com/g_LOL"
        self.brower = webdriver.Chrome()


    def parse_data(self):
        a = 100
        b = 0
        while True:

            # js_ = "document.documentElement.scrollTop=%d"%a
            js_ = "window.scrollTo(%d,document.body.scrollHeight=%d)" % (b, a)
            print(js_)
            self.brower.execute_script(js_)
            time.sleep(2)
            # a += 250
            # b += 250
            a += 500
            b += 500
            if b == 8000:
                break

        div_list = self.brower.find_elements_by_xpath("//ul[@class='layout-Cover-list']/li")
        content = []

        for list in div_list:
            item = {}
            item['img'] = list.find_element_by_xpath(".//div[@class='DyListCover-imgWrap']//img").get_attribute('src')
            item['img'] = item['img'] if len(item['img']) > 0 else None
            item['title'] = list.find_element_by_xpath(".//a//div[@class='DyListCover-info']/h3").get_attribute("title")
            item['title'] = item['title'] if len(item['title']) >0 else None
            item['type'] = list.find_element_by_xpath(".//a//div[@class='DyListCover-info']/span[@class='DyListCover-zone']").text
            item['type'] = item['type'] if len(item['type'] ) >0 else None
            item['zhubo'] = list.find_element_by_xpath(".//a//div[@class='DyListCover-info']/h2").text
            item['zhubo'] = item['zhubo'] if len(item['zhubo']) else None
            item['hot'] = list.find_element_by_xpath(".//a//div[@class='DyListCover-info']/span[@class='DyListCover-hot']").text
            item['hot'] = item['hot'] if len(item['hot']) else None
            content.append(item)
        next_url = self.brower.find_elements_by_xpath("//li[@title='下一页']/span")
        next_url = next_url[0] if len(next_url) >0 else None
        return content,next_url

    def save_data(self,data):
        with open('douyu1.txt','a',encoding='utf-8') as f:
            for i in data:
                f.write(json.dumps(i,ensure_ascii=False))
                f.write('\n')

    def run(self):
        #1 准备start_url
        #2 发送url请求
        self.brower.get(self.start_url)
        #3 解析数据
        # time.sleep(15)
        data,next_url = self.parse_data()
        print(next_url)
        self.save_data(data)
        while next_url is not None:
            print('*'*20)
            next_url.click()
            time.sleep(10)
            data, next_url = self.parse_data()
            self.save_data(data)


if __name__ == '__main__':
    douyu = DouYu()
    douyu.run()