# Rate Limiting and Throttling Guide

## What is Rate Limiting?

**Rate limiting** is a technique to control the number of requests a client can make to your API within a specific time period. It helps:

- **Prevent abuse**: Stop malicious users from overwhelming your server
- **Protect resources**: Ensure fair usage of server resources
- **Control costs**: Limit expensive operations
- **Maintain performance**: Keep your API responsive for all users

## What is Throttling?

**Throttling** is Django REST Framework's built-in mechanism for implementing rate limiting. It automatically tracks request counts and enforces limits.

## How Throttling Works in DRF

1. **Request comes in** → DRF checks throttling classes
2. **Throttle class checks** → Has this user/IP exceeded the limit?
3. **If under limit** → Request proceeds normally
4. **If over limit** → Returns `429 Too Many Requests` with retry information

## Throttling Classes in DRF

### Built-in Classes

1. **AnonRateThrottle**
   - For anonymous (unauthenticated) users
   - Identifies users by IP address
   - Use case: Protect public endpoints

2. **UserRateThrottle**
   - For authenticated users
   - Identifies users by user ID
   - Use case: Limit per-user API usage

3. **ScopedRateThrottle**
   - Custom throttling based on view scope
   - Different rates for different endpoints
   - Use case: Different limits for different operations

## Configuration in This Project

### Global Settings (settings.py)

```python
REST_FRAMEWORK = {
    'DEFAULT_THROTTLE_CLASSES': [
        'rest_framework.throttling.AnonRateThrottle',
        'rest_framework.throttling.UserRateThrottle'
    ],
    'DEFAULT_THROTTLE_RATES': {
        'anon': '100/hour',        # Anonymous users: 100 requests/hour
        'user': '1000/hour',       # Authenticated users: 1000 requests/hour
        'burst': '10/minute',      # Burst traffic: 10 requests/minute
        'sustained': '200/day',    # Sustained usage: 200 requests/day
        'anon_burst': '5/minute',  # Anonymous burst: 5 requests/minute
        'create_user': '3/hour',   # User creation: 3 requests/hour
        'read_only': '500/hour',   # Read operations: 500 requests/hour
    }
}
```

### Rate Format

Rates are specified as: `'number/period'`

- **Periods**: `second`, `minute`, `hour`, `day`
- **Examples**:
  - `'100/hour'` = 100 requests per hour
  - `'10/minute'` = 10 requests per minute
  - `'200/day'` = 200 requests per day

## View-Level Throttling

### Example 1: Default Throttling

```python
class UserViewSet(viewsets.ModelViewSet):
    # Uses DEFAULT_THROTTLE_CLASSES from settings
    throttle_classes = [UserRateThrottle, AnonRateThrottle]
```

### Example 2: Custom Throttling per Action

```python
def get_throttles(self):
    if self.action == 'create':
        return [CreateUserThrottle()]  # Stricter for creation
    elif self.action in ['list', 'retrieve']:
        return [ReadOnlyThrottle()]   # More lenient for reads
    else:
        return [BurstRateThrottle()]   # Default for updates
```

### Example 3: Scoped Throttling

```python
class UserViewSet(viewsets.ModelViewSet):
    throttle_scope = 'users'  # Uses 'users' rate from settings
    throttle_classes = [ScopedRateThrottle]
```

## Custom Throttling Classes

We've created custom throttling classes in `quickstart/throttles.py`:

### 1. BurstRateThrottle
- **Rate**: 10 requests/minute
- **Use case**: Prevent rapid-fire requests
- **Applies to**: Authenticated users

### 2. SustainedRateThrottle
- **Rate**: 200 requests/day
- **Use case**: Long-term usage limits
- **Applies to**: Authenticated users

### 3. CreateUserThrottle
- **Rate**: 3 requests/hour
- **Use case**: Prevent registration abuse
- **Applies to**: User creation endpoint

### 4. ReadOnlyThrottle
- **Rate**: 500 requests/hour
- **Use case**: More lenient limits for read operations
- **Applies to**: GET requests

## Testing Throttling

### Test with curl

```bash
# Test anonymous throttling
curl -X GET http://localhost:8000/api/users/

# Test authenticated throttling
curl -X GET http://localhost:8000/api/users/ \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"

# Test user creation throttling
curl -X POST http://localhost:8000/api/users/ \
  -H "Content-Type: application/json" \
  -d '{"username":"testuser","email":"test@example.com","password":"testpass"}'
```

### Expected Response When Throttled

```json
{
    "detail": "Request was throttled. Expected available in 3599 seconds."
}
```

**HTTP Status**: `429 Too Many Requests`

**Headers**:
- `Retry-After`: Number of seconds to wait before retrying
- `X-Throttle-Remaining`: Number of requests remaining
- `X-Throttle-Reset`: Timestamp when throttle resets

## Best Practices

### 1. Set Appropriate Limits
- **Too strict**: Frustrates legitimate users
- **Too lenient**: Doesn't protect your API
- **Recommendation**: Start lenient, tighten based on usage patterns

### 2. Different Limits for Different Operations
- **Read operations**: Higher limits (500-1000/hour)
- **Write operations**: Lower limits (100-200/hour)
- **Destructive operations**: Very low limits (10-50/hour)

### 3. Consider User Types
- **Anonymous users**: Stricter limits (100/hour)
- **Authenticated users**: Higher limits (1000/hour)
- **Premium users**: Even higher limits (5000/hour)

### 4. Monitor and Adjust
- Track throttle violations
- Adjust rates based on actual usage
- Consider implementing different tiers

## Advanced: Custom Throttling Logic

You can create completely custom throttling by overriding the `allow_request` method:

```python
from rest_framework.throttling import BaseThrottle

class CustomThrottle(BaseThrottle):
    def allow_request(self, request, view):
        # Your custom logic here
        # Return True to allow, False to throttle
        user = request.user
        if user.is_superuser:
            return True  # No limit for superusers
        # ... your logic ...
        return True
```

## Disabling Throttling

### For a specific view:
```python
class MyViewSet(viewsets.ModelViewSet):
    throttle_classes = []  # No throttling
```

### For a specific action:
```python
@action(detail=False, methods=['get'])
def my_action(self, request):
    # This action won't be throttled if you remove throttles
    pass
```

## Common Issues and Solutions

### Issue: Throttling not working
**Solution**: Make sure `DEFAULT_THROTTLE_CLASSES` is set in settings

### Issue: Too many 429 errors
**Solution**: Increase throttle rates or adjust limits

### Issue: Throttling based on wrong identifier
**Solution**: Check if using `AnonRateThrottle` (IP-based) vs `UserRateThrottle` (user-based)

## Current Implementation in This Project

1. **Global throttling** enabled for all API views
2. **Custom throttles** for different operations:
   - User creation: 3/hour
   - Read operations: 500/hour
   - Burst protection: 10/minute
3. **View-level customization** in `UserViewSet.get_throttles()`

## Next Steps

1. **Monitor**: Check throttle violations in logs
2. **Adjust**: Fine-tune rates based on usage
3. **Extend**: Add more custom throttles as needed
4. **Document**: Update API documentation with rate limits

## References

- [DRF Throttling Documentation](https://www.django-rest-framework.org/api-guide/throttling/)
- [Rate Limiting Best Practices](https://stripe.com/docs/rate-limits)

