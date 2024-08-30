from nautobot.dcim.models import Device, Cable
from nautobot.extras.models import Status
from django.contrib.contenttypes.models import ContentType


def connect_cable_endpoints(side_a, side_b):
    """Function to connect cables between objects (devices)"""

    termination_type = ContentType.objects.get(app_label="dcim", model="interface")
    cable_status = Status.objects.get(name="Connected")

    connect_cable, _ = Cable.objects.get_or_create(
        termination_a_type=termination_type,
        termination_a_id=side_a.id,
        termination_b_type=termination_type,
        termination_b_id=side_b.id,
        status=cable_status,
    )

    connect_cable.validated_save()
