# -*- coding: utf-8 -*-

from django.contrib.sites.models import get_current_site
from django.http import Http404
from django.utils import timezone
from django.views.generic import ListView, DetailView

from .models import Wiki


class BaseWikiView(object):
    def get_queryset(self):
        self.site = get_current_site(self.request)
        qs = super(BaseWikiView, self).get_queryset()
        return qs.filter(
            site=self.site,
            published=True,
            date_available__lte=timezone.now()
        )

    def get_template_names(self):
        names = super(BaseWikiView, self).get_template_names()
        wiki_name = u'wiki/wiki{}.html'.format(self.template_name_suffix)
        if wiki_name not in names:
            names.append(wiki_name)
        return self.get_domain_template_names(names) + names

    def get_domain_template_names(self, template_names):
        domain_names = []
        for name in template_names:
            domain_names.append(u'{}/{}'.format(self.site.domain, name))
        return domain_names

    def get_context_data(self, **kwargs):
        context = super(BaseWikiView, self).get_context_data(**kwargs)
        context['wiki_models'] = [w._meta.verbose_name for w \
                                  in Wiki.get_wiki_models()]
        return context


class WikiListView(BaseWikiView, ListView):
    model = Wiki

    def get_queryset(self):
        qs = super(WikiListView, self).get_queryset()
        return qs.filter(parent__isnull=True)


class WikiDetailView(BaseWikiView, DetailView):
    model = Wiki
    slug_field = 'long_slug'
    slug_url_kwarg = 'long_slug'

    def get_object(self, queryset=None):
        wiki_obj = super(WikiDetailView, self).get_object(queryset)

        for parent in wiki_obj.get_ancestors():
            if not parent.published:
                raise Http404()
        return wiki_obj.get_child_object()
