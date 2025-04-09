from django.shortcuts import render
from drf_spectacular.generators import SchemaGenerator  # Use drf-spectacular for docs


def documentation(request, *args, **kwargs):
    generator = SchemaGenerator()
    schema = generator.get_schema(request=request, public=True)  # Get API schema
    return render(request, "rest_framework_docs/docs.html", {'docs': schema})
