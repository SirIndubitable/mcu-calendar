"""
Generic helper methods that eny of the modules here might want to use
"""
from rich.progress import BarColumn, Progress, TimeElapsedColumn


def create_progress():
    """
    Factory method for a Rich Process object
    """
    return Progress(
        "[bold]{task.description}",
        BarColumn(),
        "[progress.percentage]{task.percentage:>3.0f}%",
        TimeElapsedColumn(),
    )


def truncate(string, length):
    """
    Truncates a string to a given length with "..." at the end if needed
    """
    return string[: (length - 3)].ljust(length, ".")
