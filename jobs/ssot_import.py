""" JOB TO IMPORT OBJECTS FROM CMDB """

from nautobot.apps.jobs import Job
import requests


class ImportLocations(Job):
    """Import Locations from CMDB"""

    class Meta:
        """Jobs Metadata"""

    name = "Get List of locations from the CMDB"
    description = "Job to read the locations from the CMDB"
    dryrun_default = True

    def run(self):
        """Main function"""

        locations = requests.get("http://192.168.2.245:8000/api/v1/locations")

        self.logger.info(f"Locations on CMDB {locations}")


register_jobs(ImportLocations)
