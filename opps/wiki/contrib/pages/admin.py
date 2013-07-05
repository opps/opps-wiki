# -*- coding: utf-8 -*-
from django.contrib import admin
from django import forms

from redactor.widgets import RedactorEditor
from opps.wiki.admin import WikiAdmin

from .models import Page


class PageAdminForm(forms.ModelForm):
    class Meta:
        model = Page
        widgets = {'content': RedactorEditor()}


class PageAdmin(WikiAdmin):
    form = PageAdminForm
admin.site.register(Page, PageAdmin)
