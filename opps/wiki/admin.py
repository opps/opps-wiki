#!/usr/bin/env python
# -*- coding: utf-8 -*-
import reversion
import pickle

from difflib import ndiff

from django import forms
from django.forms.models import modelform_factory
from django.core.exceptions import PermissionDenied
from django.contrib import admin, messages
from django.contrib.admin.util import unquote
from django.shortcuts import get_object_or_404, render
from django.http import Http404, HttpResponseRedirect, HttpResponse
from django.utils.translation import ugettext_lazy as _

from mptt.admin import MPTTModelAdmin

from .models import Wiki, Suggestion
from .templatetags.wiki_tags import admin_url


class WikiAdmin(reversion.VersionAdmin, MPTTModelAdmin):

    change_list_template = "admin/wiki/wiki/change_list.html"
    list_display = ('title', 'parent', 'child_class', 'long_slug', 'published')
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
    list_display = ('title', 'content_type', 'content_object', 'user',
                    'status', 'date_insert')

    def has_add_permission(self, request):
        return False

    def change_view(self, request, object_id, form_url='', extra_context=None):
        obj = self.get_object(request, unquote(object_id))
        if not self.has_change_permission(request, obj):
            raise PermissionDenied

        if obj is None:
            raise Http404()

        if request.method == 'POST':
            accept = request.POST.get('accept')
            reject = request.POST.get('reject')
            if accept:
                obj.publish()
                self.message_user(
                    request,
                    _(u'Suggestion published successfully'),
                    messages.SUCCESS
                )
            elif reject:
                obj.reject()
                self.message_user(
                    request,
                    _(u'Suggestion rejected successfully'),
                    messages.SUCCESS
                )
            return HttpResponseRedirect(admin_url(Suggestion, "changelist"))

        suggested_obj = pickle.loads(obj.serialized_data)
        wiki_model = obj.content_type.model_class()
        original_obj = obj.content_object

        compare_data = []
        for field in wiki_model.PUBLIC_FIELDS:
            cur_value = unicode(getattr(original_obj, field, '') or '')
            new_value = unicode(getattr(suggested_obj, field, '') or '')
            diff = ndiff(cur_value.splitlines(1), new_value.splitlines(1))
            compare_data.append((field, cur_value, new_value, ''.join(diff)))

        template_data = {
            'opts': self.model._meta,
            'has_change_permission': self.has_change_permission(request, obj),
            'suggestion_obj': obj,
            'compare_data': compare_data,
        }

        return render(request, 'admin/suggestion_form.html', template_data)
admin.site.register(Suggestion, SuggestionAdmin)
