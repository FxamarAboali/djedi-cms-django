.. _usage:

Usage
=====

Djedi CMS is more or less a highly configurable key/value store, built on top of the content pipeline library `content-io <content-io_>`_.

All managed content within djedi is represented by a ``Node``. Each node has a unique resource identifier called :ref:`uri`,
which holds necessary information to lookup, persist or render node content.

Nodes also relies on :ref:`plugins` handling the content serialization and rendering.
Plugins gets resolved by the `extension` part of the node uri.

**URI example**::

    i18n://en-us@page/home/body.md#draft

    [scheme] :// [namespace] @ [path] . [extension] # [version]


Examine the :ref:`uri` and :ref:`plugins` sections for deeper understanding and use cases.


Djedi in your templates
-----------------------

The most common way of using Djedi CMS is to make content editable and `i18n` compliant in your templates.

Load ``djedi_tags`` in a template and use the ``node`` or ``blocknode`` tags.

.. code-block:: django

    {% load djedi_tags %}
    <body>
        <h1>{% node 'page/home/title.txt' default='Djedi' %}</h1>

        {% node 'page/home/logo.img' %}

        {% blocknode 'page/home/body.md' %}
            ## I'm a djedi apprentice
            This is easy!
        {% endblocknode %}
    </body>


Node tag
~~~~~~~~

The ``node`` tag takes one argument, the :ref:`uri`, and two optional keyword arguments; `default` and `edit`.

- **default** (*empty unicode*)
    Content displayed for new nodes / not persisted in the storage backend.

- **edit** (*True*)
    Enable/disable inline editing. Useful if content is not visible, like a meta-tag or tag attribute, preventing user interaction.

.. code-block:: django

    <input placeholder="{% node 'foo/bar' default='Search' edit=False %}">


Blocknode tag
~~~~~~~~~~~~~

The ``blocknode`` tag is similar to the ``node`` tag except that it lacks the `default` keyword argument
and using the block body as default content instead. Beyond the `edit` kwarg, the ``blocknode`` can take any arbitrary
keyword argument for use as a content formatting context.

.. code-block:: django

    {% blocknode 'page/home/intro.md' user=user.first_name %}
        ## Welcome {{ name }}!
        I love using dynamic variables in my translatable texts.
    {% endblocknode %}



.. _content-io: https://github.com/5monkeys/content-io/


Djedi in your code
------------------

.. code-block:: python

    >>> import cio
    >>> node = cio.get('mail/receipt/subject', default=u'Thanks!')
    >>> node.uri
    <URI 'i18n://en-us@mail/receipt/subject.txt'>
    >>> node.content
    u'Thanks!'

    >>> node = cio.set('sv-se@mail/receipt/subject', u'Tack!', publish=False)
    >>> node.uri
    <URI 'i18n://sv-se@mail/receipt/subject.txt#draft'>
    >>> node.content
    u'Tack!'

    >>> node = cio.publish('sv-se@mail/receipt/subject.txt#draft')
    >>> node.uri
    <URI 'i18n://sv-se@mail/receipt/subject.txt#1'>
