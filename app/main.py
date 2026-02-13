from fastapi import Depends, FastAPI 
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from app.core.database_postgres import init_db
from app.middleware.auth_middleware import AuthMiddleware
from app.routes import booked_contact, general_contact, postgress_backup_restore, users,feature,room_type_with_size,bed_type,floor,room,addon,booking,reviewsRatings,content_management,mongo_backup_restore
from app.middleware.logging_middleware import ActivityLoggingMiddleware
from app.services.scheduler import scheduler

application = FastAPI(
    title="Hotel Booking System",
    description="Secure API with JWT Cookie-based Authentication",
    version="1.0.0"
)

application.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

application.add_middleware(AuthMiddleware)
application.add_middleware(ActivityLoggingMiddleware)

@application.on_event("startup")
def on_startup():
    
    init_db()
    scheduler.start()
    
    
application.mount("/static", StaticFiles(directory="app/static"), name="static")

application.include_router(users.router)
application.include_router(floor.router)
application.include_router(feature.router)
application.include_router(bed_type.router)
application.include_router(room_type_with_size.router)
application.include_router(room.router)
application.include_router(addon.router)
application.include_router(booking.router)
application.include_router(general_contact.router)
application.include_router(booked_contact.router)
application.include_router(content_management.router)
application.include_router(reviewsRatings.router)
application.include_router(postgress_backup_restore.router)
application.include_router(mongo_backup_restore.router)



@application.get("/health", tags=["Root"])
def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "Hotel Booking System"
    }

@application.on_event("shutdown")
def on_shutdown():
    
    scheduler.shutdown()
    print("Shutting down server...")


