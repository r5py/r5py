#!/usr/bin/env python3


"""Extends pytest.warns() to support platform-specific warnings."""


import platform
import pprint
import re

import pytest


__all__ = []


# see https://docs.python.org/3/library/platform.html#platform.system
# and https://github.com/python/cpython/blob/3.11/Lib/platform.py
ALL_PLATFORMS = [
    "",
    "Darwin",
    "Java",
    "Linux",
    "Windows",
]
LOCAL_PLATFORM = platform.system()


class PlatformSpecificWarningsChecker(pytest.WarningsRecorder):
    def __init__(
        self,
        expected_warning=Warning,
        match_expr=None,
        platforms=ALL_PLATFORMS,
        _ispytest=False,
    ):
        """
        Catch expected warnings, depending on platform.

        This acts similar to pytest’s `WarningsChecker`, but accepts an
        additional argument that filters by platform.

        See also: https://docs.pytest.org/en/stable/reference/reference.html#pytest.warns

        Arguments
        =========
        expected_warning : Warning | tuple[Warning]
            Warning type to expect (default: Warning)
        match_expr : str
            Regular expression that the warning’s message must match
        platforms : list[str]
            Expect this warning on these platforms. Evaluated against
            `platform.system()`.
            Default: `["Darwin", "Java", "Linux", "Windows", ""]`
        """
        super().__init__(_ispytest=_ispytest)

        MSG = "exceptions must be derived from Warning, not {:s}"

        if LOCAL_PLATFORM not in platforms:
            expected_warning = None
        elif isinstance(expected_warning, tuple):
            for exc in expected_warning:
                if not issubclass(exc, Warning):
                    raise TypeError(MSG.format(type(exc)))
        elif issubclass(expected_warning, Warning):
            expected_warning = (expected_warning,)
        else:
            raise TypeError(MSG.format(type(expected_warning)))

        self.expected_warning = expected_warning
        self.match_expr = match_expr

    def __exit__(self, exception_type, exception_value, traceback):
        super().__exit__(exception_type, exception_value, traceback)

        __tracebackhide__ = True

        def found_str():
            return pprint.pformat([record.message for record in self], indent=2)

        # only check if we're not currently handling an exception
        if exception_type is None and exception_value is None and traceback is None:
            if self.expected_warning is not None:
                if not any(issubclass(r.category, self.expected_warning) for r in self):
                    __tracebackhide__ = True
                    pytest.fail(
                        f"DID NOT WARN. No warnings of type {self.expected_warning} were emitted.\n"
                        f"The list of emitted warnings is: {found_str()}."
                    )
                elif self.match_expr is not None:
                    for r in self:
                        if issubclass(r.category, self.expected_warning):
                            if re.compile(self.match_expr).search(str(r.message)):
                                break
                    else:
                        pytest.fail(
                            f"DID NOT WARN. "
                            f"No warnings of type {self.expected_warning} matching "
                            f"the regex were emitted. \n"
                            f"Regex: {self.match_expr} \n"
                            f"Emitted warnings: {found_str()}"
                        )


def _warns(
    expected_warning,
    *args,
    match=None,
    platforms=ALL_PLATFORMS,
    **kwargs,
):
    """
    Assert that code raises a particular class of warning.

    See https://docs.pytest.org/en/stable/_modules/_pytest/recwarn.html#warns
    for a detailed description. This implementation adds an argument `platforms`
    that can be used to filter on which platforms to expect the warning.

    Arguments
    =========
    expected_warning : Warning | tuple[Warning]
        Warning type to expect (default: Warning)
    match : str
        Regular expression that the warning’s message must match (default: None)
    platforms : list[str]
        Expect this warning on these platforms. Evaluated against
        `platform.system()`.
        Default: `["Darwin", "Java", "Linux", "Windows", ""]`

    """
    __tracebackhide__ = True
    if not args:
        if kwargs:
            argnames = ", ".join(sorted(kwargs))
            raise TypeError(
                f"Unexpected keyword arguments passed to pytest.warns: {argnames}"
                "\nUse context-manager form instead?"
            )
        return PlatformSpecificWarningsChecker(
            expected_warning,
            match_expr=match,
            _ispytest=True,
            platforms=platforms,
        )
    else:
        func = args[0]
        if not callable(func):
            raise TypeError(f"{func!r} object (type: {type(func)}) must be callable")
        with PlatformSpecificWarningsChecker(
            expected_warning,
            _ispytest=True,
            platforms=platforms,
        ):
            return func(*args[1:], **kwargs)


_pytest_warns = pytest.warns
pytest.warns = _warns
