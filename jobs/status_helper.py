""" STATUS HELPER """

from nautobot.extras.models import Status
from django.core.exceptions import ValidationError


def find_status_uuid(status_name):
    """Function to return Status UUID to update objects

    Args:
        status_name (str): Status name

    Returns:
        status_id: UUID for the Status
    """
    try:
        status_id = Status.objects.get(name=status_name)

    except ValidationError as err:
        raise AbortTransacion(f"Failed to retrieve {status_name} id.")

    return status_id
