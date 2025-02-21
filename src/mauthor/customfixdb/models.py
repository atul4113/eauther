import json
from django.db import models
from libraries.utility.decorators import cached_property


class FixStatus(object):
    IN_PROGRESS = 0
    FINISHED = 1
    ERROR = -1


class LogLevel(object):
    debug = 0
    info = 1
    warning = 2
    error = 3

    colors = {
        debug: {
            'color': '#00F',
            'bg_color': '#FFF'
        },
        info: {
            'color': '#FFF',
            'bg_color': '#0C0'
        },
        warning: {
            'color': 'rgba(247, 153, 23, 0)',
            'bg_color': '#FFF'
        },
        error: {
            'color': '#FFF',
            'bg_color': '#C00'
        },
    }


class FixLog(models.Model):
    created_date = models.DateTimeField(auto_now_add=True)
    modified_date = models.DateTimeField(auto_now=True)
    slug = models.CharField(max_length=200)
    logged_data = models.TextField()
    status = models.IntegerField(default=FixStatus.IN_PROGRESS)
    level = models.IntegerField(default=LogLevel.debug)

    @classmethod
    def start(cls, slug):
        entry = cls(slug=slug)
        entry.save()
        return entry

    def log(self, level, data):
        self.logged_data = json.dumps(data)
        self.level = level
        self.save()

    def info(self, data):
        return self.log(LogLevel.info, data)

    def warning(self, data):
        return self.log(LogLevel.warning, data)

    def error(self, data):
        return self.log(LogLevel.error, data)

    @cached_property
    def data(self):
        if not self.logged_data:
            return None
        return json.loads(self.logged_data)

    def color(self):
        return LogLevel.colors[self.level]['color']

    def bg_color(self):
        return LogLevel.colors[self.level]['bg_color']

