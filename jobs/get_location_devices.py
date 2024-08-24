""" GET DEVICE DETAILS IN SPECIFIC LOCATION """

from nautobot.apps.jobs import Job, ObjectVar, MultiObjectVar, register_jobs
from nautobot.dcim.models.locations import Location, LocationType
from nautobot.dcim.models.devices import Device


class LocationDevices(Job):
    """Example job definition"""

    location = ObjectVar(model=Location)

    devices = MultiObjectVar(model=Device, query_params={"location": "$location"})

    class Meta:
        """Jobs Metadata"""

        name = "Get Device Details for a location"
        description = "Job to retrieve device details"
        dryrun_default = True

    def run(self, location, devices):
        """_summary_

        Args:
            devices (_type_): _description_
        """

        for device in devices:
            self.logger.info("%s", device.name)
            self.logger.info(f"Platform: {device.platform}")
            self.logger.info(f"Status: {device.status}")
            self.logger.info(f"Role: {device.role}")
            if device.primary_ip4:
                self.logger.info(f"{device.name}: {device.primary_ip4}")
            else:
                self.logger.info(f"Unable to find Primary IPv4 for {device.name}")


register_jobs(LocationDevices)
