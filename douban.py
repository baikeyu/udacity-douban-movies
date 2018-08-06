import logging
import random
import string
import requests
import time
from collections import deque
from urllib import parse

from settings import User_Agents


class DoubanSpider(object):
    """豆瓣爬虫"""
    def __init__(self):
        # 基本的URL
        self.base_url = 'https://movie.douban.com/j/new_search_subjects?'
        self.full_url = self.base_url + '{query_params}'
        # 从User-Agents中选择一个User-Agent
        self.headers = {'User-Agent': random.choice(User_Agents)}
        # 影视形式(电影, 电视剧,综艺)
        self.form_tag = None  # 类型
        self.type_tag = None  # 地区
        self.countries_tag = None  # 特色
        self.genres_tag = None
        self.sort = 'T'  # 排序方式,默认是T,表示热度
        self.range = 0, 10  # 评分范围
        self.playable = ''
        self.unwatched = ''

    def get_query_parameter(self):
        """获取用户输入信息"""
        # 获取tags参数
        # self.form_tag = input('请输入你想看的影视形式(电影|电视剧|综艺...):')
        # self.type_tag = input('请输入你想看的影视类型(剧情|爱情|喜剧|科幻...):')
        # self.countries_tag = input('请输入你想看的影视地区(大陆|美国|香港...):')
        # self.genres_tag = input('请输入你想看的影视特色(经典|冷门佳片|黑帮...):')
        self.form_tag = "电影"
        self.type_tag = "剧情"
        self.countries_tag = "美国"

    def get_default_query_parameter(self):
        """获取默认的查询参数"""
        # 获取 sort, range, playable, unwatched参数
        self.range = input('请输入评分范围[0-10]:')
        self.sort = input('请输入排序顺序(热度:T, 时间:R, 评价:S),三选一:').upper()
        self.playable = input('请选择是否可播放(默认不可播放):')
        self.unwatched = input('请选择是否为我没看过(默认是没看过):')

    def encode_query_data(self):
        """对输入信息进行编码处理"""
        if not (self.form_tag and self.type_tag and self.countries_tag and self.genres_tag):
            all_tags = ''
        else:
            all_tags = [self.form_tag, self.type_tag, self.countries_tag, self.genres_tag]
        query_param = {
            'sort': self.sort,
            'range': self.range,
            'tags': all_tags,
            'playable': self.playable,
            'unwatched': self.unwatched,
        }

        # string.printable:表示ASCII字符就不用编码了
        query_params = parse.urlencode(query_param, safe=string.printable)
        # 去除查询参数中无效的字符
        invalid_chars = ['(', ')', '[', ']', '+', '\'']
        for char in invalid_chars:
            if char in query_params:
                query_params = query_params.replace(char, '')
        # 把查询参数和base_url组合起来形成完整的url
        self.full_url = self.full_url.format(query_params=query_params) + '&start={start}'

    def download_movies(self, offset):
        """下载电影信息
        :param offset: 控制一次请求的影视数量
        :return resp:请求得到的响应体"""
        full_url = self.full_url.format(start=offset)
        resp = None
        try:
            resp = requests.get(full_url, headers=self.headers)
        except Exception as e:
            # print(resp)
            logging.error(e)
        return resp

    def get_movies(self, resp):
        """获取电影信息
        :param resp: 响应体
        :return movies:爬取到的电影信息"""
        if resp:
            if resp.status_code == 200:
                # 获取响应文件中的电影数据
                movies = dict(resp.json()).get('data')
                if movies:
                    # 获取到电影了,
                    print(movies)
                    return movies
                else:
                    # 响应结果中没有电影了!
                    # print('已超出范围!')
                    return None
        else:
            # 没有获取到电影信息
            return None



def main():
    """豆瓣电影爬虫程序入口"""
    # 1. 初始化工作,设置请求头等
    spider = DoubanSpider()
    # 2. 与用户交互,获取用户输入的信息
    spider.get_query_parameter()
    # 3. 对信息进行编码处理,组合成有效的URL
    spider.encode_query_data()
    id = offset = 0
    while True:
        # 4. 下载影视信息
        reps = spider.download_movies(offset)
        # 5.提取下载的信息
        movies = spider.get_movies(reps)
        # 6. 保存数据到MongoDB数据库
        # spider.save_movies(movies, id)
        offset += 20
        id = offset
        # 控制访问速速
        time.sleep(5)


if __name__ == '__main__':
    main()