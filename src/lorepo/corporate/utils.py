from src.lorepo.corporate.models import CorporateLogo
from src.lorepo.mycontent.models import ContentSpace, Content
from src.lorepo.spaces.util import get_spaces_subtree
from django.conf import settings
from src.lorepo.filestorage.utils import resize_image
from google.cloud import storage


def set_uploaded_file(uploaded_file, user, corporate_logo_list, space, content_type):
    uploaded_file.owner = user
    uploaded_file.content_type = content_type
    uploaded_file.save()

    # Resize image and upload to Google Cloud Storage
    resized_image_path = resize_image(uploaded_file, settings.LOGO_SIZE["width"], settings.LOGO_SIZE["height"])

    # Store file in Cloud Storage
    storage_client = storage.Client()
    bucket_name = settings.GCS_BUCKET_NAME  # Ensure this is defined in settings
    bucket = storage_client.bucket(bucket_name)

    blob = bucket.blob(resized_image_path)
    blob.upload_from_filename(resized_image_path)

    uploaded_file.path = f"gs://{bucket_name}/{resized_image_path}"
    uploaded_file.file = uploaded_file.path
    uploaded_file.save()

    if not corporate_logo_list:
        cl = CorporateLogo(logo=uploaded_file, space=space)
    else:
        cl = corporate_logo_list[0]
        cl.logo = uploaded_file
    cl.save()


def is_in_public_category(content, public_category):
    if public_category is None:
        return False
    spaces = get_spaces_subtree(public_category.id)
    spaces.add(public_category)
    return ContentSpace.objects.filter(space__in=spaces, content=content).exists()


def get_contents(space, is_trash=False, order_by='-modified_date'):
    return Content.objects.filter(spaces=str(space.id), is_deleted=is_trash).order_by(order_by)


def get_spaces_path_for_corporate_content(content, space_filter):
    """Gets the spaces path for a given content."""
    space = next((cs.space for cs in content.contentspace_set.all() if space_filter(cs.space)), None)
    spaces = []

    while space and not space.is_top_level():
        if space.parent.is_second_level():
            spaces.append(space)
            space.project = space
        space = space.parent

    spaces.reverse()
    return spaces


def get_division_for_space(space):
    while space and not space.is_second_level():
        space = space.parent
    return space


def get_contents_from_company(company, content_filter):
    return [content for content in Content.objects.filter(spaces=str(company.id)) if content_filter(content)]


def get_publication_for_space(space):
    if not space.parent:
        return None
    while space.parent and not space.parent.is_second_level():
        space = space.parent
    return space


def check_manage_access_rights(space_access_set):
    return any(not sa.space.is_private() and sa.has_permission("SPACE_ACCESS_MANAGE") for sa in space_access_set)


def get_space_accesses_to_projects(space_access_set):
    return [sa for sa in space_access_set if sa.space.is_corporate() and not sa.space.is_company()]
