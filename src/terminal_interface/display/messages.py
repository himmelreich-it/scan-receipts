"""Startup messages and static text display for terminal interface."""


def display_startup_message() -> None:
    """Display startup message about receipt processing operation.

    Shows informational message before processing begins.
    Message indicates processing is about to start and mentions input folder scanning.
    """
    print("Receipt Processing Script")
    print("Scanning input folder for receipt files...")
    print()
