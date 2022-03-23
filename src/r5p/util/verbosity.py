#!/usr/bin/env python3

"""Import the relevant Java classes to access R5."""

from . import config, jvm  # noqa: F401

import ch.qos.logback.classic
import org.slf4j.LoggerFactory


__all__ = []


config.argparser.add(
    "-v",
    "--verbose",
    help="Enable verbose output from R5.""",
    action="store_true"
)
arguments = config.arguments()

if not arguments.verbose:
    logger_context = org.slf4j.LoggerFactory.getILoggerFactory()
    for log_target in (
            "com.conveyal.r5",
            "com.conveyal.osmlib",
            "com.conveyal.gtfs",
            "com.conveyal.r5.profile.ExecutionTimer",
            "graphql.GraphQL",
            "org.mongodb.driver.connection",
            "org.eclipse.jetty",
            "org.eclipse.jetty",
            "com.conveyal.r5.profile.FastRaptorWorker",
    ):
        logger_context.getLogger(log_target).setLevel(
            ch.qos.logback.classic.Level.valueOf("OFF")
        )
