from typing import Dict, Any
from app.schemas.dashboard import GridLayout, WidgetPosition


class LayoutEngine:
    """
    Stateful layout allocator that deterministically computes responsive grid coordinates
    for Desktop (12 cols), Tablet (12 cols), and Mobile (12 cols) screen sizes.
    Avoids widget overlapping through automatic row wrapping.
    """
    def __init__(self) -> None:
        # Desktop layout cursor
        self.d_row = 0
        self.d_col = 0
        
        # Tablet layout cursor
        self.t_row = 0
        self.t_col = 0
        
        # Mobile layout cursor (vertical stacking)
        self.m_row = 0

    def reset(self) -> None:
        """Resets layout coordinate pointers for a new page or section."""
        self.d_row = 0
        self.d_col = 0
        self.t_row = 0
        self.t_col = 0
        self.m_row = 0

    def allocate_coordinates(self, card_size: str, priority: int = 50) -> GridLayout:
        """
        Allocates row, col, width, height for Desktop, Tablet, and Mobile grids
        based on card size configurations.
        """
        # 1. Define dimensions
        if card_size == "small":
            d_w, d_h = 3, 2
            t_w, t_h = 6, 2
            m_w, m_h = 12, 2
        elif card_size == "medium":
            d_w, d_h = 6, 4
            t_w, t_h = 12, 4
            m_w, m_h = 12, 4
        else:  # large or full
            d_w, d_h = 12, 5
            t_w, t_h = 12, 5
            m_w, m_h = 12, 5

        # 2. Allocate Desktop coordinates (wrap at col 12)
        if self.d_col + d_w > 12:
            self.d_row += 2 if card_size == "small" else 4
            self.d_col = 0
        d_pos = WidgetPosition(
            row=self.d_row,
            col=self.d_col,
            width=d_w,
            height=d_h,
            min_width=2 if card_size == "small" else 4,
            min_height=2
        )
        self.d_col += d_w

        # 3. Allocate Tablet coordinates (wrap at col 12)
        if self.t_col + t_w > 12:
            self.t_row += 2 if card_size == "small" else 4
            self.t_col = 0
        t_pos = WidgetPosition(
            row=self.t_row,
            col=self.t_col,
            width=t_w,
            height=t_h,
            min_width=4,
            min_height=2
        )
        self.t_col += t_w

        # 4. Allocate Mobile coordinates (vertical stack, always width 12)
        m_pos = WidgetPosition(
            row=self.m_row,
            col=0,
            width=m_w,
            height=m_h,
            min_width=6,
            min_height=2
        )
        self.m_row += m_h

        return GridLayout(
            desktop=d_pos,
            tablet=t_pos,
            mobile=m_pos,
            priority=priority
        )
