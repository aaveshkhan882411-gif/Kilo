"""Deprecated tenant middleware.

Tenant isolation is enforced from the authenticated user organization ID
at the router/service authorization layer. Client-supplied X-Tenant-ID is
not trusted as an authorization source.
"""
