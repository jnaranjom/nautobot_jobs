""" GET HOSTNAME OF ALL DEVICES """

from nautobot.apps.jobs import Job, ObjectVar, register_jobs
from nautobot.tenancy.models import Tenant


class GetHostnames(Job):
    """Example job definition"""

    tenant = ObjectVar(model=Tenant)

    devices = MultiObjectVar(
        model=Device, query_params={"status": "Active", "tenant": "$tenant"}
    )

    class Meta:
        """Jobs Metadata"""

        name = "Get Hostnames"
        description = "Job to retrieve device info"
        dryrun_default = True

    def run(self, devices):
        """_summary_

        Args:
            devices (_type_): _description_
        """

        for device in devices:
            self.logger.info("%s", device.name)
            self.logger.info(f'{device.name}: {device.platform}')
            self.logger.info(f'{device.name}: {device.status}')
            if device.primary_ip4:
                self.logger.info(f'{device.name}: {device.primary_ip4}')
            else:
                self.logger.info(f'Unable to find Primary IPv4 for {device.name}')


register_jobs(GetHostnames)
