""" SET MANAGEMENT ON DEVICES """

from nautobot.apps.jobs import Job, ObjectVar, MultiObjectVar, register_jobs
from nautobot.dcim.models.locations import Location
from nautobot.dcim.models import Device, Cable
from nautobot.ipam.models import IPAddress, Prefix

# from django.contrib.contenttypes.models import ContentType
from nautobot.extras.models import Status
from .cable_helper import connect_cable_endpoints


class SetManagementIP(Job):
    """Set Mgmt on Devices"""

    location = ObjectVar(model=Location)

    mgmt_switch = ObjectVar(model=Device, query_params={"role": "management:switch"})

    devices = MultiObjectVar(model=Device, query_params={"location": "$location"})

    class Meta:
        """Jobs Metadata"""

    name = "Set MGMT IP"
    description = "Job to set the Management on the devices"
    dryrun_default = True

    def run(self, location, mgmt_switch, devices):
        """Main function"""

        planned_status = Status.objects.get(name="Planned")
        active_status = Status.objects.get(name="Active")
        ipaddr_status = Status.objects.get(name="Reserved")
        # cable_status = Status.objects.get(name="Connected")

        mgmt_interfaces = mgmt_switch.interfaces.filter(status=planned_status)
        mgmt_prefix = Prefix.objects.get(role__name="network:management")
        # termination_type = ContentType.objects.get(app_label="dcim", model="interface")

        if len(mgmt_interfaces) >= len(devices):
            for idx, device in enumerate(devices):

                device_mgmt_int = device.interfaces.get(mgmt_only=True)

                if device_mgmt_int.ip_addresses.first():
                    self.logger.info(
                        f"Device: {device.name}, Interface: {device_mgmt_int.name} has an IP assigned already"
                    )

                else:
                    ipaddress = mgmt_prefix.get_first_available_ip()

                    mgmt_ip = IPAddress(
                        address=ipaddress,
                        namespace=mgmt_prefix.namespace,
                        type="host",
                        status=ipaddr_status,
                    )

                    mgmt_ip.validated_save()

                    device_mgmt_int.ip_addresses.add(mgmt_ip)
                    device_mgmt_int.description = (
                        f"{mgmt_switch.name}::{mgmt_interfaces[idx].name}"
                    )

                    device_mgmt_int.validated_save()

                    device.primary_ip4 = mgmt_ip
                    device.validated_save()

                if device_mgmt_int.connected_endpoint:
                    self.logger.info(
                        f"Device: {device.name}, Interface: {device_mgmt_int.name} has an active connection"
                    )
                else:
                    connect_cable_endpoints(device_mgmt_int.id, mgmt_interfaces[idx].id)
                    # mgmt_cable, _ = Cable.objects.get_or_create(
                    #     termination_a_type=termination_type,
                    #     termination_a_id=device_mgmt_int.id,
                    #     termination_b_type=termination_type,
                    #     termination_b_id=mgmt_interfaces[idx].id,
                    #     status=cable_status,
                    # )

                    # mgmt_cable.validated_save()

                    mgmt_interfaces[idx].status = active_status
                    mgmt_interfaces[idx].description = (
                        f"{device.name}::{device_mgmt_int.name}"
                    )
                    mgmt_interfaces[idx].validated_save()

        else:
            self.logger.info(
                f"Not enough interfaces available in {mgmt_switch}. Only {len(mgmt_interfaces)} available. {len(devices)} devices need MGMT configuration."
            )


register_jobs(SetManagementIP)
