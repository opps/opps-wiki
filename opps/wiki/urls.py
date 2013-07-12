# -*- coding: utf-8 -*-
from django.conf.urls import patterns, url
from django.conf import settings
from django.views.decorators.cache import cache_page
from django.views.generic import TemplateView
from django.contrib import admin

from .views import (WikiListView, WikiDetailView, WikiCreateView,
                    WikiUpdateView, ReportCreateView)


admin.site.index_template = 'admin/opps_admin_index.html'


urlpatterns = patterns(
    '',
    url(r'^$',
        cache_page(settings.OPPS_CACHE_EXPIRE)(WikiListView.as_view()),
        name='wiki-list'),

    url(r'^report/$', ReportCreateView.as_view(), name='wiki-report'),

    url(r'^(?P<app_label>\w+)/(?P<child_class>\w+)/add/$',
        WikiCreateView.as_view(),
        name='wiki-add'),
    url(r'^(?P<long_slug>[\w//-]+)/edit/$', WikiUpdateView.as_view(),
        name='wiki-edit'),

    url(r'^success_suggested/$',
        TemplateView.as_view(template_name='wiki/success_msg.html'),
        name='success_suggestion_msg'),
    url(r'^success_published/$',
        TemplateView.as_view(template_name='wiki/success_published.html'),
        name='success_published_msg'),

    url(r'^(?P<long_slug>[\w//-]+)/$',
        cache_page(settings.OPPS_CACHE_EXPIRE)(WikiDetailView.as_view()),
        name='wiki-detail'),
)
