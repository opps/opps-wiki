# -*- coding: utf-8 -*-
from django.db import models
from django.utils.translation import ugettext_lazy as _

from opps.wiki.models import Wiki


class Genre(models.Model):
    name = models.CharField(_(u'name'), max_length=200)

    def __unicode__(self):
        return self.name


class Embed(models.Model):
    musician = models.ForeignKey('Musician', verbose_name=_(u'musician'))
    embed = models.TextField(_(u'embed'))

    def __unicode__(self):
        return self.embed


class Musician(Wiki):
    PUBLIC_FIELDS = ('title', 'type', 'genre', 'birthday', 'end', 'biography')
    TYPE_CHOICES = (('artist', _(u'Artist')), ('band', _(u'Band')))
    biography = models.TextField(_(u'biography'))
    # it will use Wiki title as name
    genre = models.ForeignKey('Genre', null=True, blank=True,
                              verbose_name=_(u'genre'))
    birthday = models.DateField(_(u'birthday'))
    type = models.CharField(_(u'type'), max_length=10, choices=TYPE_CHOICES)
    end = models.DateField(_(u'end/death'), null=True, blank=True)

    def __unicode__(self):
        return self.title


class Album(Wiki):
    PUBLIC_FIELDS = ('title', 'name', 'tracks', 'musician', 'thumbnail',
                     'record_label', 'year')
    name = models.CharField(_(u'name'), max_length=200)
    tracks = models.TextField(_(u'tracks'))
    musician = models.ForeignKey('Musician', verbose_name=_(u'musician'))
    thumbnail = models.ImageField(_(u'thumbnail'), upload_to='thumbnails')
    record_label = models.CharField(_(u'record label'), max_length=200,
                                    null=True, blank=True)
    year = models.PositiveSmallIntegerField(_(u'year'))

    def save(self, *args, **kwargs):
        self.parent = self.musician
        super(Album, self).save(*args, **kwargs)

    def __unicode__(self):
        return self.name
