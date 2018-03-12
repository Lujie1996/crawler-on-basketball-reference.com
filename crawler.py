from bs4 import BeautifulSoup
import mongodb
import requests

db = mongodb.MongoDB('localhost', 27017)


def get_html_code(url):  # 该方法传入url，返回url的html的源码
    headers = {
        'User-Agent': 'MMozilla/5.0 (Windows NT 6.1; WOW64; rv:31.0) Gecko/20100101 Firefox/31.0'
    }

    r = requests.get(url, headers=headers)
    r.encoding = 'UTF-8'
    page = r.text
    return page


def per_game_data(soup):
    name = soup.find(id='info').find(itemprop='name').text
    table = soup.find(id='per_game')
    thead = table.find('thead')
    thead_ths = thead.find_all('th')
    table_head = list()
    for thead_th in thead_ths:
        table_head.append(thead_th.text)
    tbody = table.find('tbody')
    trs = tbody.find_all('tr')
    table_content = list()
    for tr in trs:
        row_data = list()
        row_data.clear()
        row_data.append(tr.find('th').find('a').text)
        tds = tr.find_all('td')
        for td in tds:
            row_data.append(td.text)
        table_content.append(row_data)
    db.write_per_game_data(name, table_head, table_content)


def get_from_players_homepage(url):
    page = get_html_code(url)
    soup = BeautifulSoup(page, 'lxml')
    per_game_data(soup)
    # TODO: get more data of an individual player


if __name__ == '__main__':
    # TODO: iterate through every player's homepage
    url = 'https://www.basketball-reference.com/players/c/cassesa01.html'
    get_from_players_homepage(url)
