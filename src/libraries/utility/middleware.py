import libraries.utility.timing as timing

class TimingMiddleware(object):
    def process_response(self, request, response):
        t = '<pre>%s</pre>' % (timing.get_times())
        response.content = response.content + t.encode('utf-8')
        return response