# -*- coding: utf-8 -*-
from django.db import models
from django.utils.translation import ugettext_lazy as _

from opps.wiki.models import Wiki


class Genre(models.Model):
    name = models.CharField(_(u'name'), max_length=200)

    def __unicode__(self):
        return self.name


class Embed(models.Model):
    embed = models.TextField(_(u'embed'), )

    def __unicode__(self):
        return self.embed


class RecordLabel(models.Model):
    name = models.CharField(_(u'name'), max_length=200)

    def __unicode__(self):
        return self.name


class BaseArtist(Wiki):
    biography = models.TextField(_(u'biography'), )
    # it will use Wiki title as name
    genre = models.ForeignKey('Genre', null=True, blank=True)
    albums = models.ManyToManyField('Album')
    embed = models.ForeignKey('Embed')

    class Meta:
        abstract = True

    def __unicode__(self):
        return self.title


class Artist(BaseArtist):
    birthday = models.DateField(_(u'birthday'), )
    death = models.DateField(_(u'death'), null=True, blank=True)
    # verify death after birthday
    band = models.ForeignKey('Band', null=True, blank=True)

    def __unicode__(self):
        return self.title


class Band(BaseArtist):
    beginning = models.DateField(_(u'beginning'), )
    end = models.DateField(_(u'end'), null=True, blank=True)

    def __unicode__(self):
        return self.title


class Track(models.Model):
    album = models.ForeignKey('Album')
    name = models.CharField(_(u'name'), max_length=200)
    record_label = models.ForeignKey('RecordLabel', null=True, blank=True)
    year = models.PositiveSmallIntegerField(_(u'year'), null=True, blank=True)

    def __unicode__(self):
        return self.name


class Album(models.Model):
    name = models.CharField(_(u'name'), max_length=200)
    thumbnail = models.ImageField(_(u'thumbnail'), upload_to='thumbnails')
    year = models.PositiveSmallIntegerField(_(u'year'), )

    def __unicode__(self):
        return self.name
