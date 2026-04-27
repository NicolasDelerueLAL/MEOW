import pytest
from meow.models.local.event.final_proceedings.event_model import PersonData


def make_editor(first: str, last: str, affiliations: set) -> PersonData:
    p = PersonData.__new__(PersonData)
    p.first = first
    p.last = last
    p.affiliations = affiliations
    return p


def test_conference_doi_creator_name_has_space_after_comma():
    editor = make_editor("Mario", "Rossi", {"INFN"})
    name = f"{editor.last}, {editor.first}"
    assert name == "Rossi, Mario"


def test_conference_doi_contributor_name_has_space_after_comma():
    editor = make_editor("Anna", "Bianchi", {"CERN"})
    name = f"{editor.last}, {editor.first}"
    assert name == "Bianchi, Anna"
