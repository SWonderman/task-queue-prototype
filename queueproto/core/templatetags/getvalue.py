from django import template

register = template.Library()


@register.filter
def getvalue(dictionary, key):
    return dictionary[key]
