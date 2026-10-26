#!/usr/bin/env python3
"""Development and migration entry point, not an issuance service."""
import os
import sys

if __name__ == "__main__":
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "tdoc_runtime.settings")
    from django.core.management import execute_from_command_line
    execute_from_command_line(sys.argv)
