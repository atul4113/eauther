from django.db.models import Q

# Example search functionality
def search_models(query):
    from src.myapp.models import MyModel
    return MyModel.objects.filter(
        Q(name__icontains=query) | Q(description__icontains=query)
    )