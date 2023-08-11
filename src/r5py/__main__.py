#!/usr/bin/env python3


"""A Python wrapper for the R5 routing analysis engine."""


from .util import Config


def main():
    config = Config()
    arguments = config.get_arguments()  # noqa F401


if __name__ == "__main__":
    main()
