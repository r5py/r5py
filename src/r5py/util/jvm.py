#!/usr/bin/env python3

"""Set up a JVM and import basic java classes."""

import os

import jpype
import jpype.imports

from .classpath import R5_CLASSPATH
from . import config
from .memory_footprint import MAX_JVM_MEMORY


__all__ = []


jpype.startJVM(
    f"-Xmx{MAX_JVM_MEMORY:d}M",
    "-Xcheck:jni",
    # "--illegal-access=permit",
    # "--add-opens=java.lang/java.nio.DirectByteBuffer=ALL-UNNAMED",
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
