""" JOB TO IMPORT OBJECTS FROM CMDB """

import requests
from nautobot.apps.jobs import Job, register_jobs
from nautobot.dcim.models.locations import Location
from nautobot.dcim.models import Device
from .location_helper import create_location
from .device_helper import create_device


CMDB_URL = "http://192.168.2.201:8000/api/v1"


class ImportLocations(Job):
    """Import Locations from CMDB"""

    class Meta:
        """Jobs Metadata"""

    name = "Get List of locations from the CMDB"
    description = "Job to read the locations from the CMDB"
    dryrun_default = True
    has_sensitive_variables = False
    approval_required = False
    read_only = False
    hidden = False
    soft_time_limit = 300
    time_limit = 600

    def run(self):
        """Main function"""

        locations = requests.get(f"{CMDB_URL}/locations", verify=False, timeout=10)
        location_list = locations.json()

        for location in location_list:
            if location["location_type"] not in ["Country", "State", "City"]:
                self.logger.info(" Checking Location: %s", location["name"])
                try:
                    validate_location = Location.objects.get(
                        name=location["name"],
                        tenant__name=location["tenant"],
                        parent__name=location["parent"],
                    )
                    self.logger.info("-> Location %s found", location["name"])
                except:
                    if location["status"] == "Staging":
                        new_location = create_location(
                            location["name"],
                            location["location_type"],
                            location["tenant"],
                            location["parent"],
                        )
                        self.logger.info(
                            "-> New location %s created successfully.",
                            new_location["name"],
                        )
                    else:
                        self.logger.info(
                            " New location %s not ready for onboarding. Current status: %s",
                            location["name"],
                            location["status"],
                        )


class ImportDevices(Job):
    """Import Devices from CMDB"""

    class Meta:
        """Jobs Metadata"""

    name = "Get List of devices from the CMDB"
    description = "Job to read the devices from the CMDB"
    dryrun_default = True
    has_sensitive_variables = False
    approval_required = False
    read_only = False
    hidden = False
    soft_time_limit = 300
    time_limit = 600

    def run(self):
        """Main function"""

        devices = requests.get(f"{CMDB_URL}/devices", verify=False, timeout=10)
        device_list = devices.json()

        for device in device_list:
            self.logger.info(" Checking Device: %s", device["name"])
            if Device.objects.filter(name=device["name"]).exists():
                self.logger.info(" Device %s found. Skipping...", device["name"])
            else:
                if device["status"] == "Staged":
                    new_device = create_device(
                        self,
                        device["name"],
                        device["serial_number"],
                        device["role"],
                        device["device_type"],
                        device["location"],
                        device["tenant"],
                    )
                    self.logger.info(
                        "-> New device %s created successfully.", new_device["name"]
                    )
                else:
                    self.logger.info(
                        " New device %s not ready for onboarding. Current status: %s",
                        device["name"],
                        device["status"],
                    )


register_jobs(ImportLocations, ImportDevices)
