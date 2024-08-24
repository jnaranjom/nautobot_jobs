""" GET DEVICES DETAILS FROM A TENANT """

from nautobot.apps.jobs import Job, ObjectVar, MultiObjectVar, register_jobs
from nautobot.tenancy.models import Tenant
from nautobot.extras.models import Status
from nautobot.dcim.models.devices import Device


class DeviceDetails(Job):
    """Example job definition"""

    tenant = ObjectVar(model=Tenant)

    status = ObjectVar(model=Status)
    
    devices = MultiObjectVar(
        model=Device, query_params={"status": "$status", "tenant": "$tenant"}
    )
    
    
    class Meta:
        """Jobs Metadata"""

        name = "Get Device Details"
        description = "Job to retrieve device details"
        dryrun_default = True

    def run(self, tenant, status, devices):
        """_summary_

        Args:
            devices (_type_): _description_
        """

        for device in devices:
            self.logger.info("%s", device.name)
            self.logger.info(f"Platform: {device.platform}")
            self.logger.info(f"Status: {device.status}")
            self.logger.info(f"Location: {device.location}")
            self.logger.info(f"Role: {device.role}")
            if device.primary_ip4:
                self.logger.info(f"{device.name}: {device.primary_ip4}")
            else:
                self.logger.info(f"Unable to find Primary IPv4 for {device.name}")


register_jobs(DeviceDetails)
