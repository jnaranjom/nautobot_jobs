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
        # connect_cable_endpoints(router_interface.id, switch_interface.id)

        termination_type = ContentType.objects.get(app_label="dcim", model="interface")
        cable_status = Status.objects.get(name="Connected")

        connect_cable, _ = Cable.objects.get_or_create(
            termination_a_type=termination_type,
            termination_a_id=router_interface.id,
            termination_b_type=termination_type,
            termination_b_id=switch_interface.id,
            status=cable_status,
        )

        connect_cable.validated_save()

        router_interface.status = active_status
        router_interface.description = (
            f"{switch_interface.device}::{switch_interface.name}"
        )
        router_interface.validated_save()

        switch_interface.status = active_status
        switch_interface.description = (
            f"{router_interface.device}::{router_interface.name}"
        )
        switch_interface.validated_save()

        # Connect branch to ISP
        self.logger.info(
            f"Will connect the Edge Router with this ISP router: {isp_router.name}."
        )


register_jobs(DeployBranchSmall)
