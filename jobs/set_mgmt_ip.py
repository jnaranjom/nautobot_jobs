""" SET MANAGEMENT IP IN INTERFACE """

from nautobot.apps.jobs import Job, ObjectVar, MultiObjectVar, register_jobs
from nautobot.dcim.models.locations import Location, LocationType
from nautobot.ipam.models import IPAddress, Prefix, Namespace
from nautobot.dcim.models import Device, Interface, Cable
from django.contrib.contenttypes.models import ContentType
from nautobot.extras.models import Status, Role


class SetManagementIP(Job):
    """Set Mgmt IP on device interface

    Args:
        Job (_type_): _description_
    """

    location = ObjectVar(model=Location)

    mgmt_switch = ObjectVar(model=Device, query_params={"role": "management:switch"})

    devices = MultiObjectVar(model=Device, query_params={"location": "$location"})

    class Meta:
        """Jobs Metadata"""

    name = "Set MGMT IP"
    description = "Job to set the IP address on the Management interface of the devices"
    dryrun_default = True

    def run(self, location, mgmt_switch, devices):
        """_summary_

        Args:
            location (_type_): _description_
        """

        planned_status = Status.objects.get(name="Planned")

        mgmt_interfaces = mgmt_switch.interfaces.filter(status=planned_status)

        mgmt_prefix = Prefix.objects.get(role__name="network:management")

        mgmt_ip_status = Status.objects.get(name="Reserved")

        mgmt_cable_status = Status.objects.get(name="Connected")

        termination_type = ContentType.objects.get(app_label="dcim", model="interface")

        # TODO: FAIL IN NUM OF DEVICES IS GREATER THAN AVAILABLE MGMT INT
        for idx, device in enumerate(devices):

            device_mgmt_int = device.interfaces.get(mgmt_only=True)

            if device_mgmt_int.ip_addresses.first():
                self.logger.info(
                    f"Interface {device_mgmt_int.name} has an IP assigned already"
                )
            else:
                ipaddress = mgmt_prefix.get_first_available_ip()
                mgmt_ip = IPAddress(
                    address=ipaddress,
                    namespace=mgmt_prefix.namespace,
                    type="host",
                    status=mgmt_ip_status,
                )

                mgmt_ip.validated_save()

                device_mgmt_int.ip_addresses.add(mgmt_ip)
                device_mgmt_int.description = (
                    mgmt_switch.name + " " + mgmt_interfaces[idx].name
                )

                device_mgmt_int.validated_save()

            if device_mgmt_int.connected_endpoint:
                self.logger.info(
                    f"Interface {device_mgmt_int.name} has an active connection"
                )
            else:
                mgmt_cable, _ = Cable.objects.get_or_create(
                    termination_a_type=termination_type,
                    termination_a_id=device_mgmt_int.id,
                    termination_b_type=termination_type,
                    termination_b_id=mgmt_interfaces[idx].id,
                    status=mgmt_cable_status,
                )

                mgmt_cable.validated_save()


register_jobs(SetManagementIP)
