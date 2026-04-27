import pytest
from meow.tasks.local.doi.models import AuthorDOI, ContributionDOI, EditorDOI


def make_contribution_doi_minimal(authors=None, editors=None) -> ContributionDOI:
    return ContributionDOI(
        code="MOAPR001",
        title="Test Contribution",
        timezone="Europe/Rome",
        primary_authors=authors or [],
        editors=editors or [],
        doi_identifier="10.18429/JACoW-CONF25-MOAPR001",
        doi_url="https://doi.org/10.18429/JACoW-CONF25-MOAPR001",
        doi_landing_page="https://jacow.org/CONF25/papers/MOAPR001",
        reception_date="",
        revisitation_date="",
        acceptance_date="",
        issuance_date="",
        reception_date_iso="",
        revisitation_date_iso="",
        acceptance_date_iso="",
        issuance_date_iso="",
    )


def test_contribution_doi_creator_name_has_space_after_comma():
    author = AuthorDOI(
        id="jacow-001",
        first_name="Mario",
        last_name="Rossi",
        affiliations={"INFN"},
    )
    doi = make_contribution_doi_minimal(authors=[author])
    attrs = doi._build_doi_attributes()
    assert attrs["creators"][0]["name"] == "Rossi, Mario"


def test_contribution_doi_contributor_name_has_space_after_comma():
    editor = EditorDOI(
        first_name="Anna",
        last_name="Bianchi",
        affiliations={"CERN"},
    )
    doi = make_contribution_doi_minimal(editors=[editor])
    attrs = doi._build_doi_attributes()
    assert attrs["contributors"][0]["name"] == "Bianchi, Anna"
