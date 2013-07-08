# -*- coding: utf-8 -*-
from django.conf.urls import patterns, url
from django.conf import settings
from django.views.decorators.cache import cache_page
from django.contrib import admin

from .views import WikiListView, WikiDetailView


admin.site.index_template = 'admin/opps_admin_index.html'


urlpatterns = patterns(
    '',
    url(r'^$',
        cache_page(settings.OPPS_CACHE_EXPIRE)(WikiListView.as_view()),
        name='wiki-list'),
    url(r'^(?P<long_slug>[\w//-]+)/$',
        cache_page(settings.OPPS_CACHE_EXPIRE)(WikiDetailView.as_view()),
        name='wiki-detail'),
)
