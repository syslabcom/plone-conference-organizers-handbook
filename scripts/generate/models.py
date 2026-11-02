"""Typed inputs and parsed document records."""

from collections.abc import Callable, Mapping
from dataclasses import dataclass
from pathlib import Path
from typing import Final, Literal, TypeAlias

import yaml
from typing_extensions import override

Kind: TypeAlias = Literal["lesson", "thin", "risk"]
Yaml: TypeAlias = str | int | float | bool | None | list["Yaml"] | dict[str, "Yaml"]


def parse_yaml(content: str, loader: Callable[[str], Yaml] = yaml.safe_load) -> Yaml:
    return loader(content)


@dataclass(frozen=True, slots=True)
class ConventionError(ValueError):
    code: str
    detail: str

    @override
    def __str__(self) -> str:
        return f"{self.code}: {self.detail}"


def mapping(value: Yaml) -> Mapping[str, Yaml]:
    """Parse a YAML mapping at the file boundary."""
    if not isinstance(value, dict):
        raise ConventionError("CONFIG", "expected a YAML mapping")
    return value


def text(value: Yaml) -> str:
    if not isinstance(value, str):
        raise ConventionError("CONFIG", "expected a string")
    return value


def integer(value: Yaml) -> int:
    if type(value) is not int:
        raise ConventionError("CONFIG", "expected an integer")
    return value


def load_yaml(path: Path) -> Mapping[str, Yaml]:
    value = parse_yaml(path.read_text(encoding="utf-8"))
    return mapping(value)


@dataclass(frozen=True, slots=True)
class Config:
    as_of_year: int = 2026
    recent_max: int = 3
    mid_max: int = 8
    source_pattern: str = r"^S[0-9]{3}$"
    ledger_pattern: str = r"^L-[0-9]{4}$"
    chapter_list: str = "docs/spec/chapter-list.yml"

    @classmethod
    def load(cls, root: Path) -> "Config":
        raw = load_yaml(root / "handbook-config.yml")
        ages = mapping(raw["age-thresholds"])
        config = cls(
            as_of_year=integer(raw["as-of-year"]),
            recent_max=integer(ages["recent-max-age"]),
            mid_max=integer(ages["mid-max-age"]),
            source_pattern=text(raw["source-id-pattern"]),
            ledger_pattern=text(raw["ledger-id-pattern"]),
            chapter_list=text(mapping(raw["paths"])["chapter-list"]),
        )
        if not 0 <= config.recent_max < config.mid_max or config.as_of_year < 2000:
            raise ConventionError("CONFIG", "invalid age thresholds or as-of year")
        return config


@dataclass(frozen=True, slots=True)
class Entry:
    id: str
    title: str
    kind: str
    path: str
    status: str


DEFAULT_CONFIG: Final = Config()


def entries(root: Path, config: Config) -> tuple[Entry, ...]:
    raw = load_yaml(root / config.chapter_list)["entries"]
    if not isinstance(raw, list):
        raise ConventionError("CONFIG", "entries must be a list")
    result: list[Entry] = []
    for value in raw:
        row = mapping(value)
        result.append(Entry(*(text(row[key]) for key in ("id", "title", "kind", "path", "status"))))
    return tuple(result)


@dataclass(frozen=True, slots=True)
class Fields:
    kind: Kind
    values: Mapping[str, str]


@dataclass(frozen=True, slots=True)
class Block:
    start: int
    stop: int
    fence: str
    title: str
    classes: tuple[str, ...]
    fields: Fields
    section: str


@dataclass(frozen=True, slots=True)
class Decision:
    level: str
    question: str
    decide_by: str


@dataclass(frozen=True, slots=True)
class Page:
    entry: Entry
    content: str
    maturity: str
    blocks: tuple[Block, ...]
    decisions: tuple[Decision, ...]
