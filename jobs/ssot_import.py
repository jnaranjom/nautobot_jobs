""" JOB TO IMPORT OBJECTS FROM CMDB """

from nautobot.apps.jobs import Job, register_jobs
from nautobot.dcim.models.locations import Location
from nautobot.dcim.models import Device
from .location_helper import create_location
import requests
import json

CMDB_URL = "http://192.168.2.245:8000/api/v1"


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

        locations = requests.get(f"{CMDB_URL}/locations")
        location_list = locations.json()

        for location in location_list:
            self.logger.info(f" Checking Location: {location['name']}")
            if location["location_type"] not in ["Country", "State", "City"]:
                try:
                    validate_location = Location.objects.get(
                        name=location["name"],
                        tenant__name=location["tenant"],
                        parent__name=location["parent"],
                    )
                    self.logger.info(f"-> Location {location['name']} found")
                except:
                    if location["status"] == "Staging":
                        new_location = create_location(
                            location["name"],
                            location["location_type"],
                            location["tenant"],
                            location["parent"],
                        )
                        self.logger.info(
                            f"-> New location {new_location.name} created successfully."
                        )
                    else:
                        self.logger.info(
                            f" New location {location['name']} not ready for onboarding. Current status: {location['status']}"
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

        devices = requests.get(f"{CMDB_URL}/devices")
        device_list = devices.json()

        for device in device_list:
            self.logger.info(f" Checking Device: {device['name']}")
            try:
                validate_device = Device.objects.get(
                    name=device["name"],
                    tenant__name=device["tenant"],
                    location__name=device["location"],
                )
                self.logger.info(f" Device {device['name']} found. Skipping...")
            except:
                self.logger.info(
                    f"""Device {device['name']} not found, will add new device.
                        This is a {device['manufacturer']} {device['device_type'].upper()}"""
                )


register_jobs(ImportLocations, ImportDevices)
