from django.urls import path
from src.mauthor.lessons_parsers.views import (
    ChangePropertiesView,
    RemoveDescriptorsView,
    fix_properties_async,  # Import the view function
    remove_descriptors_async,  # Import the view function
)
from src.mauthor.lessons_parsers.api import get_properties, addon_exist

urlpatterns = [
    # View URLs
    path('change_properties/<int:space_id>/', ChangePropertiesView.as_view()),
    path('fix_properties_async/<int:user_id>/<int:space_id>/', fix_properties_async),  # Use the imported function
    path('remove_descriptors/<int:space_id>/', RemoveDescriptorsView.as_view()),
    path('remove_descriptors_async/<int:user_id>/<int:space_id>/', remove_descriptors_async),  # Use the imported function

    # API URLs
    path('get_properties', get_properties),
    path('addon_exist', addon_exist),
]