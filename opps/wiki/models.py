# -*- coding: utf-8 -*-
import uuid
import base64
import pickle

from django.contrib.auth import get_user_model
from django.contrib.auth.models import Permission
from django.contrib.contenttypes import generic
from django.core.urlresolvers import reverse
from django.core.mail import send_mail
from django.db import models
from django.db.models import get_model, get_models
from django.conf import settings
from django.utils.translation import ugettext_lazy as _
from django.utils.text import slugify
from django.utils import timezone
from django.template.loader import render_to_string

from mptt.models import MPTTModel, TreeForeignKey

from opps.core.models import NotUserPublishable, Slugged, Owned, Date
from opps.containers.models import Container
from opps.channels.models import Channel
from opps.core.tags.models import Tagged


class Wiki(MPTTModel, NotUserPublishable, Slugged, Tagged):
    title = models.CharField(_(u"title"), max_length=140)
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
    parent = TreeForeignKey(
        'self',
        related_name='subpage',
        null=True,
        blank=True
    )

    long_slug = models.SlugField(
        _(u"Path name"),
        max_length=255,
        db_index=True,
        editable=False
    )

    inline = models.BooleanField(_(u'inline'), default=False, editable=False)

    PUBLIC_FIELDS = ('title', 'parent', 'tags')
    PUBLIC_FIELDS_WIDGETS = None

    class Meta:
        permissions = (('can_publish', _(u'User can publish automatically')),)

    def __unicode__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.pk:
            self.child_class = self.__class__.__name__
            self.child_app_label = self._meta.app_label

        self.slug = slugify(self.title)
        self.long_slug = self.slug
        parent = self.parent
        while parent:
            self.long_slug = u"{}/{}".format(parent.slug, self.long_slug)
            parent = parent.parent

        super(Wiki, self).save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('wiki-detail', kwargs={'long_slug': self.long_slug})

    @classmethod
    def add_url(cls):
        return reverse('wiki-add', args=(cls._meta.app_label, cls.__name__))

    @classmethod
    def get_wiki_models(cls):
        # Get wiki subclasses
        if not hasattr(cls, '_wiki_models'):
            cls._wiki_models = [
                m for m in get_models() if m not in (Wiki, WikiInline)
                and issubclass(m, Wiki)
            ]
        return cls._wiki_models

    def get_child_object(self):
        child_model = get_model(self.child_app_label, self.child_class)
        if child_model == Wiki:
            return self

        return child_model._default_manager.get(pk=self.pk)

    def get_published_children(self):
        return self.get_children().filter(
            published=True,
            date_available__lte=timezone.now(),
            inline=False
        )

    def get_report_users(self):
        user_model = get_user_model()
        return user_model.objects.filter(report__wiki_id=self.pk)

    def get_voting_users(self):
        user_model = get_user_model()
        return user_model.objects.filter(voting__wiki_id=self.pk)


class WikiInline(Wiki):
    def save(self, *args, **kwargs):
        self.inline = True
        self.published = True
        super(WikiInline, self).save(*args, **kwargs)


class Suggestion(Container):
    STATUS_CHOICES = (
        ('pending', _(u'Pending')),
        ('reject', _(u'Reject')),
        ('accept', _(u'Accept')),
        ('auto', _(u'Auto accepted')),
    )
    content_type = models.ForeignKey('contenttypes.ContentType')
    object_id = models.PositiveIntegerField(
        verbose_name='object name',
        null=True
    )
    content_object = generic.GenericForeignKey()
    serialized_data = models.TextField(_(u'data'))
    status = models.CharField(
        _(u'status'),
        max_length=50,
        choices=STATUS_CHOICES
    )

    class Meta:
        verbose_name = _(u'suggestion')
        verbose_name_plural = _(u'suggestions')

    def save(self, *args, **kwargs):
        self.short_url = 'None'
        self.show_on_root_channel = False
        slug = unicode(uuid.uuid4())
        channel, created = Channel.objects.get_or_create(
            slug='wiki',
            defaults={'name': 'Wiki', 'user': self.user}
        )
        self.channel = channel

        if not self.pk:
            # Send e-mail to user
            email_subject = render_to_string(
                'wiki/email/suggestion_sent_subject.txt',
                {'subject': self}
            )
            email_body = render_to_string(
                'wiki/email/suggestion_sent.txt',
                {'subject': self}
            )
            self.user.email_user(
                ''.join(email_subject.splitlines()),
                email_body,
                settings.DEFAULT_FROM_EMAIL
            )

            # Send e-mail to Wiki Team
            email_subject = render_to_string(
                'wiki/email/new_suggestion_subject.txt',
                {'subject': self}
            )
            email_body = render_to_string(
                'wiki/email/new_suggestion.txt',
                {'subject': self}
            )
            send_mail(
                ''.join(email_subject.splitlines()),
                email_body,
                settings.DEFAULT_FROM_EMAIL,
                settings.OPPS_WIKI_EMAILS
            )
        super(Suggestion, self).save(*args, **kwargs)

    def publish(self, is_auto=False):
        if is_auto:
            self.status = 'auto'
            self.save()
        else:
            self.status = 'accept'
            self.save()
            suggestions_accept = Suggestion.objects.filter(
                user=self.user,
                status='accept'
            ).count()
            USER_CAN_PUBLISH_NUMBER = getattr(
                settings,
                'USER_CAN_PUBLISH_NUMBER',
                100
            )
            if suggestions_accept >= USER_CAN_PUBLISH_NUMBER:
                p = Permission.objects.get_by_natural_key(
                    'can_publish', 'wiki', 'wiki'
                )
                self.user.user_permissions.add(p.pk)

        suggested_obj = pickle.loads(base64.b64decode(self.serialized_data))
        suggested_obj.published = True
        suggested_obj.save()

        # Send e-mail to user
        email_subject = render_to_string(
            'wiki/email/suggestion_accepted_subject.txt',
            {'subject': self}
        )
        email_body = render_to_string(
            'wiki/email/suggestion_accepted.txt',
            {'subject': self}
        )
        self.user.email_user(
            ''.join(email_subject.splitlines()),
            email_body,
            settings.DEFAULT_FROM_EMAIL
        )

    def reject(self):
        self.status = 'reject'
        self.save()

        # Send e-mail to user
        email_subject = render_to_string(
            'wiki/email/suggestion_reject_subject.txt',
            {'subject': self}
        )
        email_body = render_to_string(
            'wiki/email/suggestion_reject.txt',
            {'subject': self}
        )
        self.user.email_user(
            ''.join(email_subject.splitlines()),
            email_body,
            settings.DEFAULT_FROM_EMAIL
        )

    def __unicode__(self):
        return self.status


class Report(Owned, Date):
    wiki = models.ForeignKey('Wiki', verbose_name=_(u'wiki'))

    class Meta:
        verbose_name = _(u'report')
        verbose_name_plural = _(u'reports')
        unique_together = ('user', 'wiki')

    def save(self, *args, **kwargs):
        if not self.pk:
            # Send e-mail to Wiki Team
            email_subject = render_to_string(
                'wiki/email/new_report_subject.txt',
                {'subject': self}
            )
            email_body = render_to_string(
                'wiki/email/new_report.txt',
                {'subject': self}
            )
            send_mail(
                ''.join(email_subject.splitlines()),
                email_body,
                settings.DEFAULT_FROM_EMAIL,
                settings.OPPS_WIKI_EMAILS
            )
        super(Report, self).save(*args, **kwargs)


class Voting(Owned, Date):
    VOTE_CHOICES = ((1, _(u'liked')), (-1, _(u'disliked')))
    wiki = models.ForeignKey('wiki.Wiki', verbose_name=_(u'wiki'))
    vote = models.SmallIntegerField(
        choices=VOTE_CHOICES,
        verbose_name=_(u'vote')
    )

    class Meta:
        unique_together = ('user', 'wiki')

    def __unicode__(self):
        for choice in self.VOTE_CHOICES:
            if self.vote == choice[0]:
                option_chosen = choice[1]
        return u'"{}" was {} by {}'.format(self.wiki, option_chosen,
                                           self.user)
