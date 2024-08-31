import threading
import os
import re
import time
import csv
from lxml import etree
from urllib.parse import quote
import requests
import pandas as pd
import jieba
from snownlp import SnowNLP
from wordcloud import WordCloud
import matplotlib.pyplot as plt

# 集成爬虫和数据分析功能，为爬虫设置运行时间，更加方便
def crawComments(cookie, topic):
    comment_number = 0
    headers_com = {
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.45 Safari/537.36',
        'cookie': cookie
    }

    def getArticleId(id_str):
        url_id = "https://weibo.com/ajax/statuses/show?id={}".format(id_str)
        resp_id = requests.get(url_id, headers=headers_com)
        if resp_id is None:
            return 0
        article_id = resp_id.json()["id"]
        return article_id

    def get_one_page(params):
        url = "https://weibo.com/ajax/statuses/buildComments"
        resp = requests.get(url, headers=headers_com, params=params)
        data_list = resp.json()["data"]

        for data in data_list:
            data_dict = {
                "screen_name": data["user"]["screen_name"].strip(),
                "profile_image_url": data["user"]["profile_image_url"],
                "location": data["user"]["location"],
                "created_time": data["created_at"].replace("+0800", ""),
                "text": data["text_raw"].strip().replace('\n', ''),
            }
            nonlocal comment_number
            comment_number = comment_number + 1
            print("已经爬到的评论数：", comment_number)
            print(
                f'昵称：{data_dict["screen_name"]}\n头像：{data_dict["profile_image_url"]}\n地址：{data_dict["location"]}\n发布时间：{data_dict["created_time"]}\n评论内容：{data_dict["text"]}')
            print("=" * 90)
            saveData(data_dict)

        try:
            max_id = resp.json()["max_id"]
            if max_id:
                return max_id
            else:
                return
        except:
            return

    def get_all_data(params):
        max_id = get_one_page(params)
        params["max_id"] = max_id
        params["count"] = 20
        while max_id and not stop_event.is_set():
            time.sleep(1)
            params["max_id"] = max_id
            max_id = get_one_page(params)

    def saveData(data_dict):
        writer.writerow(data_dict)

    def stop_crawling():
        stop_event.set()

    baseUrl = 'https://s.weibo.com/weibo?q={}&Refer=index'
    fileName = topic.replace('#', '')

    # 向csv文件写入表头
    header = ["screen_name", "profile_image_url", "location", "created_time", "text"]
    f = open(f"微博话题/{fileName}.csv", "w", encoding="utf-8-sig", newline="")
    writer = csv.DictWriter(f, header)
    writer.writeheader()

    url = baseUrl.format(quote(topic))

    page = 0
    pageCount = 1

    stop_event = threading.Event()
    timer = threading.Timer(30, stop_crawling)  # 设置3分钟计时器
    timer.start()

    while not stop_event.is_set():
        page = page + 1
        tempUrl = url + '&page=' + str(page)
        print('-' * 36, tempUrl, '-' * 36)
        response = requests.get(tempUrl, headers=headers_com)
        html = etree.HTML(response.text, parser=etree.HTMLParser(encoding='utf-8'))
        count = len(html.xpath('//div[@class="card-wrap"]')) - 2
        for i in range(1, count + 1):
            if stop_event.is_set():
                break

            weibo_url = html.xpath(
                '//div[@class="card-wrap"][' + str(i) + ']/div[@class="card"]/div[1]/div[2]/div[@class="from"]/a/@href')

            if len(weibo_url) == 0:
                continue

            url_str = '.*?com\/\d+\/(.*)\?'
            res = re.findall(url_str, weibo_url[0])
            weibo_id = res[0]
            weibo_uid = weibo_url[0].split('/')[3]

            headers = {
                "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/113.0.0.0 Safari/537.36",
                "x-requested-with": "XMLHttpRequest",
                "referer": "https://weibo.com/{}/{}".format(weibo_uid, weibo_id),
                "cookie": cookie,
                "x-xsrf-token": "aDIwzDqvyb7sb-Qxm_dbqC63"
            }

            try:
                id = getArticleId(weibo_id)
            except:
                continue

            params = {
                'flow': 1,
                "is_reload": 1,
                "id": id,
                "is_show_bulletin": 2,
                "is_mix": 0,
                "count": 10,
                "uid": weibo_uid
            }

            get_all_data(params)

        if stop_event.is_set():
            break

        try:
            if pageCount == 1:
                pageA = html.xpath('//*[@id="pl_feedlist_index"]/div[5]/div/a')[0].text
                pageCount = pageCount + 1
            elif pageCount == 50:
                print('没有下一页了')
                break
            else:
                pageA = html.xpath('//*[@id="pl_feedlist_index"]/div[5]/div/a[2]')[0].text
                pageCount = pageCount + 1
        except:
            print('没有下一页了')
            break

    f.close()
    print("数据爬取完毕。")
    timer.cancel()  # 取消计时器

def drawWordsCloud(topic):
    plt.rcParams['font.sans-serif'] = ['SimHei', 'Songti SC', 'STFangsong']
    plt.rcParams['axes.unicode_minus'] = False  # 用来正常显示负号

    from collections import Counter

    # 修改成读取的文件
    fileName = topic.replace('#', '')
    data = pd.read_csv(f'微博话题/{fileName}.csv')
    save_filename = f'可视化结果/{fileName}/'
    # 确保目录存在，如果不存在则创建
    directory = os.path.join(os.getcwd(), save_filename)
    if not os.path.exists(directory):
        os.makedirs(directory)

    comments = data['text']
    comments = comments.drop_duplicates()

    print(comments.head())

    # 加载停用词表
    stopwords_file = 'stopwords.txt'
    with open(stopwords_file, "r", encoding='utf-8') as words:
        stopwords = [i.strip() for i in words]

    # 添加额外的停用词
    stopwords.extend(
        ['好感兴趣', '已开通超话社区', '转发微博', '图片评论', '已开通了超话社区', '说', '找', '微博', '哥哥'])

    def clean_text(text):
        text = re.sub(r"(回复)?(//)?\s*@\S*?\s*(:| |$)", " ", text)  # 去除正文中的@和回复/转发中的用户名
        text = re.sub(r"\[\S+\]", "", text)  # 去除表情符号
        URL_REGEX = re.compile(
            r'(?i)\b((?:https?://|www\d{0,3}[.]|[a-z0-9.\-]+[.][a-z]{2,4}/)(?:[^\s()<>]+|\(([^\s()<>]+|(\([^\s()<>]+\)))*\))+(?:\(([^\s()<>]+|(\([^\s()<>]+\)))*\)|[^\s`!()\[\]{};:\'".,<>?«»“”‘’]))',
            re.IGNORECASE)
        text = re.sub(URL_REGEX, "", text)  # 去除网址

        # 去除符号
        for ch in "。，：；{|}（）()+-*&……%￥#@！~·`、【】[];:?？《》<>,.":
            text = text.replace(ch, '')

        # 去除停用词
        for word in stopwords:
            text = text.replace(word, '')

        text = re.sub(r"\s+", " ", text)  # 合并正文中过多的空格
        text = text.replace(" ", "")  # 去除无意义的词语
        return text.strip()

    # 数据清洗
    comments = comments.apply(clean_text)
    print(comments.shape)

    # # 对每个评论进行词性标注并只保留形容词
    # adjectives = []
    # for comment in comments:
    #     for word, flag in psg.cut(comment):
    #         if flag.startswith('a') or flag.startswith('an') or flag.startswith('i') or flag.startswith('ad') or flag.startswith('Ag'):  # 以'a'开头的词性表示形容词
    #             adjectives.append(word)
    #             # 如果你想在词性标注的时候也过滤停用词，可以在这里添加相应的逻辑
    #
    # comments=adjectives

    # 修改情感态度分析函数
    def analyze_sentiment(text):
        if len(text) == 0:
            return '中性'
        s = SnowNLP(text)
        score = s.sentiments
        if score < 0.2:
            return '消极'
        elif score < 0.4:
            return '比较消极'
        elif score < 0.6:
            return '中性'
        elif score < 0.8:
            return '比较积极'
        else:
            return '积极'

    # 根据新的情感倾向分数将评论分类为消极、比较消极、中性、比较积极、积极
    sentiment_labels = [analyze_sentiment(comment) for comment in comments]
    negative_comments = [comment for comment, label in zip(comments, sentiment_labels) if label == '消极']
    somewhat_negative_comments = [comment for comment, label in zip(comments, sentiment_labels) if label == '比较消极']
    neutral_comments = [comment for comment, label in zip(comments, sentiment_labels) if label == '中性']
    somewhat_positive_comments = [comment for comment, label in zip(comments, sentiment_labels) if label == '比较积极']
    positive_comments = [comment for comment, label in zip(comments, sentiment_labels) if label == '积极']

    # 情感态度占比饼图
    sentiment_labels = ['消极', '比较消极', '中性', '比较积极', '积极']
    sentiment_sizes = [len(negative_comments), len(somewhat_negative_comments), len(neutral_comments),
                       len(somewhat_positive_comments), len(positive_comments)]
    plt.pie(sentiment_sizes, labels=sentiment_labels, autopct='%1.2f%%', shadow=True)
    plt.title("情感态度占比")
    plt.savefig(save_filename + 'pie_chart.png')
    plt.show()

    # 根据新的类别生成对应的词云图
    def generate_wordcloud(text, filename):
        if len(text) == 0:  # 添加条件判断以确保文本内容不为空
            print("文本内容为空，无法生成词云图")
            return
        wordcloud = WordCloud(font_path="simhei.ttf", background_color='white').generate(text)
        plt.figure(figsize=(10, 10))
        plt.imshow(wordcloud, interpolation='bilinear')
        plt.axis('off')
        plt.savefig(filename)  # 保存词云图
        plt.show()

    # 生成消极评论词云图
    negative_text = ' '.join(negative_comments)
    generate_wordcloud(negative_text, save_filename + 'negative_wordcloud.png')

    # 生成比较消极评论词云图
    somewhat_negative_text = ' '.join(somewhat_negative_comments)
    generate_wordcloud(somewhat_negative_text, save_filename + 'somewhat_negative_wordcloud.png')

    # 生成中性评论词云图
    neutral_text = ' '.join(neutral_comments)
    generate_wordcloud(neutral_text, save_filename + 'neutral_wordcloud.png')

    # 生成比较积极评论词云图
    somewhat_positive_text = ' '.join(somewhat_positive_comments)
    generate_wordcloud(somewhat_positive_text, save_filename + 'somewhat_positive_wordcloud.png')

    # 生成积极评论词云图
    positive_text = ' '.join(positive_comments)
    generate_wordcloud(positive_text, save_filename + 'positive_wordcloud.png')

    def plot_word_frequency(text):
        word_list = jieba.lcut(text)
        word_list = [word for word in word_list if word.strip()]
        word_counter = Counter(word_list)
        word_freq = word_counter.most_common(10)  # 取出现频率最高的前20个词语及其频次
        words, freqs = zip(*word_freq)

        # import jieba.posseg as psg
        # cixing = ()
        # words = []
        # for i in psg.cut(word_list):
        #     cixing = (i.word, i.flag)  # 词语和词性
        #     words.append(cixing)
        # save = ['a']  # 挑选词性
        # for i in words:
        #     if i[1] in save:
        #         print(i)

        plt.figure(figsize=(10, 6))
        plt.bar(words, freqs)
        plt.xticks(rotation=45)
        plt.xlabel('词语')
        plt.ylabel('频次')
        plt.title('评论词语频次图')
        plt.show()

    # 绘制总的词频图
    total_text = ' '.join(comments)
    plot_word_frequency(total_text)


if __name__ == "__main__":
    cookie = 'SINAGLOBAL=6779755535453.535.1717933380900; UOR=,,www.bing.com; SCF=ArByXTApePEkzPeTbQzQuQRUGVME16AJ5sGZjSkuIQ6LoSQ0mWBt0oRrQ5TEDbQS0O3kFkfopfADyqFGm3x_4y4.; ALF=1727698926; SUB=_2A25L13q-DeRhGeFM41UT-SjNwz2IHXVorfJ2rDV8PUJbkNANLVnDkW1NQLdgAn2-CE4DMZk52v7teNWedM2xWgzJ; SUBP=0033WrSXqPxfM725Ws9jqgMF55529P9D9WWLb7KLM9h9U9VPMhpSI6Nl5JpX5KMhUgL.FoME1hME1Kqp1h22dJLoIEBLxKBLB.-LBKqLxKqL12-LBKzLxK-L122LBK.LxKqL1h.L12zt; _s_tentry=-; Apache=7256852148078.053.1725106928656; ULV=1725106928666:6:2:1:7256852148078.053.1725106928656:1722850540797; XSRF-TOKEN=zt451MpR-b5iEYW-lVmCz2Sl; WBPSESS=9Mtg7N6y1ELlwtshNdNnmdNmIWGcx4oGbIUDOAOUngyMDUnOSK_aC2SlOPVUKtRc7qK1t3A_ft1Cqn7Kx8TV-Q8tA8-X5ss34x63E-gkwzkkvZEmJ-_gaqFZyrsxrLFtbsBbmQ8kOiBpVYTtwGxq_w==; ariaReadtype=1; ariaMouseten=null; ariaStatus=false';
    topic = '女子拿手机骑单车摔倒身亡';
    crawComments(cookie, topic);
    drawWordsCloud(topic);
