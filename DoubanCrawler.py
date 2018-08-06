import expanddouban
import string
from urllib import parse
from bs4 import BeautifulSoup


class Movie:
    """ Class for representing a movie """

    def __init__(self, name, rate, location, category, info_link, cover_link):
        """ Inits a Movie object """
        self.name = name
        self.rate = rate
        self.location = location
        self.category = category
        self.info_link = info_link
        self.cover_link = cover_link


"""
return a string corresponding to the URL of douban movie lists given category and location.
"""

# 基本的URL
base_url = 'https://movie.douban.com/tag/#/?'
sort = 'S'
type_tag = '电影'  # 类型
category_tag = '剧情'  # 地区
location_tag = '美国'  # 特色
range_tag = 9, 10  # 评分范围

"""
return a string corresponding to the URL of douban movie lists given category and location.
"""


def getMovieUrl(category, location):
    all_tags = [type_tag, category, location]
    query_param = {
        'range': range_tag,
        'tags': all_tags,
    }
    query_params = parse.urlencode(query_param, encoding='UTF-8', safe=string.printable)
    invalid_chars = ['(', ')', '[', ']', '+', '\'']
    for char in invalid_chars:
        if char in query_params:
            query_params = query_params.replace(char, '')
    return base_url + query_params


"""
return a list of Movie objects with the given category and location.
"""


def getMovies(category, location):
    url = getMovieUrl(category, location)
    resp = expanddouban.getHtml(url, True)
    soup = BeautifulSoup(resp, 'lxml')
    # print(soup)  # 输出BeautifulSoup转换后的内容
    all_movies = soup.find('div', class_="list-wp")  # 先找到最大的div
    movie_div_list = all_movies.find_all('a', class_='item')
    movies = []
    for movie_div in movie_div_list:
        movie_info_link = movie_div['href']
        movie_cover_link = movie_div.find('img')['src']
        all_span_tag = movie_div.find_all('span')
        movie_name = all_span_tag[1].text
        movie_rate = all_span_tag[2].text
        movie = Movie(movie_name, movie_rate, location, category, movie_info_link, movie_cover_link)
        movies.append(movie)
    return movies


def print_movies(movies):
    for movie in movies:
        print("{}, {}, {}, {}, {}, {}".format(movie.name, movie.rate, movie.location, movie.category, movie.info_link,
                                              movie.cover_link))


def main():
    """豆瓣电影爬虫程序入口"""
    url = getMovieUrl("剧情", "美国")
    print(url)

    movies = getMovies("剧情", "美国")
    print_movies(movies)


    """"
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
    """


if __name__ == '__main__':
    main()
