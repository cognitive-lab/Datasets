'''
codeforces scraper
'''

from bs4 import BeautifulSoup
import requests
import pandas as pd
import sys
import time
import random

def scrap_tables(page_start, page_end):

    f = open('dataset/codeforces.csv', 'w')
    f.write('id,name,categories,difficulty,solved\n')
    f = open('dataset/codeforces.csv', 'a')

    for page in range(page_start, page_end+1):
        print('getting page', page)

        URL = 'http://codeforces.com/problemset/page/' + str(page)
        page = requests.get(URL)

        soup = BeautifulSoup(page.content, features='html.parser')

        table = soup.find_all('tr')

        # a full row
        for row in range(1, len(table)-1):

            # all cols
            soup_row = BeautifulSoup(str(table[row]), 'html.parser')
            cols = soup_row.find_all('td')

            # problem number
            id = cols[0].text.strip()
            # print(cols[0].text.strip())

            # 2nd col: name and tags
            soup_name_tag = BeautifulSoup(str(cols[1]), 'html.parser')
            name_tag = soup_name_tag.find_all('div')

            # name
            name = '\"' + name_tag[0].text.strip() + '\"'
            # print(name_tag[1])

            # all tags
            soup_tags = BeautifulSoup(str(name_tag[1]), 'html.parser')
            tags = soup_tags.find_all('a')

            taglist = map(lambda t: t.text.strip(), tags)


            categories = ';'.join(list(taglist))
            if categories == '':
                categories = 'unknown'
            categories = '\"' + categories + '\"'

            # difficulty
            difficulty = cols[3].text.strip()
            if difficulty == '':
                difficulty = '-1'

            # number of solved cases
            solved = cols[4].text.strip()[1:]
            if solved == '':
                solved = '-1'

            # print(solved)

            f.write(','.join([id, name, categories, difficulty, solved]) + '\n')

    print('done!')

def scrap_desc(start, end):

    df = pd.read_csv('dataset/codeforces.csv')
    df = df[start : end+1]

    for index, row in df.iterrows():

        time.sleep(1)

        try:
            id = row['id']
            print(index, id)

            x, y = id[:-1], id[-1]
            URL = 'http://codeforces.com/problemset/problem/' + str(x) + '/' + str(y)
            page = requests.get(URL)

            soup = BeautifulSoup(page.content, 'html.parser')

            desc = soup.find('div', class_ = 'problem-statement').getText(separator='\n', strip=True)
            f = open('dataset/desc/' + id + '.txt', 'w')
            f.write(desc)

        except Exception as e:
            print(e)
            print(URL, end='\n')
            # print(page.content)

            with open('missing.txt', 'a') as missing:
                missing.write(URL + '\n')

        with open('log.txt', 'w') as log:
            log.write(str(index))


def fix_missing():

    f = open('missing.txt', 'r')

    for line in f:
        time.sleep(1)
        # print(line)
        URL = line.strip()

        slash = URL.rfind('/')
        pre_slash = slash-1

        URL = list(URL)
        # print(URL)

        URL[slash], URL[pre_slash] = URL[pre_slash], URL[slash]
        URL = ''.join(URL)

        id = URL
        id = id.replace('http://codeforces.com/problemset/problem/', '').replace('/', '')
        # print(id)

        page = requests.get(URL)
        soup = BeautifulSoup(page.content, 'html.parser')

        try:
            desc = soup.find('div', class_ = 'problem-statement').getText(separator='\n', strip=True)
            f = open('dataset/desc/' + id + '.txt', 'w')
            f.write(desc)
            print(id)
        except:
            print(id, 'missing')



if __name__ == '__main__':

    if len(sys.argv) == 4:
        fn, start, end = sys.argv[1], int(sys.argv[2]), int(sys.argv[3])
    elif len(sys.argv) == 2:
        fn = sys.argv[1]

    # make table with t
    if fn == 't':
        scrap_tables(start, end)

    # scrap description with d
    elif fn == 'd':
        try:
            with open('log.txt', 'r') as log:
                start = int(log.readline().strip())+1
        except:
            pass

        scrap_desc(start, end)

    # fix missing with m
    elif fn == 'm':
        fix_missing()
