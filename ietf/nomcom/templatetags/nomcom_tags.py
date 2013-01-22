from django import template

from ietf.nomcom.utils import get_nomcom_by_year

register = template.Library()


@register.filter
def is_chair(user, year):
    if not user or not year:
        return False
    nomcom = get_nomcom_by_year(year=year)
    return nomcom.group.is_chair(user)
