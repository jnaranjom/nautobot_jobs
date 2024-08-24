""" GET AVAILABLE PREFIXES """

from nautobot.apps.jobs import Job, ObjectVar, MultiObjectVar, register_jobs
from nautobot.ipam.models import IPAddress, Prefix
from nautobot.extras.models import Status, Role
from nautobot.tenancy.models import Tenant


class PrefixDetails(Job):
    """Example job definition"""

    tenant = ObjectVar(model=Tenant)

    role = ObjectVar(model=Role, query_params={"tenant": "$tenant"})

    prefix = ObjectVar(model=Prefix, query_params={"role": "$role"})

    class Meta:
        """Jobs Metadata"""

        name = "Get Prefix Details"
        description = "Job to retrieve Prefix details"
        dryrun_default = True

    def run(self, tenant, role, prefix):
        """_summary_

        Args:
            Prefixs (_type_): _description_
        """
        self.logger.info("%s", tenant)
        self.logger.info("%s", prefix)


register_jobs(PrefixDetails)
