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
    role = ObjectVar(model=Role)
    mgmt_switch = ObjectVar(model=Device, query_params={"role": "$role"})
    devices = MultiObjectVar(model=Device, query_params={"location": "$location"})

    class Meta:
        """Jobs Metadata"""

    name = "Set MGMT IP"
    description = "Job to set the IP address on the Management interface of the devices"
    dryrun_default = True

    def run(self, location, role, mgmt_switch, devices):
        """_summary_

        Args:
            location (_type_): _description_
        """

        myinterfaces = Interface.objects.filter(mgmt_only=True)
        planned_status = Status.objects.get(name="Planned")
        # mgmt_interfaces = Interface.objects.filter(
        #     device=mgmt_switch, status=planned_status
        # )

        print(myinterfaces)
        print(planned_status)
        # print(mgmt_interfaces)

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
