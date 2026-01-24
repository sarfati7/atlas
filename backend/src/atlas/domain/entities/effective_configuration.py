"""EffectiveConfiguration - Computed configuration with source breakdown."""

from dataclasses import dataclass


@dataclass
class EffectiveConfiguration:
    """
    Computed effective configuration with source breakdown.

    Represents the merged configuration from org -> team -> user levels,
    with individual components tracked for transparency.
    """

    content: str  # Final merged configuration
    org_content: str  # Content from org level (empty if none)
    team_content: str  # Combined content from team level(s)
    user_content: str  # Content from user level (empty if none)
