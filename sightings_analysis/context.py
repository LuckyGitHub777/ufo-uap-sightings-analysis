from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class AnalysisContext:
    """Shared dataset identity used by every output layer."""

    dataset_type: str
    dataset_label: str
    short_label: str
    source_description: str
    external_data_used: bool

    @classmethod
    def synthetic_demo(cls) -> "AnalysisContext":
        return cls(
            dataset_type="synthetic",
            dataset_label="Synthetic demonstration",
            short_label="synthetic demonstration",
            source_description="Deterministic synthetic sighting reports",
            external_data_used=False,
        )

    @classmethod
    def user_supplied(cls) -> "AnalysisContext":
        return cls(
            dataset_type="user_supplied",
            dataset_label="User-supplied dataset",
            short_label="user-supplied dataset",
            source_description="User-supplied authorized sighting-report dataset",
            external_data_used=True,
        )
