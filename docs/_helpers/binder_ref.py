#!/usr/bin/env python

"""Find a Git reference (branch/commit) to open in Binder."""

# if we are building a stable version,
# point the binder link to branch `stable`,
# otherwise, point to branch `main`


import git
import os


__all__ = ["BINDER_REF"]


def get_binder_ref():
    try:
        READTHEDOCS_VERSION = os.environ["READTHEDOCS_VERSION"]
    except KeyError:  # not running on RTD
        READTHEDOCS_VERSION = ""

    if READTHEDOCS_VERSION == "stable":
        binder_ref = "stable"  # stable is synced with last version tag/release
    elif READTHEDOCS_VERSION == "latest":
        binder_ref = "main"
    else:
        repository = git.Repo(search_parent_directories=True)
        binder_ref = repository.git.rev_parse(repository.head.commit.hexsha, short=True)
    return binder_ref


BINDER_REF = get_binder_ref()
