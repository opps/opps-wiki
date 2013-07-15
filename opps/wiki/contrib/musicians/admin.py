# -*- coding: utf-8 -*-

from django.contrib import admin
from django import forms

from opps.wiki.admin import WikiAdmin

from .models import Album, Musician, Embed


class EmbedInline(admin.TabularInline):
    model = Embed
    fk_name = 'musician'
    fields = ('title', 'embed_text')


class MusicianAdmin(WikiAdmin):
    inlines = [EmbedInline, ]
admin.site.register(Musician, MusicianAdmin)


class EmbedAdmin(WikiAdmin):
    pass
admin.site.register(Embed, EmbedAdmin)


class AlbumAdmin(WikiAdmin):
    pass
admin.site.register(Album, AlbumAdmin)
