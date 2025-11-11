from fastapi import FastAPI, Depends, HTTPException, status, Query
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Optional
import jwt
import os
from datetime import datetime
import uuid

from config.supabase_config import get_supabase_service_client, SUPABASE_JWT_SECRET, TABLE_NAMES
from schema import (
    SocialPostSchema, CitizenReport, UserProfile, UserRoleEnum,
    ProcessingStatusEnum, SourcePlatformEnum
)

app = FastAPI(
    title="VerisTruth API",
    description="API for the VerisTruth ocean hazard monitoring platform",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure properly for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Security
security = HTTPBearer()

# Dependency to get current user from JWT
async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> dict:
    """
    Validate JWT token and extract user information.
    """
    try:
        token = credentials.credentials
        
        if not SUPABASE_JWT_SECRET:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="JWT secret not configured"
            )
        
        # Decode JWT token
        payload = jwt.decode(token, SUPABASE_JWT_SECRET, algorithms=["HS256"])
        user_id = payload.get("sub")
        user_role = payload.get("user_role", "PUBLIC")
        
        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token"
            )
        
        return {
            "id": user_id,
            "role": user_role
        }
        
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token expired"
        )
    except jwt.InvalidTokenError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token"
        )

# Dependency to get Supabase client
def get_supabase():
    return get_supabase_service_client()

@app.get("/")
async def root():
    """Health check endpoint."""
    return {"message": "VerisTruth API is running", "timestamp": datetime.now()}

# --- User Profile Endpoints ---

@app.get("/api/profile", response_model=UserProfile)
async def get_user_profile(
    current_user: dict = Depends(get_current_user),
    supabase = Depends(get_supabase)
):
    """Get current user's profile."""
    try:
        result = supabase.table(TABLE_NAMES["profiles"]).select("*").eq("id", current_user["id"]).execute()
        
        if not result.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Profile not found"
            )
        
        return UserProfile(**result.data[0])
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error fetching profile: {str(e)}"
        )

@app.put("/api/profile", response_model=UserProfile)
async def update_user_profile(
    full_name: str,
    current_user: dict = Depends(get_current_user),
    supabase = Depends(get_supabase)
):
    """Update current user's profile."""
    try:
        result = supabase.table(TABLE_NAMES["profiles"]).update({
            "full_name": full_name,
            "updated_at": datetime.now().isoformat()
        }).eq("id", current_user["id"]).execute()
        
        if not result.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Profile not found"
            )
        
        return UserProfile(**result.data[0])
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error updating profile: {str(e)}"
        )

# --- Social Posts Endpoints ---

@app.get("/api/social-posts", response_model=List[SocialPostSchema])
async def get_social_posts(
    limit: int = Query(default=50, le=100),
    offset: int = Query(default=0, ge=0),
    platform: Optional[SourcePlatformEnum] = None,
    status: Optional[ProcessingStatusEnum] = None,
    current_user: dict = Depends(get_current_user),
    supabase = Depends(get_supabase)
):
    """Get social media posts with filtering and pagination."""
    try:
        query = supabase.table(TABLE_NAMES["social_posts"]).select("*")
        
        if platform:
            query = query.eq("source_platform", platform.value)
        
        if status:
            query = query.eq("status", status.value)
        
        result = query.order("posted_at", desc=True).range(offset, offset + limit - 1).execute()
        
        posts = []
        for row in result.data:
            # Convert database row to Pydantic model
            posts.append(SocialPostSchema(
                id=row["id"],
                source_platform=SourcePlatformEnum(row["source_platform"]),
                original_id=row["original_id"],
                post_url=row["post_url"],
                author_id=row["author_id"],
                content_text=row["content_text"],
                posted_at=datetime.fromisoformat(row["posted_at"]),
                media_urls=row["media_urls"] or [],
                raw_data=row["raw_data"] or {},
                status=ProcessingStatusEnum(row["status"]),
                geocoded_location=row["geocoded_location"],
                nlp_analysis=row["nlp_analysis"],
                image_analysis=row["image_analysis"],
                created_at=datetime.fromisoformat(row["created_at"])
            ))
        
        return posts
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error fetching social posts: {str(e)}"
        )

@app.get("/api/social-posts/{post_id}", response_model=SocialPostSchema)
async def get_social_post(
    post_id: str,
    current_user: dict = Depends(get_current_user),
    supabase = Depends(get_supabase)
):
    """Get a specific social media post."""
    try:
        result = supabase.table(TABLE_NAMES["social_posts"]).select("*").eq("id", post_id).execute()
        
        if not result.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Social post not found"
            )
        
        row = result.data[0]
        return SocialPostSchema(
            id=row["id"],
            source_platform=SourcePlatformEnum(row["source_platform"]),
            original_id=row["original_id"],
            post_url=row["post_url"],
            author_id=row["author_id"],
            content_text=row["content_text"],
            posted_at=datetime.fromisoformat(row["posted_at"]),
            media_urls=row["media_urls"] or [],
            raw_data=row["raw_data"] or {},
            status=ProcessingStatusEnum(row["status"]),
            geocoded_location=row["geocoded_location"],
            nlp_analysis=row["nlp_analysis"],
            image_analysis=row["image_analysis"],
            created_at=datetime.fromisoformat(row["created_at"])
        )
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid data format: {str(e)}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error fetching social post: {str(e)}"
        )

@app.put("/api/social-posts/{post_id}/status")
async def update_post_status(
    post_id: str,
    new_status: ProcessingStatusEnum,
    current_user: dict = Depends(get_current_user),
    supabase = Depends(get_supabase)
):
    """Update the processing status of a social media post (OFFICIAL role required)."""
    # Check if user has OFFICIAL role
    if current_user["role"] != UserRoleEnum.OFFICIAL.value:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only OFFICIAL users can update post status"
        )
    
    try:
        result = supabase.table(TABLE_NAMES["social_posts"]).update({
            "status": new_status.value
        }).eq("id", post_id).execute()
        
        if not result.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Social post not found"
            )
        
        return {"message": "Post status updated successfully", "new_status": new_status.value}
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error updating post status: {str(e)}"
        )

# --- Citizen Reports Endpoints ---

@app.get("/api/citizen-reports", response_model=List[CitizenReport])
async def get_citizen_reports(
    limit: int = Query(default=50, le=100),
    offset: int = Query(default=0, ge=0),
    current_user: dict = Depends(get_current_user),
    supabase = Depends(get_supabase)
):
    """Get citizen reports for the current user."""
    try:
        result = supabase.table(TABLE_NAMES["citizen_reports"]).select("*").eq(
            "user_id", current_user["id"]
        ).order("created_at", desc=True).range(offset, offset + limit - 1).execute()
        
        reports = []
        for row in result.data:
            reports.append(CitizenReport(
                id=row["id"],
                user_id=row["user_id"],
                title=row["title"],
                description=row["description"],
                location=row["location"],
                media_urls=row["media_urls"] or [],
                status=row["status"],
                created_at=datetime.fromisoformat(row["created_at"]),
                updated_at=datetime.fromisoformat(row["updated_at"])
            ))
        
        return reports
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error fetching citizen reports: {str(e)}"
        )

@app.post("/api/citizen-reports", response_model=CitizenReport)
async def create_citizen_report(
    title: str,
    description: str,
    location: Optional[dict] = None,
    media_urls: Optional[List[str]] = None,
    current_user: dict = Depends(get_current_user),
    supabase = Depends(get_supabase)
):
    """Create a new citizen report."""
    try:
        report_data = {
            "id": str(uuid.uuid4()),
            "user_id": current_user["id"],
            "title": title,
            "description": description,
            "location": location,
            "media_urls": media_urls or [],
            "status": "PENDING",
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat()
        }
        
        result = supabase.table(TABLE_NAMES["citizen_reports"]).insert(report_data).execute()
        
        if not result.data:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to create citizen report"
            )
        
        row = result.data[0]
        return CitizenReport(
            id=row["id"],
            user_id=row["user_id"],
            title=row["title"],
            description=row["description"],
            location=row["location"],
            media_urls=row["media_urls"] or [],
            status=row["status"],
            created_at=datetime.fromisoformat(row["created_at"]),
            updated_at=datetime.fromisoformat(row["updated_at"])
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error creating citizen report: {str(e)}"
        )

# --- Statistics Endpoints ---

@app.get("/api/stats/overview")
async def get_overview_stats(
    current_user: dict = Depends(get_current_user),
    supabase = Depends(get_supabase)
):
    """Get overview statistics."""
    try:
        # Get total social posts count
        social_posts_result = supabase.table(TABLE_NAMES["social_posts"]).select("id", count="exact").execute()
        total_social_posts = social_posts_result.count
        
        # Get citizen reports count for current user
        user_reports_result = supabase.table(TABLE_NAMES["citizen_reports"]).select(
            "id", count="exact"
        ).eq("user_id", current_user["id"]).execute()
        user_reports = user_reports_result.count
        
        # Get posts by platform
        platform_stats = {}
        for platform in SourcePlatformEnum:
            platform_result = supabase.table(TABLE_NAMES["social_posts"]).select(
                "id", count="exact"
            ).eq("source_platform", platform.value).execute()
            platform_stats[platform.value] = platform_result.count
        
        return {
            "total_social_posts": total_social_posts,
            "user_citizen_reports": user_reports,
            "posts_by_platform": platform_stats,
            "last_updated": datetime.now().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error fetching statistics: {str(e)}"
        )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)