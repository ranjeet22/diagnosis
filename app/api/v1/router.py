from fastapi import APIRouter
from app.api.v1.endpoints import datasets, profiles, semantic, plan, analytics, visualization, dashboard, insights, chat

router = APIRouter()

# Include datasets, profiles, semantic, plan, analytics, visualization, dashboard, and insights endpoints under '/datasets' prefix
router.include_router(datasets.router, prefix="/datasets", tags=["Datasets"])
router.include_router(profiles.router, prefix="/datasets", tags=["Profiles"])
router.include_router(semantic.router, prefix="/datasets", tags=["Semantic"])
router.include_router(plan.router, prefix="/datasets", tags=["Plan"])
router.include_router(analytics.router, prefix="/datasets", tags=["Analytics"])
router.include_router(visualization.router, prefix="/datasets", tags=["Visualization"])
router.include_router(dashboard.router, prefix="/datasets", tags=["Dashboard"])
router.include_router(insights.router, prefix="/datasets", tags=["Insights"])

# Include conversational chat endpoints under '/chat' prefix
router.include_router(chat.router, prefix="/chat", tags=["Chat"])
