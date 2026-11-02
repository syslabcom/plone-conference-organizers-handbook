"""Pure badge computation with pinned, configurable age thresholds."""

from collections.abc import Mapping


def age_bucket(age: int, recent_max: int = 3, mid_max: int = 8) -> str:
    if age <= recent_max:
        return "recent"
    if age <= mid_max:
        return "mid"
    return "old"


def lesson_title(f: Mapping[str, str], as_of_year: int, thresholds: tuple[int, int] = (3, 8)) -> str:
    """Return the section 3.3 title, including non-visual age and status signals."""
    match f["scope"]:
        case "general":
            base, suffixes = "[general]", []
        case "specific":
            age = as_of_year - int(f["year"])
            base = f"[specific · {f['year']} · {f['place']} · {age} y]"
            suffixes = ["stale-prone"] if age_bucket(age, *thresholds) == "old" else []
        case _:
            from .models import ConventionError
            raise ConventionError("L01", "invalid scope")
    if f["status"] != "active":
        suffixes.append(f["status"])
    return " ".join([base, *suffixes])


def lesson_classes(f: Mapping[str, str], as_of_year: int, thresholds: tuple[int, int] = (3, 8)) -> set[str]:
    classes = {"hb-lesson", f"hb-{f['scope']}"}
    if f["scope"] == "specific":
        bucket = age_bucket(as_of_year - int(f["year"]), *thresholds)
        classes.add(f"hb-age-{bucket}")
        if bucket == "old":
            classes.add("hb-stale-prone")
    if f["status"] != "active":
        classes.add(f"hb-{f['status']}")
    return classes


def ordered_classes(classes: set[str]) -> str:
    """Stable serialization; class equality itself is set-based."""
    order = ("hb-lesson", "hb-general", "hb-specific", "hb-age-recent", "hb-age-mid", "hb-age-old", "hb-stale-prone")
    return " ".join([token for token in order if token in classes] + sorted(classes - set(order)))
