import datetime
import logging
import pprint

current = None
times = []

def start(name):
    global current
    global times
    label = {'name' : name, 'start' : datetime.datetime.now(), 'parent' : None, 'kids' : [], 'end' : datetime.datetime.now()}
    if current is not None:
        current['kids'].append(label)
        label['parent'] = current
    if label['parent'] is None:
        times.append(label)
    current = label

def end(name):
    global current
    if name != current['name']:
        raise Exception('Timing: last started was [%(last)s] and you are trying to end [%(name)s]' % {'last' : current['name'], 'name' : name})
    current['end'] = datetime.datetime.now()
    current = current['parent']

def get_current():
    global current
    if current is not None:
        return current['name']
    else:
        return None

def clear():
    global current
    current = None

def log_times():
    global times
    logging.info(pprint.pformat(times))

def get_times():
    global times
    i = 0
    output = '\n'
    for time in times:
        output = output + _get_time(time, i).encode('utf-8')
    times = []
    return output

def _get_time(time, depth):
    output = ''
    for i in range(0, depth):
        output = output + ' '
    difference = time['end'] - time['start']
    if difference > datetime.timedelta(microseconds=100000):
        difference = '<b style="color: red">%s</b>' % difference
    output = output + ('%(name)s [%(time)s]\n' % {'name' : time['name'].encode('utf-8'), 'time' : difference}).encode('utf-8')
    for kid in time['kids']:
        output = output + _get_time(kid, depth + 2)
    return output