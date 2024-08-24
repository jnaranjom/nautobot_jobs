""" GET DEVICE DETAILS IN SPECIFIC LOCATION """

from nautobot.apps.jobs import Job, register_jobs
from nautobot.dcim.models.devices import Device


class AllDevices(Job):
    """Example job definition"""

    devices = Devices.objects.all()

    for device in devices:
        self.logger.info("%s", device.name)

    class Meta:
        """Jobs Metadata"""

        name = "Get Device Details for a location"
        description = "Job to retrieve device details"
        dryrun_default = True


register_jobs(AllDevices)
