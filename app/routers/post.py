from fastapi import FastAPI, Response, status, HTTPException, Depends, APIRouter
from sqlalchemy.orm import Session
from typing import List, Optional
from .. import models, schemas, utils, oauth2
from ..database import engine, get_db


router = APIRouter(
    prefix="/posts",
    tags=["Posts"]
)


#Get all the posts
@router.get("/", response_model=List[schemas.Post])
def get_posts(db: Session = Depends(get_db),  current_user:int = Depends(oauth2.get_current_user), limit: int = 10, skip: int = 0, search: Optional[str] = "" ):
    
    
    posts = db.query(models.Post).filter(models.Post.title.contains(search)).limit(limit).offset(skip).all()
    return posts
    
    return {"Data": posts}

#Get single post
@router.get("/{id}", response_model=schemas.Post)
def get_post(id: int, response: Response,db: Session = Depends(get_db),  current_user:int = Depends(oauth2.get_current_user)):

    post = db.query(models.Post).filter(models.Post.id == id).first()

    if not post:
         raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="NOT FOUND")
   
    return post


#Create Posts
@router.post("/", status_code=status.HTTP_201_CREATED, response_model=schemas.Post)
def create_posts(post: schemas.PostCreate, db: Session = Depends(get_db), current_user:int = Depends(oauth2.get_current_user)):

    new_post = models.Post(title=post.title, content=post.content, published=post.published, owner_id=current_user.user_id)
    db.add(new_post)
    db.commit()
    db.refresh(new_post)

    return new_post

#Delete a post
@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_post(id: int, db: Session = Depends(get_db),  current_user:int = Depends(oauth2.get_current_user)):

    post = db.query(models.Post).filter(models.Post.id == id)

    if not post.first():
         raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
          detail= f"User with id {id} not found")

    if post.owner_id != current_user.user_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=
        "Not authorized to perform this action")


    post.delete(synchronize_session=False)
    db.commit()

    return Response(status_code=status.HTTP_204_NO_CONTENT)
    
#Update a post
@router.put("/{id}")
def update_post(id: int, post: schemas.PostCreate, db: Session = Depends(get_db),  current_user:int = Depends(oauth2.get_current_user)):
    
    post_query = db.query(models.Post).filter(models.Post.id == id)
    update_post = post_query.first()

    if update_post == None:
         raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
          detail= f"User with id {id} not found")

    
    if post.owner_id != current_user.user_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=
        "Not authorized to perform this action")

    post_query.update(post.dict(),synchronize_session=False)
    db.commit()

    return {"Message": post}

