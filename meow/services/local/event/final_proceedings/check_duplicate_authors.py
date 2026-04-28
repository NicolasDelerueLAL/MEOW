import logging as lg
from collections import defaultdict

from meow.models.local.event.final_proceedings.proceedings_data_model import ProceedingsData

logger = lg.getLogger(__name__)


async def check_duplicate_authors(proceedings_data: ProceedingsData) -> list[str]:
    """Detect authors with the same normalized name but different emails, or with no email."""

    logger.info("event_final_proceedings - check_duplicate_authors")

    name_to_emails: dict[str, set[str]] = defaultdict(set)
    name_to_contributions: dict[str, set[str]] = defaultdict(set)

    for contribution in proceedings_data.contributions:
        for author in contribution.authors:
            if not author:
                continue
            name_key = f"{author.last.strip().lower()}, {author.first.strip().lower()}"
            name_to_emails[name_key].add(author.email)
            name_to_contributions[name_key].add(contribution.code)

    warnings: list[str] = []

    for name_key, emails in name_to_emails.items():
        contributions_str = ", ".join(sorted(name_to_contributions[name_key]))

        if "" in emails:
            missing_msg = (
                f"Author with missing email: '{name_key}' "
                f"in contributions: {contributions_str}. "
                f"A fallback ID (name+affiliation) has been used."
            )
            warnings.append(missing_msg)

        non_empty_emails = emails - {""}
        if len(non_empty_emails) > 1:
            emails_str = ", ".join(sorted(non_empty_emails))
            duplicate_msg = (
                f"Duplicate author: '{name_key}' "
                f"has multiple emails [{emails_str}] "
                f"in contributions: {contributions_str}."
            )
            warnings.append(duplicate_msg)

    logger.warning(f"check_duplicate_authors: {len(warnings)} warning(s) found.")
    for w in warnings:
        logger.warning(w)

    return warnings
