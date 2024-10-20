""" DEPLOY NEW SMALL BRANCH (1 Router/ 1 Switch)"""

from nautobot.apps.jobs import Job, ObjectVar, register_jobs
from nautobot.dcim.models.locations import Location
from nautobot.extras.models.roles import Role
from nautobot.dcim.models import Device
from nautobot.ipam.models import Prefix
from nautobot.dcim.models.device_components import Interface
from nautobot_bgp_models.models import (
    AutonomousSystem,
    BGPRoutingInstance,
    PeerEndpoint,
    Peering,
)
from .cable_helper import connect_cable_endpoints
from .status_helper import find_status_uuid
from .ipaddress_helper import create_ipaddr

# TODO: Add validation for device types and interfaces
# TODO: Add VLANs and Prefixes required for the deployment type


class DeployBranchSmall(Job):
    """Job to deploy new small branch"""

    branch_location = ObjectVar(model=Location, query_params={"tenant": "Branch"})
    isp_router = ObjectVar(model=Device, query_params={"tenant": "ISP"})
    wan_prefix = ObjectVar(
        model=Prefix, query_params={"role": "wan:p2p:prefix", "status": "Active"}
    )

    class Meta:
        """Jobs Metadata"""

    name = "Deploy Devices on small branch"
    description = "Job to deploy devices on a new branch in Nautobot"
    dryrun_default = True
    has_sensitive_variables = False
    approval_required = False
    read_only = False
    hidden = False
    soft_time_limit = 300
    time_limit = 600

    def run(self, branch_location, isp_router, wan_prefix):
        """Main function"""

        branch_devices = Device.objects.filter(location=branch_location)
        router_role = Role.objects.get(name="branch:edge:router")
        switch_role = Role.objects.get(name="branch:access:switch")
        planned_status = find_status_uuid("Planned")
        active_status = find_status_uuid("Active")

        for device in branch_devices:
            self.logger.info(
                "Finding device type and available interfaces for: %s", device["name"]
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
                        "Unable to find available interfaces (Planned Status) in %s. Error: %s",
                        device["name"],
                        err,
                    )
                    raise

            elif device.role == switch_role:
                access_switch = device
                vlan_count = access_switch.location.vlans.count()
                try:
                    switch_interface = device.interfaces.filter(
                        status=planned_status
                    ).first()
                    switch_access_interfaces = device.interfaces.filter(
                        status=planned_status
                    ).reverse()[:vlan_count]

                except Exception as err:
                    self.logger.info(
                        "Unable to find available interfaces (Planned Status) in %s. Error: %s",
                        device["name"],
                        err,
                    )
                    raise

            else:
                self.logger.info("Unable to find device type for %s.", device["name"])

        # Update interfaces between router and switch
        try:
            self.logger.info(
                "Connect: %s interface: %s <--> %s interface: %s",
                edge_router["name"],
                router_interface,
                access_switch["name"],
                switch_interface,
            )

            router_interface.status = active_status
            router_interface.validated_save()

            switch_interface.status = active_status
            switch_interface.mode = "tagged"
            switch_interface.validated_save()

            # Connect branch devices
            connect_cable_endpoints(router_interface.id, switch_interface.id)

        except Exception as err:
            self.logger.info(
                "Unable to connect %s with %s.",
                edge_router["name"],
                access_switch["name"],
            )
            raise

        # Update interfaces between router and ISP router
        try:
            isp_router_interface = isp_router.interfaces.filter(
                status=planned_status
            ).first()

        except Exception as err:
            self.logger.info(
                "Unable to find available interfaces (Planned Status) in %s.",
                isp_router["name"],
            )
            raise

        self.logger.info(
            "Connect: %s interface: %s <--> %s interface: %s",
            edge_router["name"],
            router_isp_interface,
            isp_router["name"],
            isp_router_interface["name"],
        )

        # Allocate IPs and connect interfaces between router and ISP router
        try:
            router_isp_interface_ip = create_ipaddr(wan_prefix)
            router_isp_interface.ip_addresses.add(router_isp_interface_ip)
            router_isp_interface.status = active_status
            router_isp_interface.validated_save()

            isp_router_interface_ip = create_ipaddr(wan_prefix)
            isp_router_interface.ip_addresses.add(isp_router_interface_ip)
            isp_router_interface.status = active_status
            isp_router_interface.validated_save()

            connect_cable_endpoints(router_isp_interface.id, isp_router_interface.id)

        except Exception as err:
            self.logger.info(
                "Unable to connect %s with %s", edge_router["name"], isp_router["name"]
            )
            raise

        # Setup Edge Router
        self.logger.info(f"Create objects for: {edge_router.name}.")

        site_prefixes = edge_router.location.prefixes.all()
        site_vlans = edge_router.location.vlans.all().reverse()

        for prefix in site_prefixes:
            self.logger.info("  Create subinterface for VLAN: %s", str(prefix.vlan.vid))
            int_id = f"{router_interface.name}.{str(prefix.vlan.vid)}"

            interface_ip_address = create_ipaddr(prefix)

            new_int = Interface(
                device=edge_router,
                name=int_id,
                type="virtual",
                description=f"VLAN::{prefix.vlan.vid}",
                status=planned_status,
                parent_interface=router_interface,
            )
            new_int.validated_save()
            new_int.ip_addresses.add(interface_ip_address)
            new_int.validated_save()

        # Setup BGP for Edge Router

        self.logger.info(f"Build BGP sessions for: {edge_router.name}")

        # Create BGP endpoints
        router_asn = AutonomousSystem.objects.get(asn=edge_router.location.asn)
        router_bgp_instance = BGPRoutingInstance(
            device=edge_router, autonomous_system=router_asn, status=active_status
        )
        router_bgp_instance.validated_save()

        isp_router_bgp_instance = BGPRoutingInstance.objects.get(device=isp_router)

        endpoint_a = PeerEndpoint(
            routing_instance=router_bgp_instance,
            enabled=True,
            source_ip=router_isp_interface_ip,
        )
        endpoint_z = PeerEndpoint(
            routing_instance=isp_router_bgp_instance,
            enabled=True,
            source_ip=isp_router_interface_ip,
        )

        # Create BGP peerings
        peering = Peering.objects.create(status=active_status)
        peering.validated_save()

        endpoint_a.peering = peering
        endpoint_a.validated_save()

        endpoint_z.peering = peering
        endpoint_z.validated_save()

        peering.update_peers()
        peering.validate_peers()

        # Setup Switch access interfaces

        self.logger.info("Setup switch %s access interfaces:", access_switch["name"])

        try:
            for idx, switch_access_interface in enumerate(switch_access_interfaces):
                self.logger.info("  Interface: %s", switch_access_interface["name"])
                switch_access_interface.mode = "access"
                switch_access_interface.description = (
                    f"VLAN::{site_vlans[idx].name}::{site_vlans[idx].vid}"
                )
                switch_access_interface.untagged_vlan = site_vlans[idx]
                switch_access_interface.validated_save()

        except Exception as err:
            self.logger.info(
                "Unable to set VLANS on %s access ports.", access_switch["name"]
            )
            raise


register_jobs(DeployBranchSmall)
