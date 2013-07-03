# -*- coding: utf-8 -*-

from django.db import models
from django.db.models import get_model
from django.conf import settings
from django.utils.translation import ugettext_lazy as _

from taggit.models import TaggedItemBase
from taggit.managers import TaggableManager

from opps.core.models import NotUserPublishable, Slugged, Imaged


class TaggedWiki(TaggedItemBase):
    """Tag for wiki """
    content_object = models.ForeignKey('wiki.WikiContent')


class WikiContent(NotUserPublishable, Slugged):
    title = models.CharField(_(u"title"), max_length=140)
    tags = TaggableManager(
        blank=True,
        through=TaggedWiki,
        verbose_name=u'Tags'
    )
    child_class = models.CharField(
        _(u'child class'),
        max_length=30,
        db_index=True,
        editable=False
    )
    child_app_label = models.CharField(
        _(u'child app label'),
        max_length=30,
        db_index=True,
        editable=False
    )

    def __unicode__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.pk:
            self.child_class = self.__class__.__name__
            self.child_app_label = self._meta.app_label
        super(WikiContent, self).save(*args, **kwargs)

    def get_child_model(self):
        child_model = get_model(self.child_app_label, self.child_class)
        if child_model == WikiContent:
            return self

        return child_model._default_manager.get(pk=self.pk)


class Page(WikiContent):
    content = models.TextField(_(u'content'))


class Genre(models.Model):
    name = models.CharField(max_length=200)


class BaseArtist(WikiContent):
    biography = models.TextField()
    # it will use wikicontent title as name
    genre = models.ForeignKey('wiki.Genre', null=True, blank=True)
    albums = models.ManyToManyField('wiki.Album')

    class Meta:
        abstract = True


class Artist(BaseArtist):
    birthday = models.DateField()
    death = models.DateField(null=True, blank=True)
    # verify death after birthday
    band = models.ForeignKey('wiki.Band', null=True, blank=True)


class Band(models.Model):
    biography = models.TextField()
    beginning = models.DateField()
    end = models.DateField(null=True, blank=True)
    albums = models.ManyToManyField('wiki.Album', related_name=u'albums')


class Album(models.Model):
    thumbnail = models.ImageField(upload_to='thumbnails')
    year = models.PositiveSmallIntegerField()


# embed (images, audios and videos)
