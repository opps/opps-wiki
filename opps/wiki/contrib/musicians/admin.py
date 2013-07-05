# -*- coding: utf-8 -*-
from django.contrib import admin
from django import forms

from opps.wiki.admin import WikiAdmin

from .models import Artist, Band


admin.site.register(Artist, WikiAdmin)
admin.site.register(Band, WikiAdmin)
