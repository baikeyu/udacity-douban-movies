import expanddouban
import string
import csv
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

    def __str__(self):
        return (self.name, self.rate, self.location, self.category, self.info_link, self.cover_link)


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
    all_movies = soup.find('div', class_="list-wp")
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


"""
get all available locations from the page
"""


def get_all_locations():
    all_location_url = getMovieUrl('全部类型', '全部地区')
    html = expanddouban.getHtml(all_location_url)
    soup = BeautifulSoup(html, 'lxml')
    locationList = []
    for child in soup.find(class_='tags').find(class_='category').next_sibling.next_sibling:
        location = child.find(class_='tag').get_text()
        if location != '全部地区':
            locationList.append(location)

    return locationList


"""
get movie list from request categories, and then write into movies.csv
"""


def get_movie_info(category_list):
    # get all available locations
    location_list = get_all_locations()

    # get movie for each category and location
    all_movie_list = []
    for category in category_list:
        for location in location_list:
            movie_obj_list = getMovies(category, location)
            all_movie_list.extend(movie_obj_list)

    # write all_movie_list to "movies.csv"
    f = open("movies.csv", "w", encoding='utf-8')
    writer = csv.writer(f)
    for element in all_movie_list:
        context_list = [element.name, element.rate, element.location, element.category, element.info_link,
                        element.cover_link]
        writer.writerow(context_list)
    f.close()


"""
Write movie related data to "output.txt".
Get what is the percentage of the top three of each movie category that you have chosen, 
and what percentage of the total number of films in this category.
"""


def get_movie_data(category_list):
    location_list = get_all_locations()
    count_dict = dict()
    sum_dict = dict()
    for category in category_list:
        sum_count = 0
        temp_dict = {}
        for location in location_list:
            movie_obj_list = getMovies(category, location)
            temp_dict[location] = temp_dict.get(location, 0) + len(movie_obj_list)
            count_dict[category] = temp_dict
            sum_count += len(movie_obj_list)
        sum_dict[category] = sum_count
    # sort top three place of per category and write the related data into "output.txt".
    f = open("output.txt", "w", encoding='utf-8')
    for key in count_dict:
        temp = count_dict[key]
        sort_list = sorted(temp.items(), key=lambda d: d[1], reverse=True)
        sort_list = sort_list[:3]
        f.write(key)
        f.write(":\n")
        f.write("数量排名前三的地区: {}, {}, {}\n".format(sort_list[0][0], sort_list[1][0], sort_list[2][0]))
        # Percentage of the total number of films in this category.
        per1 = (sort_list[0][1] / sum_dict[key]) * 100
        per2 = (sort_list[1][1] / sum_dict[key]) * 100
        per3 = (sort_list[2][1] / sum_dict[key]) * 100
        f.write("分别占此类别电影总数的百分比为: {}, {}, {}\n\n".format('%.2f' % per1, '%.2f' % per2, '%.2f' % per3))
    f.close()


"""
Print movie
"""


def print_movies(movies):
    for movie in movies:
        print("{}, {}, {}, {}, {}, {}".format(movie.name, movie.rate, movie.location, movie.category, movie.info_link,
                                              movie.cover_link))


def main():
    """豆瓣电影爬虫程序入口"""
    # url = getMovieUrl("剧情", "美国")
    # print(url)

    # movies = getMovies("剧情", "美国")
    # print_movies(movies)

    category_list = ["喜剧", "冒险", "灾难"]
    get_movie_info(category_list)
    get_movie_data(category_list)


if __name__ == '__main__':
    main()
