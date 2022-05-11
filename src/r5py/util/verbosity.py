#!/usr/bin/env python3

"""Import the relevant Java classes to access R5."""

import os

from . import config, jvm  # noqa: F401

import ch.qos.logback.classic
import java.io
import java.lang
import org.slf4j.LoggerFactory


__all__ = []


config.argparser.add(
    "-v", "--verbose", help="Enable verbose output from R5." "", action="store_true"
)
arguments = config.arguments()

if not arguments.verbose:
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
