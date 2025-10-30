# Feature: User Authentication System

## FEATURE

Build a JWT-based user authentication system with the following capabilities:
- User registration with email/password
- Login with JWT token generation
- Token refresh mechanism
- Password reset functionality
- Email verification

**Acceptance Criteria:**
1. Users can register with valid email and password
2. Login returns JWT access token and refresh token
3. Protected endpoints validate JWT tokens
4. Token refresh extends session without re-login
5. Password reset sends email with secure token

## EXAMPLES

Example authentication flow from existing OAuth implementation:

```python
async def authenticate_user(email: str, password: str) -> dict:
    """Authenticate user and return JWT tokens."""
    try:
        user = await db.users.find_one({"email": email})
        if not user or not verify_password(password, user["password_hash"]):
            raise AuthenticationError("Invalid credentials")

        access_token = create_jwt(user["id"], expires_in=3600)
        refresh_token = create_jwt(user["id"], expires_in=86400, type="refresh")

        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "user_id": user["id"]
        }
    except Exception as e:
        logger.error(f"Authentication failed: {e}")
        raise
```

See src/oauth.py:42-67 for similar async authentication pattern

Error handling pattern used in existing codebase:
- Try-catch with specific exceptions
- Logger.error for debugging
- Re-raise with context

## DOCUMENTATION

- [JWT Best Practices](https://jwt.io/introduction)
- [FastAPI Security](https://fastapi.tiangolo.com/tutorial/security/)
- "pytest" for testing
- "bcrypt" for password hashing

## OTHER CONSIDERATIONS

**Security:**
- Hash passwords with bcrypt (cost factor 12)
- Use secure random for JWT secrets
- Implement rate limiting on login endpoint (5 attempts per 15 min)
- Store refresh tokens in secure HTTP-only cookies

**Performance:**
- Cache JWT validation results (5 min TTL)
- Use connection pooling for database queries
- Async/await throughout for non-blocking I/O

**Edge Cases:**
- Handle concurrent login attempts
- Token expiration during request processing
- Email already registered
- Invalid JWT signature
