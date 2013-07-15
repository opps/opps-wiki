# -*- coding: utf-8 -*-

from django import template
from django.core.urlresolvers import reverse, NoReverseMatch


register = template.Library()


@register.assignment_tag
def admin_url(model, page, *args, **kwargs):
    """
    Tag to return admin url of given model
    """

    try:
        return reverse('admin:{}_{}_{}'.format(
            model._meta.app_label,
            model._meta.object_name.lower(),
            page
        ), args=args, kwargs=kwargs)
    except:
        return ''


@register.simple_tag(takes_context=True)
def set_app_list(context):
    new_app_list = []
    for app in context['app_list']:
        new_app = dict(app)
        new_app['models'] = []
        for model in app['models']:
            if not 'show_app' in model['perms'] or model['perms']['show_app']:
                new_app['models'].append(model)
        if new_app['models']:
            new_app_list.append(new_app)

    context['app_list'] = new_app_list
    return ''
