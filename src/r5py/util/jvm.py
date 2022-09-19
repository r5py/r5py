#!/usr/bin/env python3

"""Set up a JVM and import basic java classes."""

import os
import sys

import jpype
import jpype.imports

from .classpath import R5_CLASSPATH
from . import config
from .memory_footprint import MAX_JVM_MEMORY


__all__ = ["start_jvm"]


def start_jvm():
    """
    Start a Java Virtual Machine (JVM) if none is running already.

    Takes into account the `--max-memory` and `--verbose` command
    line and configuration options.
    """
    if not jpype.isJVMStarted():
        jpype.startJVM(
            f"-Xmx{MAX_JVM_MEMORY:d}",
            "-Xcheck:jni",
            classpath=[R5_CLASSPATH],
        )

        if not config.arguments().verbose:
            import ch.qos.logback.classic
            import java.io
            import java.lang
            import org.slf4j.LoggerFactory

            logger_context = org.slf4j.LoggerFactory.getILoggerFactory()
            for log_target in (
                "com.conveyal.gtfs",
                "com.conveyal.osmlib",
                "com.conveyal.r5",
                "com.conveyal.r5.profile.ExecutionTimer",
                "com.conveyal.r5.profile.FastRaptorWorker",
                "graphql.GraphQL",
                "org.eclipse.jetty",
                "org.hsqldb.persist.Logger" "org.mongodb.driver.connection",
            ):
                logger_context.getLogger(log_target).setLevel(
                    ch.qos.logback.classic.Level.valueOf("OFF")
                )

            if os.name == "nt":  # Windows
                null_stream = java.io.PrintStream("NUL")
            else:
                null_stream = java.io.PrintStream("/dev/null")
            java.lang.System.setErr(null_stream)
            java.lang.System.setOut(null_stream)


# The JVM should be started before we attempt to import any Java package.
# If we run `start_jvm()` before another `import` statement, linting our
# code would result in many E402 (‘Module level import not at top of file’)
# warnings, if the JVM would start implicitely when `__file__` is imported,
# we would end up with F401 (‘Module imported but unused’) warnings.

# This below is a middle way: We don’t start the JVM right away, only
# when `start_jvm()` is called. However, if we attempt to import a
# Java package (or, more precisely, a package that’s likely to be a
# Java package), the `import` statement would trigger `start_jvm()`

# see:
# https://github.com/jpype-project/jpype/blob/master/jpype/imports.py#L146


class _JImportLoaderThatStartsTheJvm(jpype.imports._JImportLoader):
    """Find Java packages for import statements, start JVM before that."""

    def find_spec(self, name, path, target=None):
        # we got this far in `sys.meta_path` (no other finder/loader
        # knew about the package we try to load), and naturally, we’re
        # towards the end of that list.

        # Let’s assume the requested packages is a Java package,
        # and start the JVM
        start_jvm()

        # then go the standard jpype way:
        return super().find_spec(name, path, target)


# replace jpype’s _JImportLoader with our own:
for i, finder in enumerate(sys.meta_path):
    if isinstance(finder, jpype.imports._JImportLoader):
        sys.meta_path[i] = _JImportLoaderThatStartsTheJvm()
