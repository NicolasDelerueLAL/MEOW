import logging as lg
from typing import Callable

from anyio import Path

from meow.models.local.event.final_proceedings.proceedings_data_model import (
    ProceedingsConfig,
    ProceedingsData,
)
from meow.services.local.event.final_proceedings.event_pdf_utils import (
    pdf_optimize_pymupdf,
)

logger = lg.getLogger(__name__)


async def optimize_proceedings_pdfs(
    proceedings_data: ProceedingsData,
    cookies: dict,
    settings: dict,
    config: ProceedingsConfig,
    callback: Callable,
) -> tuple[ProceedingsData, list[str]]:
    logger.info("event_final_proceedings - optimize_proceedings_pdfs")

    event_id = proceedings_data.event.id
    cache_dir = Path("var", "run", f"{event_id}_tmp")
    client_logs: list[str] = []

    for pdf_name, label, size_attr in [
        (f"{event_id}_proceedings_brief.pdf", "Proceedings at a Glance", "proceedings_brief_size"),
        (f"{event_id}_proceedings_volume.pdf", "Proceedings Volume", "proceedings_volume_size"),
    ]:
        src = Path(cache_dir, pdf_name)
        tmp = Path(cache_dir, f"{pdf_name}.opt.pdf")

        if not await src.exists():
            continue

        try:
            size_before = (await src.stat()).st_size
            logger.info(f"{label} [{pdf_name}] before: {size_before:,} bytes ({size_before / 1_000_000:.2f} MB)")

            if await pdf_optimize_pymupdf(str(src), str(tmp)) != 0:
                raise BaseException(f"Error optimizing {pdf_name}")

            await src.unlink()
            await tmp.rename(src)

            size_after = (await src.stat()).st_size
            reduction = (1 - size_after / size_before) * 100
            logger.info(f"{label} [{pdf_name}] after:  {size_after:,} bytes ({size_after / 1_000_000:.2f} MB) — reduction: {reduction:.1f}%")

            setattr(proceedings_data, size_attr, size_after)
            client_logs.append(f"{label}: {size_before / 1_000_000:.2f} MB → {size_after / 1_000_000:.2f} MB ({reduction:.1f}% reduction)")
        except BaseException as be:
            logger.error(be, exc_info=True)
            await tmp.unlink(missing_ok=True)

    return proceedings_data, client_logs
