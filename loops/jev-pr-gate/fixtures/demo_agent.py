#!/usr/bin/env python3
"""Deterministic teaching agent; emits a fixed patch, never edits the repository."""
import sys

if not sys.stdin.buffer.read().strip():
    sys.exit(2)

sys.stdout.write('''diff --git a/hello.py b/hello.py
--- a/hello.py
+++ b/hello.py
@@ -1 +1 @@
-print("hello")
+print("hello, world")
''')
