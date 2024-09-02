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

        for device in branch_devices:
            if device.role == router_role:
                edge_router = device
                print(device.name, device.role)

            elif device.role == switch_role:
                access_switch = device
                print(device.name, device.role)

            else:
                self.logger.info(
                    f"Unable to find device type for {device.name}. Update the device type before running this job again"
                )


register_jobs(DeployBranchSmall)
