# -*- coding: utf-8 -*-
# pylint: disable=protected-access
"""Test cases for :meth:`OpenSandboxBackend._make_write_entry`.

Regression tests for the write-entry ``mode`` encoding: the OpenSandbox
SDK and execd encode file permissions as the decimal integer whose
digits spell the octal mode (the SDK's own ``WriteEntry.mode`` default
is ``755``). Passing ``0o644`` instead puts decimal ``420`` on the wire,
which execd parses as the octal mode ``0o420``; the resulting wrong
permissions then fail with "permission denied" on the second write to
the same file.

These tests are pure unit tests: they exercise the entry construction
directly and never need a live OpenSandbox service, so unlike
``backend_opensandbox_test.py`` they run in every environment.
"""

import sys
import unittest
from unittest import mock

try:
    from opensandbox.models.filesystem import WriteEntry as _SdkWriteEntry

    _SDK_AVAILABLE = True
except ImportError:  # pragma: no cover
    _SdkWriteEntry = None  # type: ignore[assignment, misc]
    _SDK_AVAILABLE = False

from agentscope.workspace import OpenSandboxBackend
from agentscope.workspace._opensandbox._opensandbox_backend import _WriteEntry


class TestMakeWriteEntryMode(unittest.TestCase):
    """``_make_write_entry`` must spell the octal mode in decimal digits."""

    def test_entry_mode_is_decimal_644(self) -> None:
        entry = OpenSandboxBackend._make_write_entry("a.txt", b"data")

        self.assertEqual(entry.mode, 644)

    @unittest.skipUnless(_SDK_AVAILABLE, "opensandbox SDK is not installed")
    def test_sdk_entry_mode_is_decimal_644(self) -> None:
        entry = OpenSandboxBackend._make_write_entry("a.txt", b"data")

        self.assertIsInstance(entry, _SdkWriteEntry)
        self.assertEqual(entry.mode, 644)

    def test_fallback_entry_mode_is_decimal_644(self) -> None:
        # A ``None`` entry in ``sys.modules`` makes the in-function
        # import fail, forcing the SDK-less fallback branch.
        entry = None
        with mock.patch.dict(
            sys.modules,
            {"opensandbox.models.filesystem": None},
        ):
            entry = OpenSandboxBackend._make_write_entry("a.txt", b"data")

        self.assertIsInstance(entry, _WriteEntry)
        self.assertEqual(entry.mode, 644)


if __name__ == "__main__":
    unittest.main()
