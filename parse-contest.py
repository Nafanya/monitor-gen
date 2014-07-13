# -*- coding: utf-8 -*- 

from operator import itemgetter
import requests
import bs4
import json
from bs4 import BeautifulSoup as BS

headFields = [u'Место', u'Участник', '=']
contests = {}
titles = {}
global data
            
def parseContest(contestId):
    contests[contestId] = []
    #url = 'http://contest.stavpoisk.ru/olympiad/{0}/show-monitor'.format(contestId)
    #response = requests.get(url)
    #if response.status_code != 200:
    #    return []
    text = open('monitor-' + str(contestId) + '.html').read()
    #soup = BS(response.text)
    soup = BS(text)
    title = soup.find_all('span', class_='page-title')[0].string
    title = title[:title.find('(') - 1]
    titles[contestId] = title
    table = soup.find_all('table')[0]
    head = table.thead.tr
    tasks = len(head.find_all('th', class_='task'))
    body = table.tbody
    i = 1
    for row in body.find_all('tr'):
        user = {}
        name = row.find_all('td', class_='user')[0].string.strip()
        user['name'] = name
        user['rank'] = int(row.find_all('td', class_='rank')[0].string.strip())
        user['solved'] = int(row.find_all('td', class_='solved')[0].string.strip())
        user['time'] = int(row.find_all('td', class_='time')[0].string.strip())
        user['tasks'] = []
        tasks = row.find_all('td', class_='task')
        i = 0
        for task in tasks:
            user['tasks'].append({})
            user['tasks'][-1]['id'] = contestId
            user['tasks'][-1]['problem'] = i
            i += 1
            user['tasks'][-1]['result'] = task.span.attrs['class'][0]
            tries = task.span.strings.next()
            x = 0
            if tries == '+':
                x = 1
            elif tries == '.':
                pass
            else:
                x = int(tries)
            user['tasks'][-1]['tries'] = x
        contests[contestId].append(user)

def calculate():
    users = {}
    global data
    for contest in sorted(contests.keys()):
        for user in contests[contest]:
            name = user['name']
            solved = user['solved']
            tasks = user['tasks']
            if not users.has_key(name):
                users[name] = {}
            # solved
            if users[name].has_key('solved'):
                users[name]['solved'] += solved
            else:
                users[name]['solved'] = solved
            # attempts
            if not users[name].has_key('attempts'):
                users[name]['attempts'] = 0
            # tasks
            for task in tasks:
                users[name]['attempts'] += abs(task['tries'])
            if not users[name].has_key('tasks'):
                users[name]['tasks'] = []
            users[name]['tasks'].append(tasks)
           
    data = users
    js = json.dumps(users, indent=2, sort_keys=True, ensure_ascii=False)
    # js
    

def compr(x, y):
    #solved, attempts, name
    if x[0] > y[0]:
        return -1
    elif x[0] < y[0]:
        return 1
    else:
        if x[1] < y[1]:
            return -1
        elif x[1] > y[1]:
            return 1
        else:
            if x[2] < y[2]:
                return -1
            elif x[2] > y[2]:
                return 1
    return 0

def generate():
    global data
    #<td colspan="4" align="center"></td> - one contest
    out = BS(open('test.html').read())
    root = out.html.table
    headRow = root.thead
    body = root.tbody
    
    srt = []
    for user in data:
        if user and len(user) > 0:
            srt.append((data[user]['solved'], data[user]['attempts'], user,))
    
    srt = sorted(srt, cmp=compr)
    for i in srt:
        for j in i:
            print j
    ind = 1
    nameRows = []
    for man in srt:
        row = out.new_tag('tr')
        nameRows.append(row)
        tmp = out.new_tag('td')
        tmp.string = str(ind)
        row.append(tmp)
        ind += 1
        
        tmp = out.new_tag('td')
        tmp.string = man[2].encode('utf-8')
        row.append(tmp)
        
        tmp = out.new_tag('td')
        tmp.string = str(man[0])
        row.append(tmp)
        
        tmp = out.new_tag('td')
        tmp.string = str(man[1])
        row.append(tmp)
        
        body.append(row)
        
    
    for contest in sorted(contests.keys()):
        # head tasks and contest name
        nameRow = headRow.find_all('tr', id='head-row')[0]
        taskRow = headRow.find_all('tr', id='task-row')[0]
        n = 0
        if len(contests[contest]) > 0:
            n = len(contests[contest][0]['tasks'])
            contestName = out.new_tag('td', colspan=n)
            contestName.string = titles[contest]
            nameRow.append(contestName)
            for i in xrange(n):
                tmp = out.new_tag('td', align='center')
                tmp.string = chr(65 + i)
                taskRow.append(tmp)
                
    # body contestants
    rowInd = 0
    for man in srt:
        curRow = nameRows[rowInd]
        rowInd += 1
        name = man[2]
        for contest in sorted(contests.keys()):
            for c in contests[contest]:
                if c['name'] == name:
                    for task in c['tasks']:
                        tries = task['tries']
                        text = ''
                        color = ''
                        if tries == 1:
                            text = '+'
                            color = 'background-color: #90FF77'
                        elif tries == 0:
                            pass
                        elif tries < 0:
                            text = str(tries)
                            color = 'background-color: #DD290E'
                        else:
                            text = '+' + str(tries)
                            color = 'background-color: #90FF77'
                        tmp = out.new_tag('td', align='center', style=color)
                        tmp.string = text
                        curRow.append(tmp)
                        
    #print out.prettify()
    with open('out.html', 'w') as f:
        f.write(out.prettify().encode('utf-8'))
    
if __name__ == '__main__':
    contestsToParse = [25, 27, 29, 32]
    #contestsToParse = [25, 27]
    for c in contestsToParse:
        parseContest(c)
    calculate()
    generate()
