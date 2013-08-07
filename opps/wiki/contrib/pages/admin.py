# -*- coding: utf-8 -*-

from django.contrib import admin
from django import forms

from opps.core.widgets import OppsEditor
from opps.wiki.admin import WikiAdmin

from .models import Page


class PageAdminForm(forms.ModelForm):
    class Meta:
        model = Page
        widgets = {'content': OppsEditor()}


class PageAdmin(WikiAdmin):
    form = PageAdminForm
admin.site.register(Page, PageAdmin)
