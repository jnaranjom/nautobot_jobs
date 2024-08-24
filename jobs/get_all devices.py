""" GET DEVICE DETAILS IN SPECIFIC LOCATION """

from nautobot.apps.jobs import Job, register_jobs
from nautobot.dcim.models.devices import Device


class AllDevices(Job):
    """Example job definition"""

    devices = Device.objects.all()

    class Meta:
        """Jobs Metadata"""

        name = "Get Device Details for a location"
        description = "Job to retrieve device details"
        dryrun_default = True

    def run(self, devices):
        """_summary_

        Args:
            devices (_type_): _description_
        """

        for device in devices:
            self.logger.info("%s", device.name)

register_jobs(AllDevices)
