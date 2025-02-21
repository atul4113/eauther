from mauthor.metadata.models import Definition, MetadataValue, PageMetadata
import copy

def get_metadata_definitions(company):
    return Definition.objects.filter(company=company).order_by('order')

def get_metadata_values(content):
    return MetadataValue.objects.filter(content=content, page=None).order_by('order')

def get_metadata_values_and_definitions(content, company):
    definitions = get_metadata_definitions(company)
    metadata_values = list(get_metadata_values(content))

    used_definitions = [value.name for value in metadata_values]
    unused_definitions = [definition for definition in definitions if definition.name not in used_definitions]
    for definition in unused_definitions:
        definition.unused = True
    metadata_values.extend(unused_definitions)
    metadata_values = sorted(metadata_values, key=lambda value: value.order)
    return metadata_values

def get_page_metadata(content, company=None):
    pagemetada = PageMetadata.objects.filter(content=content)
    if company is not None:
        definitions = get_metadata_definitions(company)
    else:
        definitions = []
    for page in pagemetada:
        metadata_values = list(MetadataValue.objects.filter(content=content, page=page).order_by('order'))
        used_definitions = [value.name for value in metadata_values]
        unused_definitions = [definition for definition in definitions if definition.name not in used_definitions]
        for definition in unused_definitions:
            definition.unused = True
        metadata_values.extend(unused_definitions)
        page.metadata_values = sorted(metadata_values, key=lambda value: value.order)
    return pagemetada

def update_page_metadata(content):
    if not content.enable_page_metadata:
        return
    pages = content.get_pages_data()
    existing_metadata = PageMetadata.objects.filter(content=content)
    for metadata in existing_metadata:
        metadata_found = False
        for page in pages:
            if page['id'] != metadata.page_id:
                continue
            metadata.title = page['title']
            metadata.is_enabled = True
            metadata.save()
            metadata_found = True
            page['found'] = True
            break
        if not metadata_found:
            metadata.delete()
            
    for page in pages:
        if 'found' not in page and page['id'] is not None:
            metadata = PageMetadata(content=content, page_id=page['id'])
            metadata.tags = content.tags
            metadata.description = content.description
            metadata.short_description = content.short_description
            metadata.title = page['title']
            metadata.is_enabled = True
            metadata.save()

def toggle_page_metadata(content, enabled=True):
    content.enable_page_metadata = enabled
    pagemetadata = PageMetadata.objects.filter(content=content)
    for pm in pagemetadata:
        pm.is_enabled = enabled
        pm.save()
        
def save_metadata_from_request(request, content):
    MetadataValue.objects.filter(content=content, page=None).delete()
    types = request.POST.getlist('type')
    names = request.POST.getlist('name')
    descriptions = request.POST.getlist('metadata_description')
    values = request.POST.getlist('values')
    unused_flags = request.POST.getlist('unused')
    entered_value = request.POST.getlist('entered_value')
    for counter, current_type in enumerate(types):
        if unused_flags[counter] == 'false':
            definition = MetadataValue(company=request.user.company,
                                    field_type=current_type,
                                    name=names[counter],
                                    description=descriptions[counter],
                                    value=values[counter],
                                    order=counter,
                                    content=content,
                                    entered_value=entered_value[counter])
            definition.save()

def copy_page_metadata(content_from, content_to, translate_ids):
    if content_from.enable_page_metadata:
        content_to.enable_page_metadata = True
        content_to.save()
        pagemetada = PageMetadata.objects.filter(content=content_from)
        for metadata in pagemetada:
            if metadata.page_id in list(translate_ids.keys()):
                new_page_id = translate_ids[metadata.page_id]
                if new_page_id is None:
                    new_page_id = metadata.page_id
                new_metadata = copy.deepcopy(metadata)
                new_metadata.id = None
                new_metadata.content = content_to
                new_metadata.page_id = new_page_id
                new_metadata.save()
                extended_page_metadata = MetadataValue.objects.filter(content=content_from, page=metadata)
                for epm in extended_page_metadata:
                    new_epm = copy.deepcopy(epm)
                    new_epm.id = None
                    new_epm.content = content_to
                    new_epm.page = new_metadata
                    new_epm.save()

def copy_metadata(content_from, content_to):
    metadata_values = get_metadata_values(content_from)
    for value in metadata_values:
        new_value = copy.deepcopy(value)
        new_value.id = None
        new_value.content = content_to
        new_value.save()

    if content_from.enable_page_metadata:
        content_to.enable_page_metadata = True
        pagemetada = PageMetadata.objects.filter(content=content_from)
        for metadata in pagemetada:
            new_metadata = copy.deepcopy(metadata)
            new_metadata.id = None
            new_metadata.content = content_to
            new_metadata.save()
            extended_page_metadata = MetadataValue.objects.filter(content=content_from, page=metadata)
            for epm in extended_page_metadata:
                new_epm = copy.deepcopy(epm)
                new_epm.id = None
                new_epm.content = content_to
                new_epm.page = new_metadata
                new_epm.save()