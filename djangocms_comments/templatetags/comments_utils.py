import six
from django import template
import hashlib

register = template.Library()


# {{ "some identifier"|md5 }} -> g87g98ht02497hg349ugh3409h34
@register.filter(name='md5')
def md5_string(value):
    value = six.b(value)
    return hashlib.md5(value).hexdigest()


@register.filter('substract')
def subtract(value, arg):
    return value - arg
