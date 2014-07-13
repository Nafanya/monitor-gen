import requests
import bs4
from bs4 import BeautifulSoup as BS
            
def parseContests():
    contests = []
    url = 'http://contest.stavpoisk.ru/olympiad/show-all'
    response = requests.get(url)
    if response.status_code != 200:
        return []
    soup = BS(response.text)
    table = soup.find_all('div', id='actual-olympiads')[0]
    for row in table.tbody:
        if row and isinstance(row, bs4.element.Tag):
            c = {}
            for cls in row.children:
                try:
                    key = cls.attrs['class'][0]
                    if key == 'date':
                        c[key] = cls.string.strip()
                    elif key == 'name':
                        c[key] = cls.a.string.strip()
                    else:
                        c[key] = cls.a.get('href').strip()
                except:
                    pass
            contests.append(c)
    return contests
    
if __name__ == '__main__':
    contests = parseContests()
    for contest in contests:
        for key, value in contest.iteritems():
            print key, ': ', value
