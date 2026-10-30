"""Page localization: map image pixels to page coordinates."""

from digital_pen.pose.page_locator import (
    PageLayout,
    PageLocation,
    PageLocatorConfig,
    detect_dots_fast,
    locate_page,
)

__all__ = [
    "PageLayout",
    "PageLocation",
    "PageLocatorConfig",
    "detect_dots_fast",
    "locate_page",
]
