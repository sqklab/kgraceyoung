from fastapi import APIRouter

router = APIRouter(prefix="/reels", tags=["reels"])

@router.get("/feed")
def reels_feed():
    return {
        "items": [
            {
                "id": "demo-cica-routine",
                "title": "Cica routine for acne marks",
                "thumbnail": "/placeholder-reel.jpg",
                "products": ["Cica Serum", "Daily SPF"],
            },
            {
                "id": "demo-led-device",
                "title": "LED mask glow routine",
                "thumbnail": "/placeholder-reel.jpg",
                "products": ["LED Mask", "Ginseng Serum"],
            },
        ]
    }
