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
    isp_router = ObjectVar(model=Device, query_params={"tenant": "ISP"})

    class Meta:
        """Jobs Metadata"""

    name = "Deploy small branch"
    description = "Job to deploy a new branch in Nautobot"
    dryrun_default = True

    def run(self, branch_location, isp_router):
        """Main function"""

        branch_devices = Device.objects.filter(location=branch_location)

        router_role = Role.objects.get(name="branch:edge:router")

        switch_role = Role.objects.get(name="branch:access:switch")

        planned_status = find_status_uuid("Planned")
        active_status = find_status_uuid("Active")

        for device in branch_devices:
            self.logger.info(
                f"Finding device type and available interfaces for: {device.name}."
            )
            if device.role == router_role:
                edge_router = device

                try:
                    router_interface = device.interfaces.filter(status=planned_status)[
                        0
                    ]
                    router_isp_interface = device.interfaces.filter(
                        status=planned_status
                    )[-1]
                except Exception as err:
                    self.logger.info(
                        f"Unable to find available interfaces (Planned Status) in {device.name}."
                    )
                    raise

            elif device.role == switch_role:
                access_switch = device
                try:
                    switch_interface = device.interfaces.filter(status=planned_status)[
                        0
                    ]
                    switch_access_interfaces = device.interfaces.filter(
                        status=planned_status
                    )[-3:]

                except Exception as err:
                    self.logger.info(
                        f"Unable to find available interfaces (Planned Status) in {device.name}."
                    )
                    raise

            else:
                self.logger.info(f"Unable to find device type for {device.name}.")

        self.logger.info(
            f"Connect: {edge_router.name} interface: {router_interface} <---> {access_switch.name} interface: {switch_interface}"
        )

        # Connect branch devices
        connect_cable_endpoints(router_interface.id, switch_interface.id)

        for update_interface in [router_interface, switch_interface]:
            update_interface.status = active_status
            update_interface.description = (
                f"{update_interface.device}::{update_interface.name}"
            )
            update_interface.validated_save()

        # Connect branch to ISP
        self.logger.info(
            f"Will connect the Edge Router with this ISP router: {ips_router.name}."
        )


register_jobs(DeployBranchSmall)
