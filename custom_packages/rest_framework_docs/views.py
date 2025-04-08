from .docs import DocumentationGenerator
from django.shortcuts import render
from django.template.context import RequestContext


def documentation(request, *args, **kwargs):
    docs = DocumentationGenerator().get_docs(as_objects=True)
    return render("rest_framework_docs/docs.html", {'docs': docs},
                              context_instance=RequestContext(request))
