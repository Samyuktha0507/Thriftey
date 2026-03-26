"""Community Forum Router — Posts, replies, cross-user interaction."""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import datetime
from pydantic import BaseModel
from typing import Optional
import models, database
from routers.dependencies import get_current_business

router = APIRouter(prefix="/community", tags=["community"])

class PostCreate(BaseModel):
    title: str
    content: str
    category: str

class ReplyCreate(BaseModel):
    content: str

@router.get("/posts")
def get_posts(category: Optional[str] = None, business: models.Business = Depends(get_current_business), db: Session = Depends(database.get_db)):
    query = db.query(models.ForumPost)
    if category:
        query = query.filter(models.ForumPost.category == category)
    posts = query.order_by(models.ForumPost.created_at.desc()).limit(30).all()

    results = []
    for p in posts:
        biz = db.query(models.Business).filter(models.Business.id == p.business_id).first()
        reply_count = db.query(models.ForumReply).filter(models.ForumReply.post_id == p.id).count()
        results.append({
            "id": p.id, "title": p.title, "content": p.content, "category": p.category,
            "business_name": biz.name if biz else "Unknown",
            "is_own": p.business_id == business.id,
            "created_at": p.created_at.isoformat() if p.created_at else None,
            "reply_count": reply_count,
        })
    return results

@router.post("/posts")
def create_post(request: PostCreate, business: models.Business = Depends(get_current_business), db: Session = Depends(database.get_db)):
    post = models.ForumPost(
        business_id=business.id, title=request.title,
        content=request.content, category=request.category,
        created_at=datetime.utcnow(),
    )
    db.add(post)
    db.commit()
    db.refresh(post)
    return {"message": "Post created", "post_id": post.id}

@router.get("/posts/{post_id}")
def get_post(post_id: int, business: models.Business = Depends(get_current_business), db: Session = Depends(database.get_db)):
    post = db.query(models.ForumPost).filter(models.ForumPost.id == post_id).first()
    if not post:
        raise HTTPException(status_code=404, detail={"error": "not_found", "message": "Post not found"})
    biz = db.query(models.Business).filter(models.Business.id == post.business_id).first()
    replies = db.query(models.ForumReply).filter(models.ForumReply.post_id == post_id).order_by(models.ForumReply.created_at.asc()).all()
    reply_list = []
    for r in replies:
        rbiz = db.query(models.Business).filter(models.Business.id == r.business_id).first()
        reply_list.append({
            "id": r.id, "content": r.content,
            "business_name": rbiz.name if rbiz else "Unknown",
            "is_own": r.business_id == business.id,
            "created_at": r.created_at.isoformat() if r.created_at else None,
        })
    return {
        "id": post.id, "title": post.title, "content": post.content,
        "category": post.category,
        "business_name": biz.name if biz else "Unknown",
        "is_own": post.business_id == business.id,
        "created_at": post.created_at.isoformat() if post.created_at else None,
        "replies": reply_list,
    }

@router.post("/posts/{post_id}/reply")
def reply_to_post(post_id: int, request: ReplyCreate, business: models.Business = Depends(get_current_business), db: Session = Depends(database.get_db)):
    post = db.query(models.ForumPost).filter(models.ForumPost.id == post_id).first()
    if not post:
        raise HTTPException(status_code=404, detail={"error": "not_found", "message": "Post not found"})
    reply = models.ForumReply(
        post_id=post_id, business_id=business.id,
        content=request.content, created_at=datetime.utcnow(),
    )
    db.add(reply)
    db.commit()
    db.refresh(reply)
    return {"message": "Reply posted", "reply_id": reply.id}
