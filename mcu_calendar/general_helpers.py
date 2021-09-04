"""
Generic helper methods that eny of the modules here might want to use
"""
from rich.progress import Progress, BarColumn, TimeElapsedColumn


def create_progress():
    """
    Factory method for a Rich Process object
    """
    return Progress(
        "[bold]{task.description}",
        BarColumn(),
        "[progress.percentage]{task.percentage:>3.0f}%",
        TimeElapsedColumn())


def find(seq, predicate):
    """
    Finds the first element in seq that predicate return true for
    """
    for item in seq:
        if predicate(item):
            return item
    return None
