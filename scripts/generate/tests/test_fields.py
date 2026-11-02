from dataclasses import replace
from pathlib import Path

import pytest

from scripts.generate.documents import parse_blocks
from scripts.generate.fields import parse_field_line
from scripts.generate.lessons import age_bucket, lesson_classes, lesson_title
from scripts.generate.models import Config, ConventionError, mapping, parse_yaml, text

FIXTURES = Path(__file__).resolve().parents[1] / "fixtures"
RAW = parse_yaml((FIXTURES / "invalid-fields.yml").read_text())
assert isinstance(RAW, list)
CASES = tuple((text(mapping(row)["name"]), text(mapping(row)["line"]), text(mapping(row)["code"])) for row in RAW)


@pytest.mark.parametrize(("name", "line", "code"), CASES, ids=[case[0] for case in CASES])
def test_rejects_invalid_fields_when_contract_is_broken(name: str, line: str, code: str) -> None:
    # Given an invalid field-line fixture.
    # When parsing the field line.
    with pytest.raises(ConventionError) as caught:
        _ = parse_field_line(line)
    # Then the stable rule code identifies the violation.
    assert caught.value.code == code, name


def test_marks_lesson_old_when_age_exceeds_eight_years() -> None:
    # Given an old specific lesson.
    fields = parse_blocks((FIXTURES / "chapter.md").read_text())[1].fields.values
    # When computing its badge and classes against the pinned year.
    title, classes = lesson_title(fields, 2026), lesson_classes(fields, 2026)
    # Then both the visible badge and styling hooks carry its age.
    assert title == "[specific · 2012 · Arnhem · 14 y] stale-prone"
    assert classes == {"hb-lesson", "hb-specific", "hb-age-old", "hb-stale-prone"}


@pytest.mark.parametrize(("age", "bucket"), [(0, "recent"), (3, "recent"), (4, "mid"), (8, "mid"), (9, "old")])
def test_buckets_age_when_at_threshold(age: int, bucket: str) -> None:
    # Given the specified default thresholds.
    # When computing a boundary age.
    result = age_bucket(age)
    # Then inclusive threshold edges fall in the intended bucket.
    assert result == bucket


def test_uses_custom_thresholds_when_config_changes() -> None:
    # Given an age of fourteen with a mid threshold of fifteen.
    fields = parse_blocks((FIXTURES / "chapter.md").read_text())[1].fields.values
    config = replace(Config(), recent_max=5, mid_max=15)
    # When computing with the configured thresholds.
    classes = lesson_classes(fields, config.as_of_year, (config.recent_max, config.mid_max))
    # Then the default old threshold is not used.
    assert classes == {"hb-lesson", "hb-specific", "hb-age-mid"}


def test_rejects_mismatched_kind_when_class_implies_thin() -> None:
    # Given a valid risk line with a thin class context.
    line = "risk | likelihood: low | impact: high | mitigation: Prepare a fallback."
    # When parsing with the class-implied kind.
    with pytest.raises(ConventionError) as caught:
        _ = parse_field_line(line, implied_kind="thin")
    # Then the mismatch is rejected independently of field validity.
    assert caught.value.code == "B02"


def test_ignores_example_when_inside_outer_fence() -> None:
    # Given managed examples nested in backtick, tilde and colon fences.
    example = (FIXTURES / "chapter.md").read_text()
    wrapped = "\n".join(f"{fence}markdown\n{example}\n{fence}" for fence in ("````", "~~~~", "::::"))
    # When scanning the document.
    blocks = parse_blocks(wrapped)
    # Then no example becomes a managed block.
    assert blocks == ()


@pytest.mark.parametrize(("replacement", "code"), [(":::note", "B06"), ("```{warning}", "B03")])
def test_rejects_invalid_directive_when_managed(replacement: str, code: str) -> None:
    # Given a managed lesson with an incorrect opening.
    content = (FIXTURES / "chapter.md").read_text()
    if replacement == ":::note":
        content = content.replace("```{note} [general]", ":::{note} [general]", 1).replace("\n```\n", "\n:::\n", 1)
    else:
        content = content.replace("```{note}", replacement, 1)
    # When scanning the document.
    with pytest.raises(ConventionError) as caught:
        _ = parse_blocks(content)
    # Then stock directive and fence constraints are enforced.
    assert caught.value.code == code
