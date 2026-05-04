import re
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


def test_contribution_doi_creator_affiliations_are_individual_objects():
    author = AuthorDOI(
        id="jacow-001",
        first_name="Mario",
        last_name="Rossi",
        affiliations={"INFN", "CERN"},
    )
    doi = make_contribution_doi_minimal(authors=[author])
    attrs = doi._build_doi_attributes()
    affiliations = attrs["creators"][0]["affiliation"]
    assert isinstance(affiliations, list)
    assert len(affiliations) == 2
    for aff in affiliations:
        assert isinstance(aff, dict)
        assert isinstance(aff["name"], str)


def test_contribution_doi_contributor_affiliations_are_individual_objects():
    editor = EditorDOI(
        first_name="Anna",
        last_name="Bianchi",
        affiliations={"PSI", "DESY"},
    )
    doi = make_contribution_doi_minimal(editors=[editor])
    attrs = doi._build_doi_attributes()
    affiliations = attrs["contributors"][0]["affiliation"]
    assert isinstance(affiliations, list)
    assert len(affiliations) == 2
    for aff in affiliations:
        assert isinstance(aff, dict)
        assert isinstance(aff["name"], str)


def test_contribution_doi_creator_has_name_type_personal():
    author = AuthorDOI(
        id="jacow-001",
        first_name="Mario",
        last_name="Rossi",
        affiliations={"INFN"},
    )
    doi = make_contribution_doi_minimal(authors=[author])
    attrs = doi._build_doi_attributes()
    assert attrs["creators"][0]["nameType"] == "Personal"


def test_contribution_doi_contributor_has_name_type_personal():
    editor = EditorDOI(
        first_name="Anna",
        last_name="Bianchi",
        affiliations={"CERN"},
    )
    doi = make_contribution_doi_minimal(editors=[editor])
    attrs = doi._build_doi_attributes()
    assert attrs["contributors"][0]["nameType"] == "Personal"


def test_contribution_doi_dates_are_iso_format():
    doi = make_contribution_doi_minimal()
    doi.reception_date_iso = "2026-01-15"
    doi.revisitation_date_iso = "2026-02-10"
    doi.acceptance_date_iso = "2026-02-20"
    doi.issuance_date_iso = "2026-03-01"
    attrs = doi._build_doi_attributes()
    iso_pattern = re.compile(r"^\d{4}-\d{2}-\d{2}$")
    for date_entry in attrs["dates"]:
        if date_entry["date"]:
            assert iso_pattern.match(date_entry["date"]), (
                f"Date '{date_entry['date']}' (type={date_entry['dateType']}) "
                f"is not in YYYY-MM-DD format"
            )
