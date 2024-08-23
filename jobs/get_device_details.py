""" GET HOSTNAME OF ALL DEVICES """

from nautobot.apps.jobs import Job, ObjectVar, register_jobs
from nautobot.tenancy.models import Tenant


class GetHostnames(Job):
    """Example job definition"""

    tenant = ObjectVar(model=Tenant)

    class Meta:
        """Jobs Metadata"""

        name = "Get Hostnames"
        description = "Job to retrieve device info"
        dryrun_default = True

    def run(self, tenant):
        """_summary_

        Args:
            devices (_type_): _description_
        """
        self.logger.info("%s", tenant)


register_jobs(GetHostnames)
