import pkg_resources

pkg_resources.declare_namespace(__name__)

VERSION = (0, 1, 0)

__version__ = ".".join(map(str, VERSION))
__status__ = "Development"
__description__ = u"Wiki system, App for Opps CMS"

__author__ = u"YACOWS"
__credits__ = []
__email__ = u"yacows@yacows.com.br"
__copyright__ = u"Copyright 2013, Opps Project"
