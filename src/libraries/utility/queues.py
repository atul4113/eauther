from google.appengine.api import taskqueue
from google.appengine.ext import ndb
from google.appengine.runtime import DeadlineExceededError
from libraries.utility.environment import get_versioned_module
import logging

TASK_QUEUE_RETRIES = 5

class TaskQueue():
    def __init__(self):
        pass

    DEFAULT = 'default'
    SEARCH = 'search'

def executor(function, args):
    retry = 0
    while retry < TASK_QUEUE_RETRIES:
        try:
            function(*args)
            retry = TASK_QUEUE_RETRIES
        except DeadlineExceededError as e:
            retry += 1
            if retry == TASK_QUEUE_RETRIES:
                raise e


def trigger_task(url):
    logging.info('New task (%s)' % url)

    def logic(task_url):
        taskqueue.add(url=task_url)

    executor(logic, (url,))


def trigger_backend_task(url, target=get_versioned_module('download'), name=None, params=None, payload=None, queue_name='default', countdown=0):
    def logic(task_url, task_target, task_name, task_params, task_payload, task_queue_name, task_coundown):
        taskqueue.add(url=task_url, target=task_target, name=task_name, params=task_params, payload=task_payload, queue_name=task_queue_name, countdown=task_coundown)
        logging.info('New backend task (%s): %s' % (target, url))

    try:
        executor(logic, (url, target, name, params, payload, queue_name, countdown))
    except Exception as e:
        logging.error('Adding new task retires pool exhausted.')
        logging.error(e)
        raise e


#Todo: test it on production
def trigger_backend_tasks(urls, target=get_versioned_module('download'), params=None, payload=None, queue_name='default', time_delta=0):

    @ndb.transactional
    def bulk_add(new_tasks):
        return taskqueue.Queue(queue_name).add(new_tasks, True)

    def transactional_add(new_tasks):
        executor(bulk_add, [new_tasks])

    tasks = []
    for task_no, url in enumerate(urls):
        tasks.append(taskqueue.Task(payload, url=url, target=target, params=params, countdown=((task_no +1) * time_delta)))
        if len(tasks) % 50 == 0:
            transactional_add(tasks)
            tasks = []
    if len(tasks):
        transactional_add(tasks)
    logging.info('%s new backend tasks (%s):\n%s' % (len(urls), target, '\n'.join(urls)))


def delete_task(name, queue_name='default'):
    queue = taskqueue.Queue(name=queue_name)
    queue.delete_tasks(taskqueue.Task(name=name))