from django import template

register = template.Library()

@register.filter(name='has_group')
def has_group(user, group_name):
    return user.groups.filter(name=group_name).exists()

@register.filter
def add_class(field, css_class):
    """Agregar clase CSS a un campo de formulario"""
    return field.as_widget(attrs={'class': css_class})

@register.filter
def attr(field, attribute):
    """Agregar atributo a un campo de formulario"""
    attrs = {}
    for attr_pair in attribute.split(','):
        attr_name, attr_value = attr_pair.split(':')
        attrs[attr_name] = attr_value
    return field.as_widget(attrs=attrs)