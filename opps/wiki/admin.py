#!/usr/bin/env python
# -*- coding: utf-8 -*-
import reversion

from django.contrib import admin
from django import forms
from django.shortcuts import get_object_or_404
from django.http import HttpResponseRedirect
from django.utils.translation import ugettext_lazy as _

from mptt.admin import MPTTModelAdmin

from .models import Wiki, Suggestion
from .templatetags.wiki_tags import admin_url


class WikiAdmin(reversion.VersionAdmin, MPTTModelAdmin):

    change_list_template = "admin/wiki/wiki/change_list.html"
    list_display = ('title', 'parent', 'long_slug', 'published')
    mptt_indent_field = "title"

    @property
    def model_list(self):
        for model in Wiki.get_wiki_models():
            setattr(model, "meta__", model._meta)
            yield model

    def add_view(self, request, **kwargs):
        if self.model is Wiki:
            wiki_models = Wiki.get_wiki_models()
            if wiki_models:
                return HttpResponseRedirect(admin_url(wiki_models[0], 'add'))
            return HttpResponseRedirect(admin_url(Wiki, "changelist"))
        return super(WikiAdmin, self).add_view(request, **kwargs)

    def changelist_view(self, request, extra_context=None):
        if self.model is not Wiki:
            return HttpResponseRedirect(admin_url(Wiki, "changelist"))
        if not extra_context:
            extra_context = {}
        extra_context["model_list"] = self.model_list
        return super(WikiAdmin, self).changelist_view(request, extra_context)

    def change_view(self, request, object_id, **kwargs):
        wiki = get_object_or_404(Wiki, pk=object_id)
        child_object = wiki.get_child_object()
        if self.model is Wiki and child_object.__class__ is not Wiki:
            change_url = admin_url(
                child_object.__class__,
                "change",
                child_object.pk
            )
            return HttpResponseRedirect(change_url)
        return super(WikiAdmin, self).change_view(request, object_id, **kwargs)

    def get_model_perms(self, request):
        perms = super(WikiAdmin, self).get_model_perms(request)
        perms['show_app'] = self.model is Wiki
        return perms
admin.site.register(Wiki, WikiAdmin)


class SuggestionAdmin(admin.ModelAdmin):
    list_display = ('content_type', 'title', 'content_object', 'user',
                    'status', 'date_insert')

    def has_add_permission(self, request):
        return False
admin.site.register(Suggestion, SuggestionAdmin)
