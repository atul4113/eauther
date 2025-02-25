import logging
from celery import shared_task
from libraries.utility.environment import get_versioned_module
from django.core.cache import cache
from django.db import transaction

TASK_QUEUE_RETRIES = 5


class TaskQueue:
    SEARCH = 'search_queue'
    DEFAULT = 'default_queue_name'
    """
    A custom TaskQueue class to mimic Google App Engine's TaskQueue using Celery.
    """

    @staticmethod
    def add(url, target=None, name=None, params=None, payload=None, queue_name='default', countdown=0):
        """
        Adds a task to the Celery queue.
        """
        logging.info(f"Adding task to queue {queue_name}: {url}")
        trigger_backend_task(url, target, name, params, payload, queue_name, countdown)

    # @staticmethod


def executor(function, args):
    """
    Executes a function with retries on failure.
    """
    retry = 0
    while retry < TASK_QUEUE_RETRIES:
        try:
            function(*args)
            retry = TASK_QUEUE_RETRIES
        except Exception as e:  # Replace DeadlineExceededError with a generic exception
            retry += 1
            if retry == TASK_QUEUE_RETRIES:
                logging.error(f"Task failed after {TASK_QUEUE_RETRIES} retries: {e}")
                raise e


def trigger_task(url):
    """
    Triggers a new task by adding it to the Celery queue.
    """
    logging.info(f"New task ({url})")

    @shared_task
    def logic(task_url):
        # Replace this with your task logic
        logging.info(f"Executing task: {task_url}")

    executor(logic.delay, (url,))


def trigger_backend_task(url, target=get_versioned_module('download'), name=None, params=None, payload=None, queue_name='default', countdown=0):
    """
    Triggers a backend task with additional options.
    """
    @shared_task
    def logic(task_url, task_target, task_name, task_params, task_payload, task_queue_name, task_countdown):
        # Replace this with your task logic
        logging.info(f"Executing backend task ({task_target}): {task_url}")

    try:
        executor(logic.delay, (url, target, name, params, payload, queue_name, countdown))
    except Exception as e:
        logging.error("Adding new task retries pool exhausted.")
        raise e


def trigger_backend_tasks(urls, target=get_versioned_module('download'), params=None, payload=None, queue_name='default', time_delta=0):
    """
    Triggers multiple backend tasks in bulk.
    """
    tasks = []
    for task_no, url in enumerate(urls):
        task = {
            "url": url,
            "target": target,
            "params": params,
            "payload": payload,
            "queue_name": queue_name,
            "countdown": (task_no + 1) * time_delta,
        }
        tasks.append(task)
        if len(tasks) % 50 == 0:
            _bulk_add_tasks(tasks)
            tasks = []
    if tasks:
        _bulk_add_tasks(tasks)
    logging.info(f"{len(urls)} new backend tasks ({target}):\n" + "\n".join(urls))


@transaction.atomic
def _bulk_add_tasks(tasks):
    """
    Adds multiple tasks to the queue in a transactional manner.
    """
    for task in tasks:
        trigger_backend_task(**task)


def delete_task(name, queue_name='default'):
    """
    Deletes a task from the queue.
    """
    logging.warning("Celery does not support direct task deletion by name. Implement a custom solution if needed.")
