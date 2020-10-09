****************************
Mopidy-Kitchen
****************************

.. image:: https://img.shields.io/pypi/v/Mopidy-Kitchen
    :target: https://pypi.org/project/Mopidy-Kitchen/
    :alt: Latest PyPI version

.. image:: https://img.shields.io/circleci/build/gh/ralfstx/mopidy-kitchen
    :target: https://circleci.com/gh/ralfstx/mopidy-kitchen
    :alt: CircleCI build status

.. image:: https://img.shields.io/codecov/c/gh/ralfstx/mopidy-kitchen
    :target: https://codecov.io/gh/ralfstx/mopidy-kitchen
    :alt: Test coverage

Mopidy extension for my Kitchen radio.
Discoveres albums in the local filesystem based on index files.
Each album should be a directory that includes an ``index.json`` file that lists the contents and
metadata of this album.

Index files should look like this example:

.. code-block:: json

    {
        "name": "John Doe - Another Dreadful Day",
        "artist": "John Doe",
        "title": "Another Dreadful Day",
        "discs": [{
            "path": "01",
            "tracks": [{
                "path": "01.ogg",
                "title": "Another Dreadful Morning",
                "length": 101
            }]
        }, {
            "path": "02",
            "tracks": [{
                "path": "01.ogg",
                "title": "Another Dreadful Afternoon",
                "length": 202
            }, {
                "path": "02.ogg",
                "title": "Another Dreadful Evening",
                "length": 303
            }]
        }]
    }


Installation
============

Not yet published. Build the extension by running::

    python setup.py sdist

Install by running::

    python3 -m pip install dist/Mopidy-Kitchen-0.1.0.tar.gz

See https://mopidy.com/ext/kitchen/ for alternative installation methods.


Configuration
=============

Before starting Mopidy, you must add configuration for
Mopidy-Kitchen to your Mopidy configuration file::

    [kitchen]
    media_dir = /path/to/your/music/archive


Project resources
=================

- `Source code <https://github.com/ralfstx/mopidy-kitchen>`_
- `Issue tracker <https://github.com/ralfstx/mopidy-kitchen/issues>`_
- `Changelog <https://github.com/ralfstx/mopidy-kitchen/blob/master/CHANGELOG.rst>`_


Credits
=======

- Original author: `Ralf Sternberg <https://github.com/ralfstx>`__
- Current maintainer: `Ralf Sternberg <https://github.com/ralfstx>`__
- `Contributors <https://github.com/ralfstx/mopidy-kitchen/graphs/contributors>`_
