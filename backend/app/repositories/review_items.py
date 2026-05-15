from app.models.review_item import ReviewItem
from app.repositories.base import BaseRepository


class ReviewItemRepository(BaseRepository[ReviewItem]):
    model = ReviewItem
