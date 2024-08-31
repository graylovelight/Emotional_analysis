import os
import re

import pandas as pd

import jieba
from snownlp import SnowNLP
from wordcloud import WordCloud
import matplotlib.pyplot as plt
# 读取待预测数据，加载模型、词云等工具进行情感分析

plt.rcParams['font.sans-serif']=['SimHei','Songti SC','STFangsong']
plt.rcParams['axes.unicode_minus'] = False  # 用来正常显示负号


from collections import Counter


# 修改成读取的文件
data = pd.read_csv('微博话题/女子拿手机骑单车摔倒身亡.csv')
save_filename='可视化结果/女子拿手机骑单车摔倒身亡/'
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
stopwords.extend(['好感兴趣', '已开通超话社区', '转发微博', '图片评论', '已开通了超话社区', '说', '找','微博','哥哥'])


def clean_text(text):
    text = re.sub(r"(回复)?(//)?\s*@\S*?\s*(:| |$)", " ", text)  # 去除正文中的@和回复/转发中的用户名
    text = re.sub(r"\[\S+\]", "", text)      # 去除表情符号
    URL_REGEX = re.compile(
        r'(?i)\b((?:https?://|www\d{0,3}[.]|[a-z0-9.\-]+[.][a-z]{2,4}/)(?:[^\s()<>]+|\(([^\s()<>]+|(\([^\s()<>]+\)))*\))+(?:\(([^\s()<>]+|(\([^\s()<>]+\)))*\)|[^\s`!()\[\]{};:\'".,<>?«»“”‘’]))',
        re.IGNORECASE)
    text = re.sub(URL_REGEX, "", text)       # 去除网址

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
sentiment_sizes = [len(negative_comments), len(somewhat_negative_comments), len(neutral_comments), len(somewhat_positive_comments), len(positive_comments)]
plt.pie(sentiment_sizes, labels=sentiment_labels, autopct='%1.2f%%', shadow=True)
plt.title("情感态度占比")
plt.savefig(save_filename+'pie_chart.png')
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
generate_wordcloud(negative_text, save_filename+'negative_wordcloud.png')

# 生成比较消极评论词云图
somewhat_negative_text = ' '.join(somewhat_negative_comments)
generate_wordcloud(somewhat_negative_text, save_filename+'somewhat_negative_wordcloud.png')

# 生成中性评论词云图
neutral_text = ' '.join(neutral_comments)
generate_wordcloud(neutral_text, save_filename+'neutral_wordcloud.png')

# 生成比较积极评论词云图
somewhat_positive_text = ' '.join(somewhat_positive_comments)
generate_wordcloud(somewhat_positive_text, save_filename+'somewhat_positive_wordcloud.png')

# 生成积极评论词云图
positive_text = ' '.join(positive_comments)
generate_wordcloud(positive_text, save_filename+'positive_wordcloud.png')



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
