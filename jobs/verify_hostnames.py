"""
   Copyright 2021 Network to Code

   Licensed under the Apache License, Version 2.0 (the "License");
   you may not use this file except in compliance with the License.
   You may obtain a copy of the License at

       http://www.apache.org/licenses/LICENSE-2.0

   Unless required by applicable law or agreed to in writing, software
   distributed under the License is distributed on an "AS IS" BASIS,
   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
   See the License for the specific language governing permissions and
   limitations under the License.
"""

import re
from nautobot.extras.jobs import Job, StringVar, MultiObjectVar, register_jobs
from nautobot.dcim.models import Device, DeviceRole, DeviceType, Site


def filter_devices(data, log):
    """Returns a list of devices per filter parameters
    
    Args:
        data: A dictionary from the job input
        log: The log instance for logs
    """

    devices = Device.objects.all()

    site = data["site"]
    if site:
        log(f"Filter sites: {normalize(site)}")
        # *__in enables passing the query set as a parameter
        devices = devices.filter(site__in=site)

    device_role = data["device_role"]
    if device_role:
        log(f"Filter device roles: {normalize(device_role)}")
        devices = devices.filter(device_role__in=device_role)

    device_type = data["device_type"]
    if device_type:
        log(f"Filter device types: {normalize(device_type)}")
        devices = devices.filter(device_type__in=device_type)

    return devices


class FormData:
    site = MultiObjectVar(
        model = Site,
        required = False,
    )
    device_role = MultiObjectVar(
        model = DeviceRole,
        required = False,
    )
    device_type = MultiObjectVar(
        model = DeviceType,
        required = False,
    )


class VerifyHostnames(Job):
    """Demo job that verifies device hostnames match corporate standards."""

    class Meta:
        """Meta class for VerifyHostnames"""

        name = "Verify Hostnames"
        description = "Verify device hostnames match corporate standards"
        read_only = True

    site = FormData.site
    device_role = FormData.device_role
    device_type = FormData.device_type
    hostname_regex = StringVar(
        description = "Regular expression to check the hostname against",
        default = ".*",
        required = True
    )

    def run(self, data=None, commit=None):
        """Executes the job"""

        regex = data["hostname_regex"]
        self.log(f"Using the regular expression: {regex}") 
        for device in filter_devices(data, self.log_debug):
            if re.search(regex, device.name):
                self.log_success(obj=device, message="Hostname is compliant.")
            else:
                self.log_failure(obj=device, message="Hostname is not compliant.")

register_jobs(VerifyHostnames)
