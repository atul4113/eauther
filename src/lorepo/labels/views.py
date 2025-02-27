# -*- coding: utf-8 -*-
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404, render
from src.lorepo.labels.forms import LabelForm
from src.lorepo.labels.models import Label


#
# Index
#
@login_required
def index(request):
    labels = request.user.label_set.all()
    
    return render(request, 'labels/index.html', {'labels' : labels})


@login_required
def addLabel(request):
    if request.method == 'POST':
        form = LabelForm(request.POST)
        if form.is_valid():
            title = form.cleaned_data['title']
            label = Label(title=title, user=request.user) 
            label.save()
        
    return HttpResponseRedirect('/labels')
    

@login_required
def rename(request, label_id):
    label = get_object_or_404(Label, pk=label_id)
    if request.method == 'POST':
        form = LabelForm(request.POST)
        if form.is_valid():
            label.title = form.cleaned_data['title']
            label.save()
            return HttpResponseRedirect('/labels')
        
    return render(request, 'labels/rename.html', {'label' : label})
    
