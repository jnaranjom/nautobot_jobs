""" GET HOSTNAME OF ALL DEVICES """

import os
from nautobot.apps.jobs import Job, MultiObjectVar, register_jobs
from nautobot.dcim.models.devices import Device, DeviceRedundancyGroup, DeviceType, Manufacturer, Platform, VirtualChassis

class GetHostnames(Job):
    """ Example job definition """

    devices = MultiObjectVar (
        model=Device,
        query_params={
            'status': 'Active'
        }
    )

    class Meta:
        """ Jobs Metadata """
        name = "Get Hostnames"
        description = "Description of Get Hostnames job"
        dryrun_default = True

    def run(self, devices):
        """ Main function """
        for device in devices:
            self.logger.info(f"{device.role}")

register_jobs(GetHostnames)
