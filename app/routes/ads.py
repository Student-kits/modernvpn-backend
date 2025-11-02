from fastapi import APIRouter, Depends, Query, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.models import AdEvent
from app.database import get_db
from app.routes.auth import get_current_user
from app.models import User
from typing import Optional, List
import random

router = APIRouter(prefix='/ads')

# Mock advertisement data with country targeting
MOCK_ADS = {
    "IN": [  # India
        {
            "id": 1,
            "title": "Premium VPN Service - India Special",
            "description": "Secure your internet with military-grade encryption. Special discount for Indian users!",
            "link": "https://example.com/vpn-india",
            "payoutRate": "₹120 CPC",
            "category": "vpn",
            "image": "/api/placeholder/300/150"
        },
        {
            "id": 2,
            "title": "Cloud Storage Solution",
            "description": "Store your files safely in Indian data centers with 99.9% uptime guarantee.",
            "link": "https://example.com/storage-in",
            "payoutRate": "₹85 CPC",
            "category": "storage",
            "image": "/api/placeholder/300/150"
        },
        {
            "id": 3,
            "title": "Cybersecurity Course",
            "description": "Learn ethical hacking and cybersecurity. Certificate course in Hindi and English.",
            "link": "https://example.com/course-cyber",
            "payoutRate": "₹200 CPC",
            "category": "education",
            "image": "/api/placeholder/300/150"
        }
    ],
    "US": [  # United States
        {
            "id": 4,
            "title": "Enterprise VPN Solutions",
            "description": "Secure your business with our enterprise-grade VPN infrastructure.",
            "link": "https://example.com/enterprise-vpn",
            "payoutRate": "$4.50 CPC",
            "category": "vpn",
            "image": "/api/placeholder/300/150"
        },
        {
            "id": 5,
            "title": "Privacy Tools Bundle",
            "description": "Complete privacy suite including VPN, password manager, and secure email.",
            "link": "https://example.com/privacy-bundle",
            "payoutRate": "$3.20 CPC",
            "category": "privacy",
            "image": "/api/placeholder/300/150"
        },
        {
            "id": 6,
            "title": "Network Security Certification",
            "description": "Get certified in network security. Industry-recognized credentials.",
            "link": "https://example.com/netsec-cert",
            "payoutRate": "$5.80 CPC",
            "category": "education",
            "image": "/api/placeholder/300/150"
        }
    ],
    "GB": [  # United Kingdom
        {
            "id": 7,
            "title": "UK VPN Service",
            "description": "Access UK content from anywhere. Fast servers in London and Manchester.",
            "link": "https://example.com/uk-vpn",
            "payoutRate": "£2.90 CPC",
            "category": "vpn",
            "image": "/api/placeholder/300/150"
        },
        {
            "id": 8,
            "title": "Data Protection Compliance",
            "description": "GDPR compliance tools for UK businesses. Automated data protection.",
            "link": "https://example.com/gdpr-tools",
            "payoutRate": "£4.10 CPC",
            "category": "compliance",
            "image": "/api/placeholder/300/150"
        }
    ],
    "DE": [  # Germany
        {
            "id": 9,
            "title": "Deutsche VPN Lösung",
            "description": "Sicherer VPN-Service mit Servern in Deutschland. Keine Protokollierung.",
            "link": "https://example.com/vpn-deutschland",
            "payoutRate": "€3.50 CPC",
            "category": "vpn",
            "image": "/api/placeholder/300/150"
        },
        {
            "id": 10,
            "title": "Cyber Security Training",
            "description": "Professional cybersecurity training in German. Industry certification included.",
            "link": "https://example.com/cyber-training-de",
            "payoutRate": "€4.80 CPC",
            "category": "education",
            "image": "/api/placeholder/300/150"
        }
    ],
    "JP": [  # Japan
        {
            "id": 11,
            "title": "日本向けVPNサービス",
            "description": "高速で安全なVPNサービス。日本のサーバーでプライバシーを保護。",
            "link": "https://example.com/vpn-japan",
            "payoutRate": "¥380 CPC",
            "category": "vpn",
            "image": "/api/placeholder/300/150"
        }
    ]
}

@router.get('/')
async def get_ads(
    country: str = Query("IN", description="Country code for targeted ads"),
    category: Optional[str] = Query(None, description="Filter by ad category"),
    limit: int = Query(5, ge=1, le=20, description="Number of ads to return")
):
    """Get advertisements targeted by country and category"""
    try:
        # Get ads for the specified country, fallback to IN (India) if not found
        country_ads = MOCK_ADS.get(country.upper(), MOCK_ADS["IN"])
        
        # Filter by category if specified
        if category:
            country_ads = [ad for ad in country_ads if ad["category"] == category.lower()]
        
        # Shuffle ads for variety and limit results
        ads = random.sample(country_ads, min(len(country_ads), limit))
        
        return {
            "ads": ads,
            "country": country.upper(),
            "total": len(ads),
            "available_categories": list(set(ad["category"] for ad in country_ads))
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch advertisements"
        )

@router.post('/event')
async def track_ad_event(
    payload: dict, 
    db: AsyncSession = Depends(get_db),
    current_user: Optional[User] = Depends(lambda: None)  # Optional authentication
):
    """Track advertisement events (impressions, clicks, conversions)"""
    try:
        # Extract event data
        event_type = payload.get('event_type')
        metadata = payload.get('metadata', {})
        user_id = payload.get('user_id')
        
        # Use authenticated user ID if available
        if current_user:
            user_id = current_user.id
        
        # Validate event type
        valid_events = ['impression', 'click', 'conversion', 'view', 'close']
        if event_type not in valid_events:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid event type. Must be one of: {valid_events}"
            )
        
        # Create ad event record
        ad_event = AdEvent(
            user_id=user_id,
            event_type=event_type,
            metadata=metadata
        )
        
        db.add(ad_event)
        await db.commit()
        await db.refresh(ad_event)
        
        return {
            "success": True,
            "event_id": ad_event.id,
            "message": f"Ad {event_type} tracked successfully"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to track ad event"
        )

@router.get('/stats')
async def get_ad_stats(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get advertisement statistics (admin only)"""
    try:
        if not current_user.is_admin:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Admin access required"
            )
        
        # In a real implementation, you'd query the database for statistics
        stats = {
            "total_impressions": 1250,
            "total_clicks": 89,
            "total_conversions": 12,
            "click_through_rate": 7.12,
            "conversion_rate": 13.48,
            "revenue_generated": 450.75,
            "top_performing_ads": [
                {"id": 1, "title": "Premium VPN Service - India Special", "clicks": 23},
                {"id": 4, "title": "Enterprise VPN Solutions", "clicks": 19},
                {"id": 3, "title": "Cybersecurity Course", "clicks": 15}
            ],
            "performance_by_country": {
                "IN": {"impressions": 580, "clicks": 41},
                "US": {"impressions": 320, "clicks": 28},
                "GB": {"impressions": 180, "clicks": 12},
                "DE": {"impressions": 120, "clicks": 6},
                "JP": {"impressions": 50, "clicks": 2}
            }
        }
        
        return stats
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch ad statistics"
        )