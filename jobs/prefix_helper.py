p2p_prefix = Prefix.objects.get(prefix="10.100.0.0/24")

#TODO: find how to create the first /30 on this prefix

# Find the next /30:
p2p_prefix.get_first_available_prefix()

# Create a new /30
new_prefix = Prefix(prefix='10.100.0.4/30', namespace=p2p_prefix.namespace, tenant = p2p_prefix.tenant, type=p2p_prefix.type, role = p2p_prefix.role. status=reserved_status)

new_prefix.validated_save()
