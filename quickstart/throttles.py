"""
Custom throttling classes for rate limiting API requests.
"""
from rest_framework.throttling import UserRateThrottle, AnonRateThrottle, ScopedRateThrottle


class BurstRateThrottle(UserRateThrottle):
    """
    Throttle for handling burst traffic.
    Allows 10 requests per minute for authenticated users.
    """
    scope = 'burst'


class SustainedRateThrottle(UserRateThrottle):
    """
    Throttle for sustained usage over longer periods.
    Allows 200 requests per day for authenticated users.
    """
    scope = 'sustained'


class AnonBurstRateThrottle(AnonRateThrottle):
    """
    Throttle for anonymous users with burst protection.
    Allows 5 requests per minute for anonymous users.
    """
    scope = 'anon_burst'


class CreateUserThrottle(ScopedRateThrottle):
    """
    Custom throttle specifically for user creation endpoint.
    Prevents abuse of registration endpoints.
    """
    scope = 'create_user'


class ReadOnlyThrottle(ScopedRateThrottle):
    """
    More lenient throttle for read-only operations.
    """
    scope = 'read_only'

