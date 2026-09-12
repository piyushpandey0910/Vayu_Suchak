from typing import Optional
from fastapi import Request

class UserPlaceholder:
    """
    Placeholder user representation for future auth implementation.
    In v1 (no-auth), this is always None unless explicitly mock-injected.
    """
    id: str
    email: str
    is_active: bool = True

async def get_current_user_optional(request: Request) -> Optional[UserPlaceholder]:
    """
    Dependency injection hook for optional user authentication.
    Currently returns None for public, no-auth access.
    Can later be wired to inspect Bearer tokens/JWT cookies without modifying route signatures.
    """
    # Placeholder: Future JWT decoding or session verification will be placed here
    # Example:
    # auth_header = request.headers.get("Authorization")
    # if auth_header and auth_header.startswith("Bearer "):
    #     token = auth_header.split(" ")[1]
    #     return verify_jwt_token(token)
    return None
