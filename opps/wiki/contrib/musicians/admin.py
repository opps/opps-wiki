# -*- coding: utf-8 -*-

from django.contrib import admin
from django import forms

from opps.wiki.admin import WikiAdmin

from .models import Album, Musician


admin.site.register(Album, WikiAdmin)
admin.site.register(Musician, WikiAdmin)
