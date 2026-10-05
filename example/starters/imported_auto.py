"""Loaded by hive.autoconfigure.imports, not by package scan.

The same class can be registered as an entry point::

    [project.entry-points."hive.autoconfigure"]
    showcase.imported = "example.starters.imported_auto:ImportedAuto"

This repository does not register that entry point on the library distribution,
because an installed copy of fastapi-hive would then fail to import ``example``
in other applications. ``AUTOCONFIGURE_IMPORTS`` uses the same loader.
"""

from fastapi_hive.ioc_framework.decorators import autoconfigure, provides


@autoconfigure(name="showcase.imported", order=40)
class ImportedAuto:

    @provides("showcase.imported")
    def banner(self):
        return "imported-by-config"
