# -*- coding: utf-8 -*-
from django.db import models
from django.utils.translation import ugettext_lazy as _

from redactor.widgets import RedactorEditor

from opps.wiki.models import Wiki


class Page(Wiki):
    PUBLIC_FIELDS = ('title', 'content', 'parent', 'tags')
    PUBLIC_FIELDS_WIDGETS = {'content': RedactorEditor()}
    content = models.TextField(_(u'content'), )
