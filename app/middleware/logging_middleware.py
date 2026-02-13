import logging
import json
import os
from datetime import datetime
from logging.handlers import TimedRotatingFileHandler
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
import time

LOG_DIR = os.path.join(os.path.dirname(__file__), "..", "logs")
os.makedirs(LOG_DIR, exist_ok=True)

logger = logging.getLogger("activity_logger")
logger.setLevel(logging.INFO)

if not logger.handlers:
    log_file_path = os.path.join(LOG_DIR, "activity.log")
    file_handler = TimedRotatingFileHandler(
        log_file_path,
        when="midnight",
        interval=1,
        backupCount=30,
        encoding="utf-8"
    )
    file_handler.suffix = "%Y-%m-%d"

    class JsonFormatter(logging.Formatter):
        def format(self, record):
            log_data = {
                "timestamp": datetime.utcnow().isoformat() + "Z",
                "level": record.levelname,
                "message": record.getMessage(),
            }
            if hasattr(record, "extra_data"):
                log_data.update(record.extra_data)
            return json.dumps(log_data)

    file_handler.setFormatter(JsonFormatter())
    logger.addHandler(file_handler)

console_handler = logging.StreamHandler()
console_handler.setFormatter(logging.Formatter('%(message)s'))
logger.addHandler(console_handler)


class ActivityLoggingMiddleware(BaseHTTPMiddleware):

    
    EXCLUDE_PATHS = ["/health", "/docs", "/openapi.json", "/favicon.ico","/user/me",
        "/user/recent-activity"]
    
    async def dispatch(self, request: Request, call_next):
        if request.url.path in self.EXCLUDE_PATHS:
            return await call_next(request)

        start_time = time.time()
        
        user = getattr(request.state, "user", None)
        role = getattr(request.state, "role", None)
        
        client_ip = request.headers.get("x-forwarded-for", 
                                       request.client.host if request.client else "unknown")
        if "," in client_ip:
            client_ip = client_ip.split(",")[0].strip()
        
        request_body = None
        if request.method in ["POST", "PUT", "PATCH"]:
            try:
                body_bytes = await request.body()
                
                async def receive():
                    return {"type": "http.request", "body": body_bytes}
                
                request._receive = receive
                
                if body_bytes:
                    body_str = body_bytes.decode("utf-8")[:500]
                    if "password" in body_str.lower():
                        request_body = "[REDACTED - Contains sensitive data]"
                    else:
                        request_body = body_str
            except Exception as e:
                request_body = f"[Could not parse body: {str(e)}]"
        
        response = None
        error = None
        status_code = 500
        
        try:
            response = await call_next(request)
            status_code = response.status_code
            
            user = getattr(request.state, "user", None)
            role = getattr(request.state, "role", None)
            
        except Exception as e:
            error = str(e)
            logger.error(f"Exception in request processing: {error}")
            raise
        finally:
            duration = time.time() - start_time
            
            log_data = {
                "event": "api_request",
                "method": request.method,
                "path": request.url.path,
                "query_params": dict(request.query_params) if request.query_params else None,
                "user_id": user.id if user and hasattr(user, 'id') else None,
                "user_email": user.email if user and hasattr(user, 'email') else None,
                "role": role.role_name if role and hasattr(role, 'role_name') else None,
                "client_ip": client_ip,
                "user_agent": request.headers.get("user-agent", "unknown")[:200],
                "status_code": status_code,
                "duration_ms": round(duration * 1000, 2),
                "error": error,
            }
            
            if status_code >= 500:
                logger.error("API Request", extra={"extra_data": log_data})
            elif status_code >= 400:
                logger.warning("API Request", extra={"extra_data": log_data})
            else:
                logger.info("API Request", extra={"extra_data": log_data})
            
            print(f"LOGGED: {request.method} {request.url.path} - {status_code}")
        
        return response


def get_recent_activities(limit: int = 50, user_id: int = None):
    """
    Read recent activities from log file for admin dashboard.
    """
    activities = []
    
    log_files_to_check = []
    
    main_log = os.path.join(LOG_DIR, "activity.log")
    log_files_to_check.append(main_log)
    
    for i in range(7):
        from datetime import timedelta
        date = datetime.now() - timedelta(days=i)
        rotated_log = os.path.join(LOG_DIR, f"activity.log.{date.strftime('%Y-%m-%d')}")
        log_files_to_check.append(rotated_log)
    
    print(f"DEBUG: Checking log files: {log_files_to_check}")
    print(f"DEBUG: LOG_DIR exists: {os.path.exists(LOG_DIR)}")
    print(f"DEBUG: LOG_DIR contents: {os.listdir(LOG_DIR) if os.path.exists(LOG_DIR) else 'N/A'}")
    
    for log_file in log_files_to_check:
        if not os.path.exists(log_file):
            continue
        
        print(f"DEBUG: Reading log file: {log_file}")
        
        try:
            with open(log_file, "r", encoding="utf-8") as f:
                lines = f.readlines()
                print(f"DEBUG: Found {len(lines)} lines in {log_file}")
                
                for idx, line in enumerate(lines):
                    line = line.strip()
                    if not line:
                        continue
                        
                    try:
                        log_entry = json.loads(line)
                        print(f"DEBUG: Line {idx+1} parsed successfully. Keys: {list(log_entry.keys())}")
                        
                        if log_entry.get("event") != "api_request":
                            print(f"DEBUG: Skipping line {idx+1} - not an api_request event")
                            continue
                        
                        if user_id is not None:
                            entry_user_id = log_entry.get("user_id")
                            print(f"DEBUG: Filtering - entry_user_id: {entry_user_id}, requested: {user_id}")
                            if entry_user_id != user_id:
                                continue
                        
                        activities.append(log_entry)
                        print(f"DEBUG: Added activity {len(activities)}")
                        
                        if len(activities) >= limit:
                            break
                    except json.JSONDecodeError as e:
                        print(f"DEBUG: Failed to parse line {idx+1}: {line[:100]} - Error: {e}")
                        continue
                    except Exception as e:
                        print(f"DEBUG: Error processing line {idx+1}: {e}")
                        continue
                        
            if len(activities) >= limit:
                break
                
        except Exception as e:
            print(f"ERROR reading log file {log_file}: {e}")
            logger.error(f"Error reading log file {log_file}: {e}")
    
    print(f"DEBUG: Total activities found: {len(activities)}")
    
    return sorted(activities, key=lambda x: x.get("timestamp", ""), reverse=True)[:limit]