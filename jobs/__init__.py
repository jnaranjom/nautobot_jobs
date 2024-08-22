""" REGISTER JOBS HERE """

from nautobot.apps.jobs import register_jobs
from .get_hostnames import GetHostnames

register_jobs(GetHostnames)
