__author__ = 'nafanya'

# creates tables using os's `wget` to load pages

import os
from bs4 import BeautifulSoup as Bs

'''
contests = {
    id: {
        title: 'TITLE',
        problems: NUMBER,
        people: [
            {
                name: NAME,
                solved: N,
                time: N,
                tasks: [
                    {
                        'problem': ,
                        'result': ,
                        'text': ,
                    },
                ],
            },
            {
                name: NAME,
                solved: N,
                time: N,
                tasks: [
                ],
            },
        ]
    },
    id: {
        ...
    },
}
'''

contests = dict()
names_set = set()
total = dict()


def get_first(obj, tag, class_):
    return obj.find_all(tag, class_=class_)[0]


def get_pts(s):
    s = s.strip()
    if len(s) > 1:
        x = int(s)
        if x > 0:
            return x
    return 0


def srt_compare(x, y):
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


def parse_contest(contest_id):
    print 'parsing', contest_id

    response = ''
    with open('pages/{}.html'.format(contest_id)) as inp:
        response = inp.read()
    soup = Bs(response)

    cur_contest = dict()

    # table (head and body)
    table = soup.find_all('table')[0]
    head = table.thead.tr
    body = table.tbody

    contest_title = get_first(soup, 'span', 'page-title').string
    contest_title = contest_title[:contest_title.find('(') - 1]
    cur_contest['title'] = contest_title

    # number of problems
    cur_contest['problems'] = len(head.find_all('th', class_='task'))
    cur_contest['people'] = list()

    # row with contestant
    for row in body.find_all('tr'):
        contestant = dict()

        name = get_first(row, 'td', 'user').string.strip()
        contestant['name'] = name
        contestant['solved'] = int(get_first(row, 'td', 'solved').string)
        contestant['time'] = int(get_first(row, 'td', 'time').string)
        contestant['tasks'] = list()
        tasks = row.find_all('td', class_='task')
        cnt = 0
        for task in tasks:
            cur_task = dict()
            cur_task['problem'] = cnt
            cnt += 1
            cur_task['result'] = task.span.attrs['class'][0]
            cur_task['text'] = task.span.strings.next()
            contestant['tasks'].append(cur_task)

        cur_contest['people'].append(contestant)

    contests[contest_id] = cur_contest


def calculate():
    for contest in contests:
        for man in contests[contest]['people']:
            names_set.add(man['name'])

    for name in names_set:
        man = dict()
        man['solved'] = 0
        man['se'] = 0
        total[name] = man

    # fix missing people (add 'unsolved' tasks)
    for contest_id in contests.keys():
        p = set()
        for man in contests[contest_id]['people']:
            p.add(man['name'])
        to_add = names_set.difference(p)
        for name_to_add in to_add:
            print 'add', name_to_add, 'in', contest_id
            man = dict()
            man['name'] = name_to_add
            man['solved'] = 0
            man['time'] = 0
            tasks = list()
            for cnt in xrange(contests[contest_id]['problems']):
                cur_task = dict()
                cur_task['problem'] = cnt
                cur_task['result'] = 'NS'
                cur_task['text'] = '.'
                tasks.append(cur_task)
            man['tasks'] = tasks
            contests[contest_id]['people'].append(man)

    for contestId in sorted(contests.keys()):
        for man in contests[contestId]['people']:
            name = man['name']
            solved = man['solved']
            tasks = man['tasks']

            if not name in total:
                total[name] = dict()

            if not 'solved' in total[name]:
                total[name]['solved'] = solved
            else:
                total[name]['solved'] += solved

            if not 'se' in total[name]:
                total[name]['se'] = 0

            for task in tasks:
                total[name]['se'] += get_pts(task['text'])


def generate(table_name):
    out = Bs(open('template.html').read())
    root = out.html.table
    head_row = root.thead
    body = root.tbody

    to_sort = list()
    for name in names_set:
        to_sort.append((total[name]['solved'], total[name]['se'], name))
    srt = sorted(to_sort, cmp=srt_compare)

    name_rows = list()
    ind = 1
    for man in srt:
        row = out.new_tag('tr')
        name_rows.append(row)

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

    # contest titles and task names (A, B, C, ...)
    for contest_id in sorted(contests.keys()):
        # head tasks and contest name
        title_row = head_row.find_all('tr', id='head-row')[0]
        task_row = head_row.find_all('tr', id='task-row')[0]

        n = contests[contest_id]['problems']
        contest_name = out.new_tag('td', colspan=n)
        contest_name.string = str(contests[contest_id]['title'].encode('utf-8'))
        title_row.append(contest_name)
        for cnt in xrange(n):
            tmp = out.new_tag('td', align='center')
            tmp.string = chr(65 + cnt)
            task_row.append(tmp)

    # body contestants
    row_ind = 0
    for man in srt:
        cur_row = name_rows[row_ind]
        row_ind += 1
        name = man[2]
        for contest_id in sorted(contests.keys()):
            for c in contests[contest_id]['people']:
                if c['name'] == name:
                    for task in c['tasks']:
                        text = task['text']
                        if '+' in text:
                            color = 'background-color: #90FF77'
                        elif '-' in text:
                            color = 'background-color: #DD290E'
                        else:
                            color = ''
                            text = ''
                        tmp = out.new_tag('td', align='center', style=color)
                        tmp.string = text
                        cur_row.append(tmp)

    with open('out/' + table_name, 'w') as f:
        f.write(out.prettify().encode('utf-8'))

def create_table(name, ids):
    contests.clear()
    names_set.clear()
    total.clear()
    for x in ids:
        url = 'http://contest.stavpoisk.ru/olympiad/{0}/show-monitor'.format(x)
        os.system('wget {} -nv -O pages/{}.html'.format(url, x))
    for id in ids:
        # seems to fail only if monitor is empty
        try:
            parse_contest(id)
        except:
            pass
    calculate()
    generate(name)


if __name__ == '__main__':
    par_c = [25, 27, 29, 32, 38, 39, 40, 43, 47, 48, 50, 52]
    par_d = [31, 33, 34, 35, 36, 41, 42, 44, 46, 49, 51, 53, 54]
    create_table('stand-c.html', par_c)
    create_table('stand-d.html', par_d)
