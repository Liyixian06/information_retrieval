import requests
from bs4 import BeautifulSoup
from lxml import html
import random
import time
from pprint import pprint
import csv
import datetime

user_agents = [ 
    "Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1; SV1; AcooBrowser; .NET CLR 1.1.4322; .NET CLR 2.0.50727)", 
    "Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 6.0; Acoo Browser; SLCC1; .NET CLR 2.0.50727; Media Center PC 5.0; .NET CLR 3.0.04506)", 
    "Mozilla/4.0 (compatible; MSIE 7.0; AOL 9.5; AOLBuild 4337.35; Windows NT 5.1; .NET CLR 1.1.4322; .NET CLR 2.0.50727)", 
    "Mozilla/5.0 (Windows; U; MSIE 9.0; Windows NT 9.0; en-US)", 
    "Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 6.1; Win64; x64; Trident/5.0; .NET CLR 3.5.30729; .NET CLR 3.0.30729; .NET CLR 2.0.50727; Media Center PC 6.0)", 
    "Mozilla/5.0 (compatible; MSIE 8.0; Windows NT 6.0; Trident/4.0; WOW64; Trident/4.0; SLCC2; .NET CLR 2.0.50727; .NET CLR 3.5.30729; .NET CLR 3.0.30729; .NET CLR 1.0.3705; .NET CLR 1.1.4322)", 
    "Mozilla/4.0 (compatible; MSIE 7.0b; Windows NT 5.2; .NET CLR 1.1.4322; .NET CLR 2.0.50727; InfoPath.2; .NET CLR 3.0.04506.30)", 
    "Mozilla/5.0 (Windows; U; Windows NT 5.1; zh-CN) AppleWebKit/523.15 (KHTML, like Gecko, Safari/419.3) Arora/0.3 (Change: 287 c9dfb30)", 
    "Mozilla/5.0 (X11; U; Linux; en-US) AppleWebKit/527+ (KHTML, like Gecko, Safari/419.3) Arora/0.6", 
    "Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US; rv:1.8.1.2pre) Gecko/20070215 K-Ninja/2.1.1", 
    "Mozilla/5.0 (Windows; U; Windows NT 5.1; zh-CN; rv:1.9) Gecko/20080705 Firefox/3.0 Kapiko/3.0", 
    "Mozilla/5.0 (X11; Linux i686; U;) Gecko/20070322 Kazehakase/0.4.5", 
    "Mozilla/5.0 (X11; U; Linux i686; en-US; rv:1.9.0.8) Gecko Fedora/1.9.0.8-1.fc10 Kazehakase/0.5.6", 
    "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/535.11 (KHTML, like Gecko) Chrome/17.0.963.56 Safari/535.11", 
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_7_3) AppleWebKit/535.20 (KHTML, like Gecko) Chrome/19.0.1036.7 Safari/535.20", 
    "Opera/9.80 (Macintosh; Intel Mac OS X 10.6.8; U; fr) Presto/2.9.168 Version/11.52"
    ]
request_headers = {
    "User-Agent": random.choice(user_agents),
    "Connection": "keep-alive",
    "Referer":
        "https://www.douban.com"
}

def get_article_links(uri):
    web_data = requests.get(url=uri, headers = request_headers)
    status_code = web_data.status_code
    if status_code == 200:
        html_txt = web_data.text
        # 解析为 soup 文档
        soup = BeautifulSoup(html_txt, "lxml")
        # 定位本页上所有 12 篇文章的 url
        article_elements = soup.select("a.original_imgArea_cover")
        # 遍历每篇文章
        for article_element in article_elements:
            # 提取 href 属性值
            article_href = "https://www.gcores.com" + article_element.get('href').strip()
            # 获取每篇文章详情页的信息
            get_article_info(article_href)
            time.sleep(0.5)
    else:
        print("wrong status code!")

def get_article_info(article_href):
    web_data = requests.get(url=article_href, headers = request_headers)
    status_code = web_data.status_code
    if status_code == 200:
        html_txt = web_data.text
    else:
        print("wrong status code!")
    soup = BeautifulSoup(html_txt, "lxml")
    title = soup.find("h1", class_="originalPage_title").string
    date = soup.find(class_="me-2 u_color-gray-info").attrs['title']
    date = datetime.datetime.strptime(date, "%Y-%m-%d %H:%M:%S")
    segments = soup.find_all("span", attrs={"data-text": "true"})
    segments_txt = []
    for i in segments:
        segments_txt.append(i.string.replace('\n','').replace('\r','').replace('\t',''))
    content = ''.join(segments_txt)
    links = []
    contain_urls = soup.find_all("a", class_="md-link")
    for i in contain_urls:
        links.append(i.attrs["href"])
    
    article_info = {
        "title": title,
        "url": article_href,
        "date": date,
        "content": content,
        "links": links
    }
    pprint(article_info)
    with open('gcore_article.csv', 'a', encoding='gb18030', newline='') as f:
        csv_writer = csv.DictWriter(f, fieldnames=article_info.keys())
        csv_writer.writerow(article_info)

if __name__ == "__main__":
    page_max = 150
    urls = [f'https://www.gcores.com/articles?page={i}' for i in range(1, page_max+1)]
    csv_headers = ['title','url','date','content','links']
    with open('gcore_article.csv', 'w', encoding='gb18030', newline='') as f:
        csv_writer = csv.writer(f)
        csv_writer.writerow(csv_headers)
    page = 1
    for uri in urls:
        print("page {}/{}".format(page, page_max))
        page += 1
        get_article_links(uri)
        time.sleep(1)
    print('end...')