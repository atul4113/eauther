from django import template
import logging

register = template.Library()

@register.inclusion_tag('course/build_list.html')
def build_list(chapters, course_id, back_url, project_id):
    return { 'chapters' : chapters, 'course_id' : course_id, 'back_url' : back_url, 'project_id' : project_id }

@register.inclusion_tag('course/build_lessons_list.html')
def build_lessons_list(publications):
    return { 'publications' : publications }

@register.inclusion_tag('course/build_add_resources_tree.html')
def build_add_resources_tree(chapters):
    return { 'chapters' :  chapters }