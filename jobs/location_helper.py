""" IP ADDRESS HELPER """

from nautobot.dcim.models.locations import Location, LocationType
from .status_helper import find_status_uuid
from django.core.exceptions import ValidationError


def create_location(location_name, location_type, location_tenant, location_parent):
    """Function to create a new Location

    Args:

    Returns:

    """
    try:
        staging_status = find_status_uuid("Staging")
        parent = Location.objects.get(name=location_parent)
        location_type = LocationType.objects.get(name=location_type)

        new_location = Location(
            location_type=location_type,
            name=location_name,
            status=staging_status,
            tenant=location_tenant,
            parent=location_parent,
        )

        new_location.validated_save()

        return new_location

    except ValidationError as err:
        raise AbortTransacion(f"Failed to create new Location")
