import codecs
import os
import re

from django.template import TemplateDoesNotExist

import cio
import cio.conf
from .encoding import smart_unicode


NODE_PATTERN = re.compile(r"\{%\s*node '(?P<uri>[^']+)'(\s+default='(?P<default>[^']+)')?\s*%\}")
BLOCKNODE_PATTERN = re.compile(r"\{%\s*blocknode '(?P<uri>[^']+)'.*%\}\s*(?P<default>.+)\s*\{% endblocknode %\}")


def get_template_dirs():
    """
    Scan all template loaders and retrieve template source directories.

    :return list:
    """
    template_dirs = []

    try:
        # Django 1.8+ has multiple template engines, we only test Django's for now.
        from django.template.loader import engines

        for engine in engines.all():
            template_dirs.extend(engine.template_dirs)

    except ImportError:
        from django.template.loader import template_source_loaders, find_template

        try:
            find_template('')  # Ensure template_source_loaders is populated
        except TemplateDoesNotExist:
            pass

        for loader in template_source_loaders:
            get_template_sources = getattr(loader, 'get_template_sources', None)
            if get_template_sources:
                loader_dirs = get_template_sources('')
                template_dirs.extend(loader_dirs)

    return template_dirs


def find_nodes():
    """
    Find node URI's and default content in templates.

    :return dict: {uri: content, ...}
    """
    nodes = {}
    template_dirs = get_template_dirs()

    for directory in template_dirs:
        for root, _, files in os.walk(directory):
            for filename in files:
                path = os.path.join(root, filename)

                with codecs.open(path, encoding='utf-8') as f:
                    source = f.read()

                    simple_nodes = search_nodes(NODE_PATTERN, source)
                    block_nodes = search_nodes(BLOCKNODE_PATTERN, source)

                    nodes.update(simple_nodes)
                    nodes.update(block_nodes)

    return nodes


def search_nodes(pattern, source):
    """
    :param pattern: Compiled regex pattern
    :param str source:
    :return dict:
    """
    nodes = {}

    for match in pattern.finditer(source):
        match = match.groupdict()
        node = cio.get(match['uri'], default=match['default'], lazy=True)
        node._flushed = True  # Prevent from being sent through pipeline
        uri = node.uri.clone(ext=node.uri.ext or cio.conf.settings.URI_DEFAULT_EXT)
        if uri not in nodes:
            nodes[uri] = smart_unicode(node.initial) if node.initial is not None else None

    return nodes
