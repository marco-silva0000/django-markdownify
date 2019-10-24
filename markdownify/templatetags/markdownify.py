from functools import partial

from django import template
from django.conf import settings
from django.utils.safestring import mark_safe

import markdown
import bleach


register = template.Library()


def custom_markdownify(whitelist_tags, whitelist_attrs, whitelist_styles, whitelist_protocols):

    # Markdown settings
    strip = getattr(settings, 'MARKDOWNIFY_STRIP', True)
    extensions = getattr(settings, 'MARKDOWNIFY_MARKDOWN_EXTENSIONS', [])

    # Bleach Linkify
    linkify = None
    linkify_text = getattr(settings, 'MARKDOWNIFY_LINKIFY_TEXT', True)

    if linkify_text:
        linkify_parse_email = getattr(settings, 'MARKDOWNIFY_LINKIFY_PARSE_EMAIL', False)
        linkify_callbacks = getattr(settings, 'MARKDOWNIFY_LINKIFY_CALLBACKS', None)
        linkify_skip_tags = getattr(settings, 'MARKDOWNIFY_LINKIFY_SKIP_TAGS', None)
        linkifyfilter = bleach.linkifier.LinkifyFilter

        linkify = [partial(linkifyfilter,
                           callbacks=linkify_callbacks,
                           skip_tags=linkify_skip_tags,
                           parse_email=linkify_parse_email
                           )]


    def markdownify(text):
        # Convert markdown to html
        html = markdown.markdown(text, extensions=extensions)

        # Sanitize html if wanted
        if getattr(settings, 'MARKDOWNIFY_BLEACH', True):

            cleaner = bleach.Cleaner(tags=whitelist_tags,
                                     attributes=whitelist_attrs,
                                     styles=whitelist_styles,
                                     protocols=whitelist_protocols,
                                     strip=strip,
                                     filters=linkify,
                                     )

            html = cleaner.clean(html)

        return mark_safe(html)
    return markdownify

def custom_markdownify_maker(tags_to_exclude=[], attrs_to_exclude=[], styles_to_exclude=[], protocols_to_exclude=[]):
    whitelist_tags = getattr(settings, 'MARKDOWNIFY_WHITELIST_TAGS', bleach.sanitizer.ALLOWED_TAGS)
    tags = list(set(whitelist_tags) - set(tags_to_exclude))

    whitelist_attrs = getattr(settings, 'MARKDOWNIFY_WHITELIST_ATTRS', bleach.sanitizer.ALLOWED_ATTRIBUTES)
    attrs = list(set(whitelist_attrs) - set(attrs_to_exclude))

    whitelist_styles = getattr(settings, 'MARKDOWNIFY_WHITELIST_STYLES', bleach.sanitizer.ALLOWED_STYLES)
    styles = list(set(whitelist_styles) - set(styles_to_exclude))

    whitelist_protocols = getattr(settings, 'MARKDOWNIFY_WHITELIST_PROTOCOLS', bleach.sanitizer.ALLOWED_PROTOCOLS)
    protocols = list(set(whitelist_protocols) - set(protocols_to_exclude))


    return custom_markdownify(tags, attrs, styles, protocols)


register.filter("markdownify", custom_markdownify_maker())
