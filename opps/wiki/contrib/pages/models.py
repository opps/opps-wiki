# -*- coding: utf-8 -*-

from django.db import models
from django.utils.translation import ugettext_lazy as _

from opps.core.widgets import OppsEditor

from opps.wiki.models import Wiki


class Page(Wiki):
    PUBLIC_FIELDS = ('title', 'content', 'parent', 'tags')
    PUBLIC_FIELDS_WIDGETS = {'content': OppsEditor()}
    content = models.TextField(_(u'content'), )
