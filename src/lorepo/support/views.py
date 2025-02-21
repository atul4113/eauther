from django.contrib.auth.decorators import login_required, user_passes_test
from django.http import HttpResponseRedirect, Http404
from django.shortcuts import render, get_object_or_404
from lorepo.support.forms import CommentForm, TicketForm
from lorepo.support.models import Ticket, Comment, TicketStatus, TicketType,\
    TicketAttachment
import datetime
from django.core.paginator import Paginator
from django.template.context import Context
from django.template import loader
from lorepo.public.util import send_message
from django.conf import settings
from lorepo.support.templatetags.support import print_status
from libraries.utility.request import get_request_value
from lorepo.spaces.models import SpaceType, Space
from lorepo.filestorage.forms import UploadForm
from google.appengine.api import blobstore
from django.contrib import messages
from mauthor.company.util import get_users_from_company
from django.contrib.auth.models import User
from lorepo.support.util import parse_lesson_id
from lorepo.permission.decorators import security_token

@login_required
@user_passes_test(lambda u: u.company != None)
def index(request, page='1'):
    return _render_list(request, page, 'support/index.html', False)


@login_required
@user_passes_test(lambda u: u.company != None)
def admin(request, page='1'):
    return _render_list(request, page, 'support/admin.html', True)


def _render_list(request, page, template, is_admin):
    page = int(page)
    status = get_request_value(request, 'status', 0)
    ticket_type = get_request_value(request, 'ticket_type', 0)
    if is_admin:
        company_input = get_request_value(request, 'company', '0')
    else:
        company_input = '0'

    if is_admin:
        assignee_input = get_request_value(request, 'assignee', '0')
    else:
        assignee_input = '0'

    if int(status) == 0:
        statuses = [TicketStatus.NEW, TicketStatus.ACCEPTED, TicketStatus.IN_DEVELOPMENT, TicketStatus.READY]
    else:
        statuses = [status]

    if int(ticket_type) == 0:
        types = [TicketType.BUG, TicketType.QUESTION, TicketType.REQUEST]
    else:
        types = [ticket_type]

    ticket_list = Ticket.objects.filter(status__in=statuses, ticket_type__in=types)

    company = None
    if company_input != '0':
        spaces = Space.objects.filter(id=company_input, space_type=SpaceType.CORPORATE)
        if len(spaces) == 1:
            company = spaces[0]
        else:
            company = None
    else:
        if not is_admin:
            company = request.user.company

    if company is not None:
        ticket_list = ticket_list.filter(company=company)

    if is_admin and not request.user.is_superuser:
        ticket_list = ticket_list.filter(assigned_to=request.user)

    if is_admin and request.user.is_superuser:
        assignees = set([ticket.assigned_to for ticket in ticket_list])
        assignees = sorted(assignees, key=lambda ass: "" if ass is None else ass.username)
    else:
        assignees = []

    if assignee_input == '-1':
        ticket_list = ticket_list.exclude(assigned_to__isnull=False)
    elif assignee_input != '0':
        assignee = User.objects.get(pk=assignee_input)
        ticket_list = ticket_list.filter(assigned_to=assignee)

    if assignee_input == '-1':
        ticket_list = sorted(ticket_list, key = lambda ticket: ticket.last_comment_date,reverse=True)
        paginator = Paginator(ticket_list, 25)
    else:
        ticket_list = ticket_list.order_by('-last_comment_date') #cannot run order by with (assigned_to__isnull=False) filter - GAE issues
        paginator = Paginator(ticket_list, 25)

    if page < 1:
        page = 1
    if page > paginator.num_pages:
        page = paginator.num_pages
    current_page = paginator.page(page)
    tickets = _build_tickets_list(current_page.object_list)

    if is_admin and request.user.is_superuser:
        companies = Space.objects.filter(space_type=SpaceType.CORPORATE, parent=None, is_deleted=False).order_by('title')

    elif is_admin:
        assigned_tickets = Ticket.objects.filter(assigned_to=request.user)
        companies = sorted(set([ticket.company for ticket in assigned_tickets]))
    else:
        companies = []
    return render(request, template, {'tickets' : tickets,
                                      'page' : current_page,
                                      'status' : status,
                                      'ticket_type' : ticket_type,
                                      'company_input' : company_input,
                                      'companies' : companies,
                                      'assignee_input': assignee_input,
                                      'assignees': assignees})

def _build_tickets_list(ticket_list):
    for ticket in ticket_list:
        ticket.last_comment = Comment.getLastComment(ticket)
        ticket.comments_count = int(ticket.comment_set.count())-1
    return ticket_list

@login_required
@user_passes_test(lambda u: u.company != None)
def show_ticket(request, ticket_id):
    comment_form = _handle_add_comment(request, ticket_id)
    if comment_form.is_valid():
        return HttpResponseRedirect('/support/ticket/' + ticket_id)
    ticket = get_object_or_404(Ticket, pk=ticket_id)
    if ticket.company != request.user.company:
        raise Http404
    comment_list = ticket.comment_set.all().order_by('created_date')
    attachments = ticket.ticketattachment_set.all().order_by('created_date')
    return render(request, 'support/ticket.html', {"ticket" : ticket, "comments" : comment_list, 'form' : comment_form, 'attachments' : attachments})

@login_required
@security_token('copy_content')
def admin_show_ticket(request, ticket_id):
    ticket = get_object_or_404(Ticket, pk=ticket_id)
    if not request.user.is_superuser and ticket.assigned_to != request.user:
        return HttpResponseRedirect('/support/admin')
    _handle_assigned_to(request, ticket)
    comment_form = _handle_add_comment(request, ticket_id)
    if comment_form.is_valid():
        return HttpResponseRedirect('/support/admin/ticket/' + ticket_id)
    comment_list = ticket.comment_set.all().order_by('created_date')
    attachments = ticket.ticketattachment_set.all().order_by('created_date')
    users = get_users_from_company(request.user.company)

    lesson_id = None
    if ticket.lesson_url is not None and ticket.lesson_url != '':
        lesson_id = parse_lesson_id(ticket.lesson_url)

    return render(request, 'support/ticket.html', {
        "ticket": ticket,
        "comments": comment_list,
        'form': comment_form,
        'admin': True,
        'attachments': attachments,
        'lesson_id': lesson_id,
        'users': users
    })

def _handle_assigned_to(request, ticket):
    if request.method == 'POST':
        old_assigned_to = request.POST.get('old_assigned_to')
        assigned_to = request.POST.get('assigned_to')
        if old_assigned_to != assigned_to and assigned_to != '0':
            user = User.objects.get(pk=assigned_to)
            comment = Comment(
                            ticket=ticket, 
                            created_date=datetime.datetime.now(), 
                            text='Ticket assigned to %s' % user.username,
                            author=request.user)
            comment.save()
            ticket.last_comment_date = comment.created_date
            ticket.assigned_to = user
            ticket.save()
            send_assignment_notification(ticket, request.user)
            messages.success(request, "User %s has been assigned to this ticket" % user.username)
        elif old_assigned_to != assigned_to and assigned_to == '0':
            comment = Comment(
                            ticket=ticket, 
                            created_date=datetime.datetime.now(), 
                            text='Ticket assigned to no-one',
                            author=request.user)
            comment.save()
            ticket.last_comment_date = comment.created_date
            ticket.assigned_to = None
            ticket.save()
            send_assignment_notification(ticket, request.user)
            messages.success(request, "No one is assigned to this ticket now")

def _handle_add_comment(request, ticket_id):
    if request.method == 'POST':
        comment_form = CommentForm(request.POST)
        if comment_form.is_valid():
            ticket = get_object_or_404(Ticket, pk=ticket_id)
            text = comment_form.cleaned_data['text']
            if text is not None and text != '':
                comment = Comment(
                            ticket=ticket, 
                            created_date=datetime.datetime.now(), 
                            text=text, 
                            author=request.user)
                comment.save()
                ticket.last_comment_date = comment.created_date
                ticket.save()
                send_new_comment_notification(ticket, comment)
                messages.success(request, "Your new comment has been added.")
    else:
        comment_form = CommentForm()
    return comment_form


@login_required
def add_attachment(request, ticket_id, admin=None):
    ticket = get_object_or_404(Ticket, pk=ticket_id)
    if request.method == 'POST':
        form = UploadForm(request.POST, request.FILES)
        if form.is_valid():
            uploaded_file = form.save(False)
            uploaded_file.content_type = request.FILES['file'].content_type
            import cgi
            uploaded_file.filename = cgi.escape(request.FILES['file'].name, True)
            uploaded_file.owner = request.user
            uploaded_file.title = request.POST.get('title', '')
            uploaded_file.save()
            attachment = TicketAttachment(file=uploaded_file, ticket=ticket)
            attachment.save()
            text = 'New attachment added: %s/file/serve/%s' % (settings.BASE_URL, uploaded_file.id)
            comment = Comment(
                    ticket=ticket, 
                    created_date=datetime.datetime.now(), 
                    text=text, 
                    author=request.user)
            comment.save()
            send_new_comment_notification(ticket, comment)
            messages.success(request, "Your attachment has been added.")
            if admin:
                return HttpResponseRedirect('/support/admin/ticket/' + ticket_id)
            else:
                return HttpResponseRedirect('/support/ticket/' + ticket_id)
    else:
        form = UploadForm()
    url = '/support/add_attachment/' + ticket_id
    if admin:
        url = url + '/1'
    upload_url = blobstore.create_upload_url(url)
    return render(request, 'support/attachment.html', {'form' : form, 'upload_url' : upload_url, 'ticket' : ticket_id})


@login_required
@user_passes_test(lambda u: u.company != None)
def add_ticket(request):
    if request.method == 'POST':
        form = TicketForm(request.POST)
        if form.is_valid():
            title = form.cleaned_data['title']
            text = form.cleaned_data['text']
            ticket_type = form.cleaned_data['ticket_type']
            lesson_url = form.cleaned_data['lesson_url']
            now = datetime.datetime.now()
            ticket = Ticket(
                          title=title, 
                          created_date=now, 
                          author=request.user,
                          last_comment_date=now,
                          ticket_type=ticket_type,
                          lesson_url=lesson_url
                          )
            ticket.company = request.user.company
            ticket.save()
            comment = Comment(
                        ticket=ticket, 
                        created_date=now,
                        text=text, 
                        author=request.user)
            comment.save()
            send_new_ticket_notification(ticket, comment)
            messages.success(request, "Your ticket has been added.")
            return HttpResponseRedirect('/support')
    else:
        form = TicketForm()
        if 'lesson_url' in request.GET:
            form.data['lesson_url'] = request.GET.get('lesson_url')
    return render(request, 'support/addticket.html', {'form' : form})

@login_required
def change_status(request, ticket_id, status):
    _handle_status_change(request, ticket_id, status)
    return HttpResponseRedirect('/support/ticket/' + ticket_id)

@login_required
def admin_change_status(request, ticket_id, status):
    _handle_status_change(request, ticket_id, status)
    return HttpResponseRedirect('/support/admin/ticket/' + ticket_id)

def _handle_status_change(request, ticket_id, status):
    ticket = get_object_or_404(Ticket, pk=ticket_id)
    if not request.user.is_superuser and ticket.assigned_to != request.user and ticket.company != request.user.company:
        return HttpResponseRedirect('/support/admin')
    old_status = ticket.status
    ticket.status = status
    ticket.save()

    text = 'Status changed from "%s" to "%s".' % (print_status(old_status), print_status(status))
    comment = Comment(
                    ticket=ticket, 
                    created_date=datetime.datetime.now(), 
                    text=text, 
                    author=request.user)
    comment.save()
    send_status_change_notification(request.user, ticket, old_status, status)
    messages.success(request, text)

def send_assignment_notification(ticket, user):
    context = {'user': user, 'ticket': ticket, 'changer': user, 'settings': settings}
    if user != ticket.assigned_to and ticket.assigned_to is not None:
        subject = '[mAuthor support] New ticket assigned: %s' % ticket.title
        template = 'support/assignee_change.txt'
        send_notification([ticket.assigned_to.email], subject, context, template)
    notify_admins('[mAuthor support] Ticket assigned', context, 'support/admin_assignee_change.txt', ticket)

def send_status_change_notification(changer, ticket, previous_status, new_status):
    context = {
        'user': ticket.author,
        'ticket': ticket,
        'status': new_status,
        'old_status': previous_status,
        'changer': changer,
        'settings': settings
    }
    if changer != ticket.author:
        subject = "[mAuthor support] Status change: %s" % ticket.title
        template = 'support/status_change.txt'
        send_notification([ticket.author.email], subject, context, template)
    notify_admins('[mAuthor support] Ticket status changed', context, 'support/admin_status_change.txt', ticket)

def send_new_comment_notification(ticket, comment):
    context = {
        'user': ticket.author,
        'ticket': ticket,
        'comment': comment,
        'changer': comment.author,
        'settings': settings
    }
    if comment.author != ticket.author:
        subject = "[mAuthor support] New comment: %s" % ticket.title
        template = 'support/new_comment.txt'
        send_notification([ticket.author.email], subject, context, template)
    notify_admins('[mAuthor support] New comment', context, 'support/admin_new_comment.txt', ticket)

def send_new_ticket_notification(ticket, comment):
    context = {'ticket': ticket, 'comment': comment, 'changer': ticket.author, 'settings': settings}
    notify_admins('[mAuthor support] New ticket', context, 'support/admin_new_ticket.txt', ticket)

def send_notification(users, subject, context, template):
    context = Context(context)
    email = loader.get_template(template)
    rendered = email.render(context)
    send_message(settings.SERVER_EMAIL, users, subject, rendered)

def notify_admins(subject, context, template, ticket):
    users = ['learnetic@solwit.com', 'artur.dyro@learnetic.com', 'wojciech.dobkowicz@learnetic.com']
    if ticket.assigned_to is not None:
        users.append(ticket.assigned_to.email)
    send_notification(users, subject, context, template)
