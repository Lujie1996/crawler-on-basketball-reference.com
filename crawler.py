from bs4 import BeautifulSoup, Comment
import os
import requests
import mongodb
import logging

db = mongodb.MongoDB('localhost', 27017)

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


def get_html_code(url):
    headers = {
        'User-Agent': 'MMozilla/5.0 (Windows NT 6.1; WOW64; rv:31.0) Gecko/20100101 Firefox/31.0'
    }

    r = requests.get(url, headers=headers)
    r.encoding = 'UTF-8'
    page = r.text
    return page


def parse_table(table):
    assert table is not None
    thead_trs = table.find('thead').find_all('tr')
    thead_ths = thead_trs[-1].find_all('th')
    table_head = list()
    for thead_th in thead_ths:
        table_head.append(thead_th.text)
    tbody = table.find('tbody')
    trs = tbody.find_all('tr')
    table_content = list()
    for tr in trs:
        number_of_columns = len(table_head)
        row_data = list()
        if tr.find('th') is not None:
            row_data.append(tr.find('th').text)
        # in some cases, the first column (year) is not included in <th></th> but directly in <td></td>
        tds = tr.find_all('td')
        for td in tds:
            row_data.append(td.text)
        while len(row_data) < number_of_columns:
            row_data.append("")
        table_content.append(row_data)
    return table_head, table_content


def add_col_of_name(name, table_head, table_content):
    assert name and table_content and table_content is not None
    table_head.insert(0, 'name')
    for index in range(0, len(table_content)):
        table_content[index].insert(0, name)
    return table_head, table_content


def get_from_players_homepage(url):
    page = get_html_code(url)
    soup = BeautifulSoup(page, 'lxml')
    assert soup is not None
    target_tables = ["all_per_game", "all_totals", "all_per_minute", "all_per_poss",
                     "all_advanced", "all_shooting", "all_advanced_pbp", "all_playoffs_per_game",
                     "all_playoffs_totals", "all_playoffs_per_minute", "all_playoffs_per_poss",
                     "all_playoffs_advanced", "all_playoffs_shooting", "all_play_offs_advanced_pbp",
                     "all_all_star", "all_all_salaries"]
    name = soup.find(id='info').find(itemprop='name').text
    print(name + "'s web page is ready...")
    table_wrappers = soup.select(".table_wrapper")
    for table_wrapper in table_wrappers:
        assert table_wrapper is not None
        if table_wrapper['id'] not in target_tables:
            continue
        table_name = table_wrapper['id'][4:]
        comments = table_wrapper.find(text=lambda text: isinstance(text, Comment))
        if comments is not None:
            table_wrapper_soup = BeautifulSoup(comments, 'lxml')
            table = table_wrapper_soup.select("table")[0]
        else:
            table = table_wrapper.select("table")[0]
        table_head, table_content = parse_table(table)
        add_col_of_name(name, table_head, table_content)
        print("#" + str(table_wrappers.index(table_wrapper)) + ": ", end="")
        db.add_rows_to_table(table_name, table_head, table_content)
    print("He is OK in DB!")
    print("------------------------------------------------------")


def get_player_list(url):
    print("Getting player list...")
    alpha_list = list()
    player_list = list()
    if not os.path.exists('player_urls.txt'):
        print("No local file. Crawling from internet...")
        file = open('player_urls.txt', 'w', encoding="utf-8")
        for index in range(0, 26):
            char = chr(ord('a') + index)
            alpha_list.append(url + char + '/')
        for alpha_url in alpha_list:
            if alpha_list.index(alpha_url) == 23:
                continue
            page = get_html_code(alpha_url)
            soup = BeautifulSoup(page, 'lxml')
            table = soup.select("#players")[0]
            trs = table.find("tbody").find_all("tr")
            for tr in trs:
                player_homepage = 'https://www.basketball-reference.com' + tr.find("th").find("a")['href']
                player_list.append(player_homepage)
            print(chr(ord('A') + alpha_list.index(alpha_url)) + " list is Ready!")
        for player_homepage in player_list:
            file.write(player_homepage + '\n')
    else:
        file = open('player_urls.txt', 'r', encoding="utf-8")
        print("Local file exists. Reading from file...")
        for str in file.readlines():
            player_list.append(str)
        print("Read OK!")
    file.close()
    return player_list


if __name__ == '__main__':
    url = 'https://www.basketball-reference.com/players/'
    player_list = get_player_list(url)
    assert player_list is not None
    for player_homepage in player_list:
        player_homepage = player_homepage.replace("\n", "")
        print("Now crawling individual player_homepage at " + player_homepage)
        get_from_players_homepage(player_homepage)