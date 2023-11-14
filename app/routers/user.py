from fastapi import FastAPI, Response, status, HTTPException, Depends, APIRouter
from sqlalchemy.orm import Session
from .. import models, schemas, utils
from ..database import engine, get_db
from typing import List

router = APIRouter(
    prefix="/users",
    tags=["Users"]
)

#Get a single user
@router.get("/{user_id}",response_model=schemas.UserOut)
def get_user(user_id: int, response: Response,db: Session = Depends(get_db)):

    user = db.query(models.User).filter(models.User.user_id == user_id).first()

    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
         detail=f"User with id {user_id} not found")


    return user



#Create new user
@router.post("/", status_code=status.HTTP_201_CREATED, response_model=schemas.UserOut)
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):

    #hash the password
    hashed_password = utils.hash(user.password)
    user.password = hashed_password

    new_user = models.User(email=user.email,password = user.password)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)


    return new_user
