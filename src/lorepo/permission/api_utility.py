from libraries.utility.helpers import get_object_or_none
from lorepo.spaces.models import Space


def get_filtered_publication_data(publication_tuple, space_access_dict):
    space_id, _, _ = publication_tuple
    space = space_access_dict[space_id].space

    return {
        "id": space.id,
        "name": space.title,
        "actual_roles": space_access_dict[space_id].roles,
    }


def get_publication(publication_element_id):
    publication = get_object_or_none(Space, id=publication_element_id)
    if publication:
        return {
            "id": publication.id,
            "name": publication.title
        }
    else:
        return None


def get_project_data(child_list, project_id, space_access_dict):
    project_space = space_access_dict[project_id].space
    publications = [x for x in map(get_publication, child_list) if x is not None]
    data = {
        "id": project_space.id,
        "name": project_space.title,
        "actual_roles": space_access_dict[project_id].roles,
        "publications": publications
    }
    return data