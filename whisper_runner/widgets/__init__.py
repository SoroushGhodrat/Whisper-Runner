"""Widgets drawn in the app's style. Each module holds one widget (or a few small related ones)."""

from .accordion import Accordion
from .badge import Badge
from .button import Button
from .card import Card
from .flags import flag_image
from .labels import autowrap, clear, label, label_state, say, set_label_state
from .popup_menu import PopupMenu
from .progress import Progress
from .scroll import ScrollArea, ScrollBar
from .tabs import Tabs

__all__ = ["Accordion", "Badge", "Button", "Card", "flag_image", "autowrap", "clear", "label", "label_state",
           "say", "set_label_state", "PopupMenu", "Progress", "ScrollArea", "ScrollBar", "Tabs"]
