""" SET MANAGEMENT IP IN INTERFACE """

from nautobot.apps.jobs import Job, ObjectVar, MultiObjectVar, register_jobs
from nautobot.dcim.models.locations import Location, LocationType
from nautobot.ipam.models import IPAddress
from nautobot.dcim.models import Device, Interface
from nautobot.extras.models import Status, Role


class SetManagementIP(Job):
    """Set Mgmt IP on device interface

    Args:
        Job (_type_): _description_
    """

    location = ObjectVar(model=Location)
    devices = MultiObjectVar(model=Device, query_params={"location": "$location"})

    class Meta:
        """Jobs Metadata"""

    name = "Set MGMT IP"
    description = "Job to set the IP address on the Management interface of the devices"
    dryrun_default = True

    def run(self, location, devices):
        """_summary_

        Args:
            location (_type_): _description_
        """
        myinterfaces = Interface.objects.filter(mgmt_only=True)

        myipaddresses = IPAddress.objects.filter(
            role__name="network:management", status__name="Reserved"
        )

        i = 0
        for myinterface in myinterfaces:
            if myinterface.device in devices:
                myinterface.ip_addresses.add(myipaddresses[i])
                myinterface.description = myipaddresses[i].address
                myinterface.validated_save()
                i += 1

register_jobs(SetManagementIP)
