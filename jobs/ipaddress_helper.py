""" IP ADDRESS HELPER """

from nautobot.ipam.models import IPAddress
from .status_helper import find_status_uuid
from django.core.exceptions import ValidationError


def create_ipaddr(prefix):
    """ Function to create IP Address within a given Prefix

    Args:
        prefix (str): Prefix to carve out IP address
    Returns:
       ipaddress(dict): New IP address object
    """
    try:
        reserved_status = find_status_uuid("Reserved")
        ipaddress = prefix.get_first_available_ip()

        ip_address = IPAddress(
            address=ipaddress,
            namespace=prefix.namespace,
            type="host",
            status=reserved_status,
        )

        ip_address.validated_save()

        return ip_address

    except ValidationError as err:
        raise AbortTransacion(f"Failed to create IP")
