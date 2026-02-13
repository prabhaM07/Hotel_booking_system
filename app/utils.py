from bson import ObjectId
from datetime import datetime

from requests import Session

from app.models.role import Roles
from app.models.token_store import TokenStore

def convertTOString(object_id: ObjectId) -> str:
    return str(object_id)
  
def formatDatetime(date : datetime):
    if(date):
        return date.isoformat()
    return None

def get_role(db: Session,role_id :int):
    role = db.query(Roles).filter(Roles.id == role_id).first()
    return role.role_name


def cleanup_expired_tokens(db: Session):
    now = datetime.now()
    db.query(TokenStore).filter(
        (TokenStore.access_token_expiry <= now) | (TokenStore.refresh_token_expiry <= now)
    ).delete(synchronize_session=False)
    db.commit()
