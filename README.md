opps-wiki
=========

The following variable must be setted in your settings file

```python
OPPS_WIKI_EMAILS = [your@email.coml, ]

# It's a tuple/list with the emails that will receive the notifications when
# a suggestion or a report is created.
```

The following variables should be setted on your settings file if you want to
choose when the user can publish automatically and when the wiki should be
unpublished
```python
USER_CAN_PUBLISH_NUMBER = 100   # (Default)
# It's the minimum number of previous accepted suggestions that allow the
# user to start publishing without waiting for approval.

UNPUBLISH_REPORTS_NUMBER = 100   # (Default)
# It is the number of reports needed to unpublish a wiki.
```

Without 'opps-wiki' and 'reversion' in your INSTALLED_APPS this app won't work.
Add them like below:
```python
'opps.wiki',
'reversion',
```

The reversion is used to control the wiki's versions. Then you have a log
with older and newer versions of the wiki so you can choose which one you want.


If you want to activate the apps 'musicians' and 'pages' that are in the
contrib folder, just add them to your INSTALLED_APPS like below:
```python
'opps.wiki',
'opps.wiki.contrib.pages',
'opps.wiki.contrib.musicians',
```
Include wiki's urls on the urls.py before the opps urls, like this:
```python
url('^wiki/', include('opps.wiki.urls')),
url(r'^', include('opps.urls')),
```
