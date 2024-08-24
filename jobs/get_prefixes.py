""" GET AVAILABLE PREFIXES """

from nautobot.apps.jobs import Job, ObjectVar, MultiObjectVar, register_jobs
from nautobot.ipam.models import IPAddress, Prefix


class PrefixDetails(Job):
    """Example job definition"""

    prefix = ObjectVar(model=Prefix)

    class Meta:
        """Jobs Metadata"""

        name = "Get Prefix Details"
        description = "Job to retrieve Prefix details"
        dryrun_default = True

    def run(self, prefix):
        """_summary_

        Args:
            Prefixs (_type_): _description_
        """

        self.logger.info("%s", prefix)


register_jobs(PrefixDetails)
