""" DEPLOY NEW SMALL BRANCH (1 Router/ 1 Switch)"""

from nautobot.apps.jobs import Job, ObjectVar, MultiObjectVar, register_jobs
from nautobot.dcim.models.locations import Location
from nautobot.extras.models.roles import Role
from nautobot.dcim.models import Device, Cable
from nautobot.ipam.models import IPAddress, Prefix
from nautobot.extras.models import Status
from .cable_helper import connect_cable_endpoints
from .status_helper import find_status_uuid
from .ipaddress_helper import create_ipaddr


class DeployBranchSmall(Job):
    """Job to deploy new small branch"""

    branch_location = ObjectVar(model=Location, query_params={"tenant": "Branch"})

    class Meta:
        """Jobs Metadata"""

    name = "Deploy small branch"
    description = "Job to deploy a new branch in Nautobot"
    dryrun_default = True

    def run(self, branch_location):
        """Main function"""

        branch_devices = Device.objects.filter(location=branch_location)

        router_role = Role.objects.get(name="branch:edge:router")

        switch_role = Role.objects.get(name="branch:access:switch")

        planned_status = find_status_uuid("Planned")

        for device in branch_devices:
            if device.role == router_role:
                edge_router = device
                router_interface = device.interfaces.filter(status=planned_status)[0]

            elif device.role == switch_role:
                access_switch = device
                switch_interface = device.interfaces.filter(status=planned_status)[0]

            else:
                self.logger.info(
                    f"Unable to find device type for {device.name}. Update the device type before running this job again"
                )

        active_status = find_status_uuid("Active")

        connect_cable_endpoints(router_interface.id, switch_interface.id)

        router_interface.status = active_status
        router_interface.description = f"{edge_router.name}::{router_interface.name}"
        router_interface.validated_save()

        switch_interface.status = active_status
        switch_interface.description = f"{access_switchr.name}::{switch_interface.name}"
        switch_interface.validated_save()


register_jobs(DeployBranchSmall)
