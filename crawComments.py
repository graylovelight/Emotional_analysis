import re
import time
import csv
from lxml import etree
from urllib.parse import quote
import requests
#爬取待预测数据，存为csv文件

comment_number = 0

headers_com = {
    'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.45 Safari/537.36',
    'cookie': 'SINAGLOBAL=6779755535453.535.1717933380900; UOR=,,www.bing.com; SCF=ArByXTApePEkzPeTbQzQuQRUGVME16AJ5sGZjSkuIQ6LoSQ0mWBt0oRrQ5TEDbQS0O3kFkfopfADyqFGm3x_4y4.; ALF=1727698926; SUB=_2A25L13q-DeRhGeFM41UT-SjNwz2IHXVorfJ2rDV8PUJbkNANLVnDkW1NQLdgAn2-CE4DMZk52v7teNWedM2xWgzJ; SUBP=0033WrSXqPxfM725Ws9jqgMF55529P9D9WWLb7KLM9h9U9VPMhpSI6Nl5JpX5KMhUgL.FoME1hME1Kqp1h22dJLoIEBLxKBLB.-LBKqLxKqL12-LBKzLxK-L122LBK.LxKqL1h.L12zt; _s_tentry=-; Apache=7256852148078.053.1725106928656; ULV=1725106928666:6:2:1:7256852148078.053.1725106928656:1722850540797; XSRF-TOKEN=zt451MpR-b5iEYW-lVmCz2Sl; WBPSESS=9Mtg7N6y1ELlwtshNdNnmdNmIWGcx4oGbIUDOAOUngyMDUnOSK_aC2SlOPVUKtRc7qK1t3A_ft1Cqn7Kx8TV-Q8tA8-X5ss34x63E-gkwzkkvZEmJ-_gaqFZyrsxrLFtbsBbmQ8kOiBpVYTtwGxq_w==; ariaReadtype=1; ariaMouseten=null; ariaStatus=false'
}


def getArticleId(id_str):
    """
    :param id_str: 需要解密的id字符串
    :return:
    """
    url_id = "https://weibo.com/ajax/statuses/show?id={}".format(id_str)
    resp_id = requests.get(url_id, headers=headers)
    if resp_id is None:
        return 0
    article_id = resp_id.json()["id"]
    return article_id


def get_one_page(params):
    """
    :param params: get请求需要的参数，数据类型为字典
    :return: max_id：请求所需的另一个参数
    """
    url = "https://weibo.com/ajax/statuses/buildComments"
    resp = requests.get(url, headers=headers, params=params)

    data_list = resp.json()["data"]

    for data in data_list:
        data_dict = {
            "screen_name": data["user"]["screen_name"].strip(),
            "profile_image_url": data["user"]["profile_image_url"],
            "location": data["user"]["location"],
            "created_time": data["created_at"].replace("+0800", ""),
            "text": data["text_raw"].strip().replace('\n', ''),
        }
        global comment_number
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
    """
    :param params: get请求需要的参数，数据类型为字典
    :return:
    """
    max_id = get_one_page(params)
    params["max_id"] = max_id
    params["count"] = 20
    while max_id:
        time.sleep(1)
        params["max_id"] = max_id
        max_id = get_one_page(params)


def saveData(data_dict):
    """
    :param data_dict: 要保存的数据，形式为dict类型
    :return:
    """
    writer.writerow(data_dict)


if __name__ == '__main__':
    # cookie=input('输入你的微博主页cookie', type=TEXT)
    baseUrl = 'https://s.weibo.com/weibo?q={}&Refer=index'
    topic = '#女子拿手机骑单车摔倒身亡#'  # 爬取的话题
    fileName = topic.replace('#', '')

    # 向csv文件写入表头
    header = ["screen_name", "profile_image_url", "location", "created_time", "text"]
    f = open(f"微博话题/{fileName}.csv", "w", encoding="utf-8-sig", newline="")
    writer = csv.DictWriter(f, header)
    writer.writeheader()

    url = baseUrl.format(quote(topic))

    page = 0
    pageCount = 1

    while True:
        page = page + 1
        tempUrl = url + '&page=' + str(page)
        print('-' * 36, tempUrl, '-' * 36)
        response = requests.get(tempUrl, headers=headers_com)
        html = etree.HTML(response.text, parser=etree.HTMLParser(encoding='utf-8'))
        count = len(html.xpath('//div[@class="card-wrap"]')) - 2
        for i in range(1, count + 1):
            # 微博url
            weibo_url = html.xpath(
                '//div[@class="card-wrap"][' + str(
                    i) + ']/div[@class="card"]/div[1]/div[2]/div[@class="from"]/a/@href')

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
                "cookie": 'SINAGLOBAL=6779755535453.535.1717933380900; UOR=,,www.bing.com; SCF=ArByXTApePEkzPeTbQzQuQRUGVME16AJ5sGZjSkuIQ6LoSQ0mWBt0oRrQ5TEDbQS0O3kFkfopfADyqFGm3x_4y4.; ALF=1727698926; SUB=_2A25L13q-DeRhGeFM41UT-SjNwz2IHXVorfJ2rDV8PUJbkNANLVnDkW1NQLdgAn2-CE4DMZk52v7teNWedM2xWgzJ; SUBP=0033WrSXqPxfM725Ws9jqgMF55529P9D9WWLb7KLM9h9U9VPMhpSI6Nl5JpX5KMhUgL.FoME1hME1Kqp1h22dJLoIEBLxKBLB.-LBKqLxKqL12-LBKzLxK-L122LBK.LxKqL1h.L12zt; _s_tentry=-; Apache=7256852148078.053.1725106928656; ULV=1725106928666:6:2:1:7256852148078.053.1725106928656:1722850540797; XSRF-TOKEN=zt451MpR-b5iEYW-lVmCz2Sl; WBPSESS=9Mtg7N6y1ELlwtshNdNnmdNmIWGcx4oGbIUDOAOUngyMDUnOSK_aC2SlOPVUKtRc7qK1t3A_ft1Cqn7Kx8TV-Q8tA8-X5ss34x63E-gkwzkkvZEmJ-_gaqFZyrsxrLFtbsBbmQ8kOiBpVYTtwGxq_w==; ariaReadtype=1; ariaMouseten=null; ariaStatus=false',
                "x-xsrf-token": "aDIwzDqvyb7sb-Qxm_dbqC63"
            }
            
            try:
                id = getArticleId(weibo_id)  # 获取参数需要的真正id
            except:
                continue

            # get请求的参数
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
