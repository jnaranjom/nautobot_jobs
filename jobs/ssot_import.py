""" JOB TO IMPORT OBJECTS FROM CMDB """

from nautobot.apps.jobs import Job, register_jobs
from nautobot.dcim.models.locations import Location
from nautobot.dcim.models import Device
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
            self.logger.info(f" Checking Location: {location['name']}")
            try:
                existing_locations = Location.objects.get(
                    name=location["name"],
                    tenant__name=location["tenant"],
                    parent__name=location["parent"],
                )
                self.logger.info(f" Location {location['name']} found")
            except:
                self.logger.info(
                    f" Location {location['name']} not found, will add new location."
                )


class ImportDevices(Job):
    """Import Devices from CMDB"""

    class Meta:
        """Jobs Metadata"""

    name = "Get List of devices from the CMDB"
    description = "Job to read the devices from the CMDB"
    dryrun_default = True

    def run(self):
        """Main function"""

        devices = requests.get("http://192.168.2.245:8000/api/v1/devices")
        device_list = devices.json()

        for device in device_list:
            self.logger.info(f" Checking Device: {device['name']}")
            try:
                existing_devices = Device.objects.get(
                    name=device["name"],
                    tenant__name=device["tenant"],
                    location__name=device["location"],
                )
                self.logger.info(f" Device {device['name']} found")
            except:
                self.logger.info(
                    f" Device {device['name']} not found, will add new device."
                )


register_jobs(ImportLocations, ImportDevices)
