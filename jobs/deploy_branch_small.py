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
        active_status = find_status_uuid("Active")

        for device in branch_devices:
            self.logger.info(
                f"Finding device {device.name} type and available interface"
            )
            if device.role == router_role:

                edge_router = device
                if len(device.interfaces.filter(status=planned_status)[0]) > 0:
                    router_interface = device.interfaces.filter(status=planned_status)[
                        0
                    ]
                else:
                    self.logger.info(
                        f"Unable to find available interfaces (Planned Status) in {device.name}."
                    )
                    break

            elif device.role == switch_role:
                access_switch = device
                if len(device.interfaces.filter(status=planned_status)[0]) > 0:
                    switch_interface = device.interfaces.filter(status=planned_status)[
                        0
                    ]
                else:
                    self.logger.info(
                        f"Unable to find available interfaces (Planned Status) in {device.name}."
                    )
                    break

            else:
                self.logger.info(
                    f"Unable to find device type for {device.name}. Update the device type before running this job again"
                )

        self.logger.info(
            f"Connect {edge_router.name} interface {router_interface} with {access_switch.name} interface {switch_interface}"
        )
        connect_cable_endpoints(router_interface.id, switch_interface.id)

        for update_interface in [router_interface, switch_interface]:
            update_interface.status = active_status
            update_interface.description = (
                f"{update_interface.device}::{update_interface.name}"
            )
            update_interface.validated_save()


register_jobs(DeployBranchSmall)
