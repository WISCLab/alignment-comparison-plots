"""
Runtime enforcement of protocol conformance for all exported plot functions.

Dynamically discovers all Protocol classes defined in _types.py and verifies
that every name in __all__ matches at least one of them by parameter signature.
"""

import inspect
from typing import Protocol

import pytest

import alignment_comparison_plots as pkg
import alignment_comparison_plots._types as _types


def _get_protocols() -> list[type]:
    """Return all Protocol classes defined in _types."""
    return [
        obj
        for _, obj in inspect.getmembers(_types, inspect.isclass)
        if obj is not Protocol and Protocol in obj.__mro__
    ]


def _call_params(cls_or_fn) -> set[str]:
    """Parameter names of __call__ (excluding self) or of the function itself."""
    if inspect.isclass(cls_or_fn):
        sig = inspect.signature(cls_or_fn.__call__)
    else:
        sig = inspect.signature(cls_or_fn)
    return {name for name in sig.parameters if name != "self"}


PROTOCOLS = _get_protocols()


PROTOCOL_TYPES = set(_get_protocols())


PLOT_NAMES = [name for name in pkg.__all__ if callable(getattr(pkg, name)) and not inspect.isclass(getattr(pkg, name))]


@pytest.mark.parametrize("name", PLOT_NAMES)
def test_annotated_with_protocol(name: str) -> None:
    annotation = pkg.__annotations__.get(name)
    assert annotation is not None, (
        f"{name} is in __all__ but has no type annotation — "
        f"annotate it with a protocol from _types.py."
    )
    assert annotation in PROTOCOL_TYPES, (
        f"{name} is annotated with {annotation!r} which is not a protocol "
        f"from _types.py. Use one of: {[p.__name__ for p in PROTOCOL_TYPES]}"
    )


@pytest.mark.parametrize("name", PLOT_NAMES)
def test_matches_at_least_one_protocol(name: str) -> None:
    fn = getattr(pkg, name)
    fn_params = _call_params(fn)

    matches = [
        proto for proto in PROTOCOLS
        if _call_params(proto).issubset(fn_params)
    ]

    assert matches, (
        f"{name} does not match any protocol in _types.py.\n"
        f"  Function params: {fn_params}\n"
        f"  Available protocols: {[p.__name__ for p in PROTOCOLS]}"
    )
