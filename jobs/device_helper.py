""" IP ADDRESS HELPER """

from nautobot.dcim.models.locations import Location
from nautobot.dcim.models import Device, DeviceType
from nautobot.extras.models.roles import Role
from nautobot.tenancy.models import Tenant
from .status_helper import find_status_uuid
from django.core.exceptions import ValidationError


def create_device(
    self, dev_name, dev_serial, dev_role, dev_type, dev_location, dev_tenant
):
    """Function to create a new Device

    Args:

    Returns:

    """
    try:

        staging_status = find_status_uuid("Staged")
        device_role = Role.objects.get(name=dev_role)
        device_type = DeviceType.objects.get(model=dev_type)
        device_location = Location.objects.get(name=dev_location)
        device_tenant = Tenant.objects.get(name=dev_tenant)

        new_device = Device(
            device_type=device_type,
            location=device_location,
            name=dev_name,
            role=device_role,
            serial=dev_serial,
            status=staging_status,
            tenant=device_tenant,
        )
        new_device.validated_save()

        return new_device

    except ValidationError as err:
        raise AbortTransacion(f"Failed to create device {dev_name}: {err}")
