from loguru import logger

from src.models.route import Route
from src.modules.story_badge.claimer import Story


async def process_claim_badge(route: Route) -> bool:
    story = Story(
        private_key=route.wallet.private_key,
        proxy=route.wallet.proxy
    )
    logger.debug(story)

    claimed = await story.claim_badge()
    if claimed:
        return True
