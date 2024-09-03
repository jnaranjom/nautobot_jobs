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
from django.contrib.contenttypes.models import ContentType
from nautobot.dcim.models.device_components import Interface


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
                    router_interface = device.interfaces.filter(
                        status=planned_status
                    ).first()
                    router_isp_interface = device.interfaces.filter(
                        status=planned_status
                    ).last()

                except Exception as err:
                    self.logger.info(
                        f"Unable to find available interfaces (Planned Status) in {device.name}."
                    )
                    raise

            elif device.role == switch_role:
                access_switch = device
                try:
                    switch_interface = device.interfaces.filter(
                        status=planned_status
                    ).first()
                    switch_access_interfaces = device.interfaces.filter(
                        status=planned_status
                    ).reverse()[:3]

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

        # Update interfaces between router and switch
        router_interface.status = active_status

        router_interface.validated_save()

        switch_interface.status = active_status
        switch_interface.mode = "tagged"

        switch_interface.validated_save()

        # Connect branch devices
        connect_cable_endpoints(router_interface.id, switch_interface.id)

        # Update interfaces between router and ISP router
        try:
            isp_router_interface = isp_router.interfaces.filter(
                status=planned_status
            ).first()

        except Exception as err:
            self.logger.info(
                f"Unable to find available interfaces (Planned Status) in {isp_router.name}."
            )
            raise

        self.logger.info(
            f"Connect: {edge_router.name} interface: {router_isp_interface} <---> {isp_router.name} interface: {isp_router_interface.name}"
        )
        router_isp_interface.status = active_status

        router_isp_interface.validated_save()

        isp_router_interface.status = active_status

        isp_router_interface.validated_save()

        # Connect interfaces between router and ISP router
        connect_cable_endpoints(router_isp_interface.id, isp_router_interface.id)

        # Setup Edge Router
        self.logger.info(f"Setup Edge Router")

        site_prefixes = edge_router.location.prefixes.all()
        site_vlans = edge_router.location.vlans.all().reverse()

        for prefix in site_prefixes:
            self.logger.info(f"Create subinterface for VLAN: {str(prefix.vlan.vid)}")
            int_id = f"{router_interface.name}.{str(prefix.vlan.vid)}"

            interface_ip_address = create_ipaddr(prefix)

            new_int = Interface(
                device=edge_router,
                name=int_id,
                type="virtual",
                description=str(prefix.vlan.vid),
                status=planned_status,
                parent_interface=router_interface,
            )
            new_int.validated_save()
            new_int.ip_addresses.add(interface_ip_address)
            new_int.validated_save()

        self.logger.info("Setup Switch Access Interfaces:")

        for idx, switch_access_interface in enum(switch_access_interfaces):
            self.logger.info(f"Interface: {switch_access_interface.name}")
            switch_access_interface.mode = "access"
            switch_access_interface.description = f"ACCESS VLAN {site_vlans[idx].name}"
            switch_access_interface.untagged_vlan = site_vlans[idx]
            switch_access_interface.validated_save()


register_jobs(DeployBranchSmall)
