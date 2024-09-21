""" IP ADDRESS HELPER """

from nautobot.dcim.models.locations import Location
from nautobot.dcim.models import Device, DeviceType
from nautobot.extras.models.roles import Role
from nautobot.tenancy.models import Tenant
from .status_helper import find_status_uuid
from django.core.exceptions import ValidationError


def create_device(
    dev_name, dev_serial, dev_role, dev_type, dev_location, dev_tenant, dev_description
):
    """Function to create a new Device

    Args:

    Returns:

    """
    try:

        staging_status = find_status_uuid("Staged")
        device_role = Role.objects.get(name=dev_role)
        self.logger.info(f" HERE 1")
        device_type = DeviceType.objects.get(name=dev_type)
        self.logger.info(f" HERE 2")
        device_location = Location.objects.get(name=dev_location)
        self.logger.info(f" HERE 3")
        device_tenant = Tenant.objects.get(name=dev_tenant)
        self.logger.info(f" HERE 4")
        device_description = f"{dev_description}"

        new_device = Device(
            description=device_description,
            device_type=device_type,
            location=device_location,
            name=dev_name,
            role=device_role,
            serial=dev_serial,
            status=staging_status,
            tenant=device_tenant,
        )
        self.logger.info(f" OR HERE")
        new_device.validated_save()

        return new_device

    except ValidationError as err:
        raise AbortTransacion(f"Failed to create device {dev_name}: {err}")
