""" SET MANAGEMENT IP IN INTERFACE """

from nautobot.apps.jobs import Job, ObjectVar, MultiObjectVar, register_jobs
from nautobot.dcim.models.locations import Location, LocationType
from nautobot.ipam.models import IPAddress, Namespace
from nautobot.dcim.models import Device, Interface
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


        #TODO: FAIL IN NUM OF DEVICES IS GREATER THAN AVAILABLE MGMT INT
        for idx, device in enumerate(devices):
            device_mgmt_int = device.interfaces.get(mgmt_only=True)

            print(device.name, device_mgmt_int.name, mgmt_switch.name, mgmt_interfaces[idx].name)

            ipaddress = mgmt_prefix.get_first_available_ip()

            mgmt_ip = IPAddress(address=ipaddress,namespace=mgmt_prefix.namespace,type="host",status=mgmt_ip_status)

            mgmt_ip.validated_save()

            device_mgmt_int.ip_addresses.add(mgmt_ip)

            device_mgmt_int.description = mgmt_switch.name + mgmt_interfaces[idx].name

            device_mgmt_int.validated_save()


        # for myinterface in myinterfaces:
        #     if myinterface.device in devices:

        #         myipaddresses = IPAddress.objects.filter(
        #             role__name="network:management", status__name="Reserved"
        #         )

        #         myipaddress = myipaddresses[0]
        #         myipaddress.status = Status.objects.get(name="Active")
        #         myipaddress.validated_save()

        #         myinterface.ip_addresses.add(myipaddress)
        #         myinterface.description = "MGMT"
        #         myinterface.validated_save()


register_jobs(SetManagementIP)
