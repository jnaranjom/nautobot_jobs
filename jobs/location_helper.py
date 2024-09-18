""" IP ADDRESS HELPER """

from nautobot.dcim.models.locations import Location, LocationType
from .status_helper import find_status_uuid
from nautobot.tenancy.models import Tenant
from django.core.exceptions import ValidationError


def create_location(loc_name, loc_type, loc_tenant, loc_parent):
    """Function to create a new Location

    Args:

    Returns:

    """
    try:
        staging_status = find_status_uuid("Staging")
        location_parent = Location.objects.get(name=loc_parent)
        location_tenant = Tenant.objects.get(name=loc_tenant)
        location_type = LocationType.objects.get(name=loc_type)
        location_description = f"{loc_parent} {loc_type} {loc_name}"

        new_location = Location(
            location_type=location_type,
            name=loc_name,
            status=staging_status,
            tenant=location_tenant,
            parent=location_parent,
            description=location_description,
        )

        new_location.validated_save()

        return new_location

    except ValidationError as err:
        raise AbortTransacion(f"Failed to create new Location")
