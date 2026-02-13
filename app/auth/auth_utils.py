import inspect
from functools import wraps
from fastapi import Request, HTTPException

def require_scope(required_scope: str):
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            
            request = None
            
            for arg in args:
                if isinstance(arg, Request):
                    request = arg
                    break
            
            if not request:
                request = kwargs.get('request')
            
            if not request:
                print(f"  ERROR in require_scope: Request not found")
                print(f"   Args: {[type(a).__name__ for a in args]}")
                print(f"   Kwargs: {list(kwargs.keys())}")
                raise HTTPException(status_code=500, detail="Request not found in decorator")

            scopes = getattr(request.state, "scopes", [])
            role = getattr(request.state, "role", None)
            role_name = role.role_name if role else "unknown"

            print(f" Checking scope '{required_scope}' for role '{role_name}' with scopes: {scopes}")

            if "admin:full" in scopes:
                print(f"Admin bypass granted")
                if inspect.iscoroutinefunction(func):
                    return await func(*args, **kwargs)
                return func(*args, **kwargs)

            if not any(s in scopes for s in required_scope):
                raise HTTPException(
                    status_code=403,
                    detail=f"Role '{role_name}' lacks required permission: {required_scope}"
                )

            print(f"Scope check passed")
            
            if inspect.iscoroutinefunction(func):
                return await func(*args, **kwargs)
            return func(*args, **kwargs)

        return wrapper
    return decorator


