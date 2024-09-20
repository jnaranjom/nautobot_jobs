""" STATUS HELPER """

from nautobot.extras.models import Status
from django.core.exceptions import ValidationError

class AbortTransaction(Exception):
    """Custom exception for aborting transactions"""
    pass


def find_status_uuid(status_name):
    """Function to return Status UUID to update objects

    Args:
        status_name (str): Status name

    Returns:
        status_id: UUID for the Status
    """
    try:
        status = Status.objects.get(name=status_name)
        status_id = status.id

    except ValidationError as err:
        raise AbortTransaction(f"Failed to retrieve {status_name} id.")

    return status_id
