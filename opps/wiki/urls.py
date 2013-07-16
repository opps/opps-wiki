# -*- coding: utf-8 -*-
from django.conf.urls import patterns, url
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.views.decorators.cache import cache_page
from django.views.generic import TemplateView
from django.contrib import admin

from .views import (WikiListView, WikiDetailView, WikiCreateView,
                    WikiUpdateView, ReportCreateView, VotingView)


admin.site.index_template = 'admin/opps_admin_index.html'


urlpatterns = patterns(
    '',
    url(r'^$',
        cache_page(settings.OPPS_CACHE_EXPIRE)(WikiListView.as_view()),
        name='wiki-list'),

    url(r'^report/$',
        login_required(ReportCreateView.as_view()),
        name='wiki-report'),

    url(r'^(?P<app_label>\w+)/(?P<child_class>\w+)/add/$',
        login_required(WikiCreateView.as_view()),
        name='wiki-add'),
    url(r'^(?P<long_slug>[\w//-]+)/edit/$',
        login_required(WikiUpdateView.as_view()),
        name='wiki-edit'),

    url(r'^success_suggested/$',
        cache_page(settings.OPPS_CACHE_EXPIRE)(TemplateView.as_view(
            template_name='wiki/success_msg.html')),
        name='success_suggestion_msg'),
    url(r'^success_published/$',
        cache_page(settings.OPPS_CACHE_EXPIRE)(TemplateView.as_view(
            template_name='wiki/success_published.html')),
        name='success_published_msg'),

    url(r'^voting/$',
        login_required(VotingView.as_view()),
        name='wiki-voting'),

    url(r'^(?P<long_slug>[\w//-]+)/$',
        cache_page(settings.OPPS_CACHE_EXPIRE)(WikiDetailView.as_view()),
        name='wiki-detail'),
)
