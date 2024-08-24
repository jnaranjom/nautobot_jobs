""" GET AVAILABLE PREFIXES """

from nautobot.apps.jobs import Job, ObjectVar, MultiObjectVar, register_jobs
from nautobot.ipam.models import IPAddress, Prefix
from netaddr import *
import pprint


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
        network = IPNetwork(prefix)
        self.logger.info("%s", network.network)
        self.logger.info("%s", network.netmask)
        self.logger.info("%s", network.size)


register_jobs(PrefixDetails)
