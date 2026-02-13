# seed_roles_scopes.py
from app.core.database_postgres import SessionLocal
from app.models.role import Roles
from app.models.scope import Scopes

db = SessionLocal()

DEFAULT_SCOPES = [
    "user:read", "user:write",
    "room:read", "room:write",
    "booking:read", "booking:write",
    "feature:read", "feature:write",
    "floor:read", "floor:write",
    "room_type:read", "room_type:write",
    "addon:read", "addon:write",
    "bed_type:read", "bed_type:write",
    "reschedule:read", "reschedule:write",
    "refund:read", "refund:write",
    "payment:read", "payment:write",
    "reviews_ratings:read", "reviews_ratings:write"
]

try:
    scopes = []
    for s in DEFAULT_SCOPES:
        scope_obj = db.query(Scopes).filter_by(scope_name=s).first()
        if not scope_obj:
            scope_obj = Scopes(scope_name=s)
            db.add(scope_obj)
        scopes.append(scope_obj)

    db.commit() 
    db.refresh(scopes[0])

    admin_role = db.query(Roles).filter_by(role_name="Admin").first()
    user_role = db.query(Roles).filter_by(role_name="User").first()

    if not admin_role:
        admin_role = Roles(role_name="admin")
        admin_role.scope = scopes
        db.add(admin_role)

    if not user_role:
        user_role = Roles(role_name="user")
        user_role.scope = [s for s in scopes if s.scope_name.endswith(":read")]
        db.add(user_role)

    db.commit()
    print("Roles and scopes successfully inserted.")

except Exception as e:
    db.rollback()
    print(f"Error inserting roles/scopes: {e}")

finally:
    db.close()



## run as python -m app.alter_scopes