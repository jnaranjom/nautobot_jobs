""" GET AVAILABLE PREFIXES """

from nautobot.apps.jobs import Job, ObjectVar, MultiObjectVar, register_jobs
from nautobot.ipam.models import IPAddress, Prefix
from nautobot.extras.models import Status, Role


class PrefixDetails(Job):
    """Example job definition"""

    role = ObjectVar(model=Role)

    prefix = ObjectVar(model=Prefix, query_params={"role": "$role"})

    class Meta:
        """Jobs Metadata"""

        name = "Get Prefix Details"
        description = "Job to retrieve Prefix details"
        dryrun_default = True

    def run(self, role, prefix):
        """_summary_

        Args:
            Prefixs (_type_): _description_
        """
        self.logger.info("Role: %s", role)
        self.logger.info("Prefix: %s", prefix)


register_jobs(PrefixDetails)
