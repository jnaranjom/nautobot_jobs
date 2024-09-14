""" JOB TO IMPORT OBJECTS FROM CMDB """

from nautobot.apps.jobs import Job, register_jobs
import requests
import json


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
        location_list = locations.json()

        for location in location_list:
            self.logger.info(f"Name: {location['name']}")
            self.logger.info(f" Parent: {location['parent']}")
            self.logger.info(f" Tenant: {location['tenant']}")


register_jobs(ImportLocations)
