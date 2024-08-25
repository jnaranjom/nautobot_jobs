""" GET all devices """

from nautobot.apps.jobs import Job, register_jobs
from nautobot.dcim.models.devices import Device

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

        for device in mydevices:
            if device.device_type.manufacturer.name == 'Cisco':
                self.logger.info("Cisco: %s", device.name)
            elif device.device_type.manufacturer.name == 'Arista':
                self.logger.info("Arista: %s", device.name)
            else:
                self.logger.info("Unknown: %s", device.name)



register_jobs(AllDevices)
