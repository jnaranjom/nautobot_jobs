""" GET all devices """

from nautobot.apps.jobs import Job, register_jobs
from nautobot.dcim.models.devices import Device
from nautobot.ipam.models import Prefix


class AllDevices(Job):
    """Example job definition"""

    class Meta:
        """Jobs Metadata"""

        name = "Get All devices"
        description = "Job to retrieve device details"
        dryrun_default = True

    def run(self):
        """_summary_

        Args:
            devices (_type_): _description_
        """
        mydevices = Device.objects.all()
        myprefixes = Prefix.objects.all()

        for device in mydevices:
            self.logger.info("%s", device.name)

        for prefix in prefixes:
            self.logger.info("%s", prefix)

register_jobs(AllDevices)
