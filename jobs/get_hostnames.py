""" GET HOSTNAME OF ALL DEVICES """

import os
from nautobot.apps.jobs import Job, MultiObjectVar
from nautobot.dcim.models.devices import Device, DeviceRedundancyGroup, DeviceType, Manufacturer, Platform, VirtualChassis

class GetHostnames(Job):
    """ Example job definition """

    tenant = ObjectVar (
        tenant=Tenant
    )
    
    devices = MultiObjectVar (
        model=Device,
        query_params={
            'status': 'Active',
            'tenant': "$tenant"
        }
    )

    class Meta:
        """ Jobs Metadata """
        name = "Get Hostnames"
        description = "Job to retrieve devices Role"
        dryrun_default = True

    def run(self, devices):
        """ Main function """
        for device in devices:
            self.logger.info(f"{device.name}: {device.role}")
            self.logger.info(f"{device.name}: {device.platform}")
            self.logger.info(f"{device.name}: {device.status}")
            if device.primary_ip4:
                self.logger.info(f"{device.name}: {device.primary_ip4}")
            else:
                self.logger.info(f"Unable to find Primary IPv4 for {device.name} ")
