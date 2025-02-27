import re
from django.db.models import Q
from src.mauthor.metadata.util import get_metadata_values, get_page_metadata
from src.lorepo.spaces.models import SpaceAccess
from src.lorepo.spaces.util import get_space_for_content

DEFAULT_SEARCH_LIMIT = 10


def update_index(content):
    """
    Updates the search index for a given content.
    If the content is deleted, it is removed from the index.
    Otherwise, the content is indexed with its metadata.
    """
    if content.is_deleted:
        # If the content is deleted, remove it from the index (if it exists)
        content.search_indexed = False
        content.save()
    else:
        # Index the content with its metadata
        space_type = get_space_for_content(content).space_type
        custom_metadata = get_metadata_values(content)
        page_metadata = get_page_metadata(content)

        # Combine all searchable fields into a single text field
        searchable_text = (
            f"{content.title.lower()} {content.tags.lower()} "
            f"{content.short_description.lower()} {content.description.lower()} "
            f"{' '.join([metadata.entered_value.lower() for metadata in custom_metadata])} "
            f"{' '.join([page.title.lower() + ' ' + page.tags.lower() + ' ' + page.description.lower() + ' ' + page.short_description.lower() + ' ' + ' '.join([extended.entered_value.lower() for extended in page.metadata_values]) for page in page_metadata])}"
        )

        # Update the content's searchable fields in the database
        content.searchable_text = searchable_text
        content.space_type = space_type
        content.search_indexed = True
        content.save()


def search_index(query, user, page=1, limit=DEFAULT_SEARCH_LIMIT):
    """
    Searches the index for content matching the query.
    Filters results based on the user's space access.
    """
    # Parse the query to remove unsupported characters
    query = parse_query(query)

    # Get the spaces the user has access to
    space_ids = SpaceAccess.objects.filter(user=user).values_list('space', flat=True)

    # Build the search query using Django's ORM
    search_query = Q(searchable_text__icontains=query) & Q(spaces__in=space_ids) & Q(search_indexed=True)

    # Perform the search
    results = Content.objects.filter(search_query).order_by('-created_date')

    # Paginate the results
    start = (page - 1) * limit
    end = start + limit
    return results[start:end]


def get_spaces_query(user):
    """
    Generates a query string for spaces the user has access to.
    """
    space_ids = SpaceAccess.objects.filter(user=user).values_list('space', flat=True)
    return f"spaces:({' OR '.join([str(space_id) for space_id in space_ids])})"


def parse_query(query):
    """
    Clears the query from unsupported operations and characters.
    """
    query = query.replace('\\', ' ')

    # Remove tokenizing characters
    tokenizing_chars = ['!', '"', '%', '(', ')', '*', ',', '|', '/', '[',
                        ']', '^', '`', ':', '=', '>', '<', '?', '@', '{',
                        '}', '~', '$']
    for char in tokenizing_chars:
        query = query.replace(char, ' ')

    # Remove - or + preceded by whitespace
    query = re.sub(r'(\s|^)([-+]+)', ' ', query)

    # Remove - followed by whitespace
    query = re.sub(r'([-]+)(\s|$)', ' ', query)

    return query.strip()