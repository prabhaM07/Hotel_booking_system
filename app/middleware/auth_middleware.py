from datetime import datetime, timezone
from fastapi import Request, status, HTTPException
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from app.core.database_postgres import SessionLocal
from app.models.user import Users
from app.models.role import Roles
from app.models.token_store import TokenStore
from app.auth.jwt_handler import get_token, verify_access_token, verify_refresh_token
import traceback


class AuthMiddleware(BaseHTTPMiddleware):
    
    def __init__(self, app):
        super().__init__(app)
        self.EXCLUDE_PATHS = [
            "/General/Query/create",
            "/user/login",
            "/user/register",
            "/docs",
            "/openapi.json",
            "/health",
            "/user/verify_email",
            "/"
        ]

    async def dispatch(self, request: Request, call_next):
        
        if request.url.path in self.EXCLUDE_PATHS:
            return await call_next(request)

        db = SessionLocal()
        try:
            print(f"Auth check for: {request.url.path}")

            access_token = get_token(request)
            refresh_token = request.cookies.get("refresh_token")

            if not access_token:
                raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Access token missing")
            if not refresh_token:
                raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Refresh token missing")

            access_payload = verify_access_token(access_token)
            refresh_payload = verify_refresh_token(refresh_token)

            user_id = access_payload.get("sub")
            if not user_id:
                raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid access token payload")

            now = datetime.now(timezone.utc)
            token_entry = db.query(TokenStore).filter(
                TokenStore.user_id == user_id,
                TokenStore.access_token == access_token,
                TokenStore.refresh_token == refresh_token
            ).first()

            if not token_entry:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Session not found. Please login again."
                )

            if token_entry.access_token_expiry <= now:
                print("Access token expired — deleting entry.")
                db.delete(token_entry)
                db.commit()
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Access token expired. Please login again."
                )
            if token_entry.refresh_token_expiry <= now:
                print("Refresh token expired — deleting entry.")
                db.delete(token_entry)
                db.commit()
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Refresh token expired. Please login again."
                )
            user = db.query(Users).filter(Users.id == user_id).first()
            if not user:
                raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")

            role = db.query(Roles).filter(Roles.id == user.role_id).first()
            if not role:
                raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Role not found")

            scopes = [scope.scope_name for scope in role.scope] if role.scope else []
            if not scopes:
                raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="No scopes assigned")

            request.state.user = user
            request.state.role = role
            request.state.scopes = scopes

            print(f"Authenticated user {user.id} with role {role.role_name}")

        except HTTPException as e:
            print(f"HTTPException: {e.detail}")
            db.close()
            return JSONResponse(status_code=e.status_code, content={"detail": e.detail})

        except Exception as e:
            print(f"Middleware Exception: {str(e)}")
            print(traceback.format_exc())
            db.close()
            return JSONResponse(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                content={"detail": f"Authentication failed: {str(e)}"}
            )

        finally:
            db.close()

        response = await call_next(request)
        return response
    
    