from fastapi import APIRouter, HTTPException, Depends, status
from models import User, Notification, NotificationType
from auth import get_current_user
from database import get_database
from bson import ObjectId
from datetime import datetime
from typing import List, Optional
import logging

logger = logging.getLogger(__name__)
router = APIRouter()

@router.get("/", response_model=List[dict])
async def get_notifications(
    current_user: User = Depends(get_current_user),
    limit: int = 20,
    skip: int = 0,
    unread_only: bool = False
):
    """Get user's notifications"""
    database = get_database()
    
    query = {"userId": current_user.id}
    if unread_only:
        query["isRead"] = False
    
    notifications = []
    cursor = database.notifications.find(query).sort("createdAt", -1).skip(skip).limit(limit)
    
    async for notification in cursor:
        notification["id"] = str(notification["_id"])
        del notification["_id"]
        notifications.append(notification)
    
    return notifications

@router.get("/unread-count")
async def get_unread_count(current_user: User = Depends(get_current_user)):
    """Get count of unread notifications"""
    database = get_database()
    
    count = await database.notifications.count_documents({
        "userId": current_user.id,
        "isRead": False
    })
    
    return {"unreadCount": count}

@router.put("/{notification_id}/read")
async def mark_notification_read(
    notification_id: str,
    current_user: User = Depends(get_current_user)
):
    """Mark a notification as read"""
    database = get_database()
    
    if not ObjectId.is_valid(notification_id):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid notification ID"
        )
    
    result = await database.notifications.update_one(
        {
            "_id": ObjectId(notification_id),
            "userId": current_user.id
        },
        {
            "$set": {
                "isRead": True,
                "readAt": datetime.now()
            }
        }
    )
    
    if result.modified_count == 0:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Notification not found"
        )
    
    return {"message": "Notification marked as read"}

@router.put("/mark-all-read")
async def mark_all_notifications_read(current_user: User = Depends(get_current_user)):
    """Mark all notifications as read"""
    database = get_database()
    
    result = await database.notifications.update_many(
        {
            "userId": current_user.id,
            "isRead": False
        },
        {
            "$set": {
                "isRead": True,
                "readAt": datetime.now()
            }
        }
    )
    
    return {
        "message": f"Marked {result.modified_count} notifications as read"
    }

@router.delete("/{notification_id}")
async def delete_notification(
    notification_id: str,
    current_user: User = Depends(get_current_user)
):
    """Delete a notification"""
    database = get_database()
    
    if not ObjectId.is_valid(notification_id):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid notification ID"
        )
    
    result = await database.notifications.delete_one({
        "_id": ObjectId(notification_id),
        "userId": current_user.id
    })
    
    if result.deleted_count == 0:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Notification not found"
        )
    
    return {"message": "Notification deleted successfully"}

@router.delete("/clear-all")
async def clear_all_notifications(current_user: User = Depends(get_current_user)):
    """Clear all notifications for user"""
    database = get_database()
    
    result = await database.notifications.delete_many({
        "userId": current_user.id
    })
    
    return {
        "message": f"Cleared {result.deleted_count} notifications"
    }

@router.get("/broadcast")
async def get_broadcast_notifications(
    limit: int = 10,
    skip: int = 0
):
    """Get broadcast notifications (for all users)"""
    database = get_database()
    
    notifications = []
    cursor = database.notifications.find({
        "userId": None  # Broadcast notifications have null userId
    }).sort("createdAt", -1).skip(skip).limit(limit)
    
    async for notification in cursor:
        notification["id"] = str(notification["_id"])
        del notification["_id"]
        notifications.append(notification)
    
    return notifications

# Admin functions for sending notifications
@router.post("/send-broadcast")
async def send_broadcast_notification(
    title: str,
    message: str,
    notification_type: NotificationType = NotificationType.GENERAL,
    current_user: User = Depends(get_current_user)
):
    """Send broadcast notification to all users (admin only)"""
    # Simple admin check - in production, implement proper role-based access
    if not current_user.userId.startswith("admin"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    
    database = get_database()
    
    notification = {
        "userId": None,  # Null for broadcast notifications
        "title": title,
        "message": message,
        "type": notification_type,
        "isRead": False,
        "createdAt": datetime.now()
    }
    
    result = await database.notifications.insert_one(notification)
    
    return {
        "message": "Broadcast notification sent successfully",
        "notificationId": str(result.inserted_id)
    }

@router.post("/send-user")
async def send_user_notification(
    user_id: str,
    title: str,
    message: str,
    notification_type: NotificationType = NotificationType.GENERAL,
    current_user: User = Depends(get_current_user)
):
    """Send notification to specific user (admin only)"""
    # Simple admin check - in production, implement proper role-based access
    if not current_user.userId.startswith("admin"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    
    database = get_database()
    
    # Check if user exists
    user = await database.users.find_one({
        "$or": [
            {"userId": user_id},
            {"_id": ObjectId(user_id) if ObjectId.is_valid(user_id) else None}
        ]
    })
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    notification = {
        "userId": user["_id"],
        "title": title,
        "message": message,
        "type": notification_type,
        "isRead": False,
        "createdAt": datetime.now()
    }
    
    result = await database.notifications.insert_one(notification)
    
    return {
        "message": "User notification sent successfully",
        "notificationId": str(result.inserted_id),
        "userId": user["userId"]
    }
