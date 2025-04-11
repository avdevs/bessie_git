from django import template

register = template.Library()


@register.filter
def get_field(form, field_name):
    return form[field_name]


@register.filter
def format_team_name(value):
    return value.replace("-", " ").title()
