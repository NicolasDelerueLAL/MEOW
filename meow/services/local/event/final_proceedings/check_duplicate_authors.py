import logging as lg
from collections import defaultdict

from meow.models.local.event.final_proceedings.proceedings_data_model import ProceedingsData

logger = lg.getLogger(__name__)


async def check_duplicate_authors(proceedings_data: ProceedingsData) -> list[str]:
    """Detect authors with the same normalized name but different Indico IDs."""

    logger.info("event_final_proceedings - check_duplicate_authors")

    name_to_ids: dict[str, set[str]] = defaultdict(set)
    name_to_contributions: dict[str, set[str]] = defaultdict(set)

    for contribution in proceedings_data.contributions:
        for author in contribution.authors:
            if not author:
                continue
            name_key = f"{author.last.strip().lower()}, {author.first.strip().lower()}"
            name_to_ids[name_key].add(author.id)
            name_to_contributions[name_key].add(contribution.code)

    warnings: list[str] = []

    for name_key, ids in name_to_ids.items():
        if len(ids) > 1:
            ids_str = ", ".join(sorted(ids))
            contributions_str = ", ".join(sorted(name_to_contributions[name_key]))
            warnings.append(
                f"Duplicate author: '{name_key}' "
                f"has multiple Indico IDs [{ids_str}] "
                f"in contributions: {contributions_str}."
            )

    logger.warning(f"check_duplicate_authors: {len(warnings)} duplicate(s) found.")
    for w in warnings:
        logger.warning(w)

    return warnings
