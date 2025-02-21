from django.template.defaultfilters import register

@register.filter
def print_status(status):
    names = {1 : 'New',
             2 : 'Accepted',
             3 : 'In development',
             4 : 'Closed',
             5 : 'Ready'
             }
    return names[int(status)]

@register.filter
def print_type(ticket_type):
    names = {1 : 'Bug',
             2 : 'Question',
             3 : 'Request'
             }
    return names[int(ticket_type)]