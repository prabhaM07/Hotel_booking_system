from fastapi import APIRouter,Request,Depends
from sqlalchemy.orm import Session
from typing import List
from app.auth.auth_utils import require_scope
from app.schemas.general_query_schema import GeneralQueryResponseSchema,UserQuerySchema
from app.crud import generalQuery
from app.core.dependency import get_db


router = APIRouter(prefix="/General/Query", tags=["Contact By General User"])

@router.post("/create", response_model=UserQuerySchema)
async def create_query(query: UserQuerySchema,request: Request,db: Session = Depends(get_db)):
    result = await generalQuery.create_query(query,request,db)
    return result

@router.put("/response", response_model=UserQuerySchema)
@require_scope(["user:write"])
async def respond_query(request : Request,query_id: str, response: GeneralQueryResponseSchema):
    result = await generalQuery.respond_query(query_id,response)
    return result

@router.get("/get", response_model=List[UserQuerySchema])
@require_scope(["user:write"])
async def get_all_queries(request : Request):
    result = await generalQuery.get_all_queries()
    return result