import logging as lg
from typing import Callable

from anyio import Path, create_task_group

from meow.models.local.event.final_proceedings.contribution_model import (
    ContributionData,
    ContributionPosterData,
    FileData,
)
from meow.models.local.event.final_proceedings.proceedings_data_utils import (
    extract_contributions_posters,
)

from meow.models.local.event.final_proceedings.proceedings_data_model import (
    ProceedingsData,
)
from meow.models.local.event.final_proceedings.session_model import SessionData
from meow.services.local.event.final_proceedings.event_pdf_utils import (
    draw_frame_anyio,
    pdf_linearize_qpdf,
    pdf_metadata_qpdf,
)
from meow.services.local.event.final_proceedings.write_metadata_utils import (
    get_metadata_pikepdf,
    get_side_data,
    get_xml_metatdata_pikepdf,
)
from meow.services.local.event.final_proceedings.write_metadata_utils import (
    get_footer_data,
    get_header_data,
)


logger = lg.getLogger(__name__)


async def write_posters_metadata(
    proceedings_data: ProceedingsData, cookies: dict, settings: dict, callback: Callable
) -> ProceedingsData:
    """ """

    logger.info("event_final_proceedings - write_posters_metadata")

    posters_data: list[ContributionPosterData] = await extract_contributions_posters(
        proceedings_data,
        callback,
    )

    total_files: int = len(posters_data)

    logger.info(f"write_posters_metadata - files: {total_files}")

    dir_name = f"{proceedings_data.event.id}_tmp"
    pdf_cache_dir: Path = Path("var", "run", dir_name)
    await pdf_cache_dir.mkdir(exist_ok=True, parents=True)

    sessions_dict: dict[int, SessionData] = dict()
    for session in proceedings_data.sessions:
        sessions_dict[session.id] = session

    async with create_task_group() as tg:
        for current_poster in posters_data:
            tg.start_soon(
                write_metadata_task,
                proceedings_data,
                current_poster,
                sessions_dict,
                settings,
                pdf_cache_dir,
            )

    # with start_blocking_portal() as portal:
    #     futures = [
    #         portal.start_task_soon(write_metadata_task,
    #                                current_slide, sessions_dict,
    #                                settings, pdf_cache_dir)
    #         for current_slide in slides_data
    #     ]
    #
    #     for future in as_completed(futures):
    #         pass

    return proceedings_data


async def write_metadata_task(
    proceedings_data,
    current_poster: ContributionPosterData,
    sessions,
    settings,
    pdf_cache_dir,
):
    current_file: FileData = current_poster.poster

    contribution: ContributionData = current_poster.contribution

    logger.info(f"contribution.session_id={contribution.session_id}")

    session = sessions.get(contribution.session_id)

    logger.info(f"contribution.session_id={contribution.session_id}")

    original_pdf_name = f"{current_file.filename}"
    original_pdf_file = Path(pdf_cache_dir, original_pdf_name)

    jacow_pdf_name = f"{current_file.filename}_jacow"
    jacow_pdf_file = Path(pdf_cache_dir, jacow_pdf_name)

    await jacow_pdf_file.unlink(missing_ok=True)

    logger.info(f"{original_pdf_file} --> {jacow_pdf_file} {session}")

    if not session:
        logger.warning(
            f"{original_pdf_file} --> {jacow_pdf_file} -> EXIT session not found"
        )
        return None

    logger.info(f"{original_pdf_file} --> {jacow_pdf_file}")

    header_data: dict | None = get_header_data(contribution)
    footer_data: dict | None = get_footer_data(contribution, session)
    side_data: dict = await get_side_data(settings, pdf_cache_dir)

    # metadata_mutool = get_metadata_mutool(contribution)
    metadata_pikepdf: dict | None = get_metadata_pikepdf(contribution)

    # xml_metadata_mutool = get_xml_metatdata_mutool(contribution)
    xml_metadata_pikepdf: dict | None = get_xml_metatdata_pikepdf(contribution)

    pre_print: str = (
        settings.get("pre_print", "This is a preprint")
        if contribution.peer_reviewing_accepted
        else ""
    )

    await draw_frame_anyio(
        str(original_pdf_file),
        str(jacow_pdf_file),
        contribution.page,
        pre_print,
        header_data,
        footer_data,
        side_data,
        None,
        None,
        True,
    )

    await pdf_metadata_qpdf(str(jacow_pdf_file), metadata_pikepdf, xml_metadata_pikepdf)

    # await pdf_linearize_qpdf(str(original_pdf_file), str(jacow_pdf_file), None, None)
