# -*- coding: utf-8 -*-
from django.db import models
from django.utils.translation import ugettext_lazy as _

from redactor.widgets import RedactorEditor

from opps.wiki.models import Wiki, WikiInline


class Genre(models.Model):
    name = models.CharField(_(u'name'), max_length=200)

    def __unicode__(self):
        return self.name


class Musician(Wiki):
    PUBLIC_FIELDS = ('title', 'type', 'genre', 'birthday', 'end', 'biography',
                     'tags')
    PUBLIC_FIELDS_WIDGETS = {'biography': RedactorEditor()}
    TYPE_CHOICES = (('artist', _(u'Artist')), ('band', _(u'Band')))
    biography = models.TextField(_(u'biography'))
    # it will use Wiki title as name
    genre = models.ForeignKey('Genre', null=True, blank=True,
                              verbose_name=_(u'genre'))
    birthday = models.DateField(_(u'birthday'))
    type = models.CharField(_(u'type'), max_length=10, choices=TYPE_CHOICES)
    end = models.DateField(_(u'end/death'), null=True, blank=True)

    class Meta:
        verbose_name = _(u'musician')
        verbose_name_plural = _(u'musician')

    def __unicode__(self):
        return self.title


class Album(Wiki):
    PUBLIC_FIELDS = ('title', 'name', 'tracks', 'musician', 'thumbnail',
                     'record_label', 'year', 'tags')
    name = models.CharField(_(u'name'), max_length=200)
    tracks = models.TextField(_(u'tracks'))
    musician = models.ForeignKey('Musician', verbose_name=_(u'musician'))
    thumbnail = models.ImageField(_(u'thumbnail'), upload_to='thumbnails')
    record_label = models.CharField(_(u'record label'), max_length=200,
                                    null=True, blank=True)
    year = models.PositiveSmallIntegerField(_(u'year'))

    class Meta:
        verbose_name = _(u'musician album')
        verbose_name_plural = (u'musician albums')

    def save(self, *args, **kwargs):
        self.parent_id = self.musician_id
        super(Album, self).save(*args, **kwargs)

    def __unicode__(self):
        return self.name


class Embed(WikiInline):
    musician = models.ForeignKey('Musician', verbose_name=_(u'musician'))
    embed_text = models.TextField(_(u'embed'))

    PUBLIC_FIELDS = ('title', 'musician', 'embed_text')

    class Meta:
        verbose_name = _(u'musician embed')
        verbose_name_plural = _(u'musician embeds')

    def __unicode__(self):
        return self.embed_text

    def save(self, *args, **kwargs):
        self.parent_id = self.musician_id
        self.published = True
        super(Embed, self).save(*args, **kwargs)
