#!/usr/bin/env python
# -*- coding: utf-8 -*-
import reversion

from django.contrib import admin
from django import forms
from django.shortcuts import get_object_or_404
from django.http import HttpResponseRedirect
from django.utils.translation import ugettext_lazy as _

from redactor.widgets import RedactorEditor

from .models import Wiki, Page, Artist
from .templatetags.wiki_tags import admin_url


class WikiAdmin(reversion.VersionAdmin):

    change_list_template = "admin/wiki/wiki/change_list.html"

    @property
    def model_list(self):
        for model in Wiki.get_wiki_models():
            setattr(model, "meta__", model._meta)
            yield model

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


class PageAdminForm(forms.ModelForm):
    class Meta:
        model = Page
        widgets = {'content': RedactorEditor()}


class PageAdmin(WikiAdmin):
    form = PageAdminForm
admin.site.register(Page, PageAdmin)
admin.site.register(Artist, WikiAdmin)
