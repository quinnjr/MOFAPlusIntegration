"""
MOFAPlusIntegrationPlugin — PluMA-convention entry point.

PluMA's Python plugin loader globs ``<path>/<Name>/<Name>Plugin.py`` and
looks for a class named ``<Name>Plugin`` with ``input(filename)`` /
``run()`` / ``output(filename)`` methods. This module provides that
wrapper around the core ``MOFAPlusIntegration`` class so the plugin can
be loaded by PluMA without modification.

Parameter file format: whitespace-delimited ``key value`` pairs.
See ``example/parameters.txt`` for keys.

Author: Joseph R. Quinn <quinn.josephr@protonmail.com>
License: MIT
"""

from __future__ import annotations

from MOFAPlusIntegration import MOFAPlusIntegration


class MOFAPlusIntegrationPlugin(MOFAPlusIntegration):
    """PluMA-convention wrapper around :class:`MOFAPlusIntegration`.

    Inherits all behavior from the core class. Its only purpose is to
    satisfy PluMA's filename/class-name convention so the plugin can be
    loaded by PluMA's Python plugin loader.
    """

    pass
