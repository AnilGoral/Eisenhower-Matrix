"""Centralized theme engine for the Eisenhower Matrix application.

All font sizes, stylesheet templates, and scaling logic live here.
Widgets import ``Theme`` and call its helpers instead of hardcoding sizes.
"""

from PyQt5.QtGui import QFont, QColor


class Theme:
    """Scalable theme with named font-size constants and stylesheet generators."""

    _scale: float = 1.0

    # ── CSS pixel font sizes (base values at 100% scale) ─────────────
    FONT_DISPLAY    = 23   # App title bar, task body text
    FONT_HEADLINE   = 22   # Quadrant titles, context-menu items, inputs
    FONT_TITLE      = 18   # Dialog headings, notes, badges, nav buttons
    FONT_BODY       = 17   # Due-date labels, global QLabel/QLineEdit, checkbox
    FONT_BODY_SM    = 16   # Dialog controls (settings tabs/inputs/buttons)
    FONT_CAL_NAV    = 15   # Calendar month/year buttons
    FONT_CAPTION    = 14   # Calendar grid, toast, small text
    FONT_CAPTION_SM = 13   # Clear-date button
    FONT_OVERLINE   = 11   # Tooltips
    FONT_DOT_LG     = 10   # Title-bar accent dot
    FONT_MICRO      = 8    # Decorative quadrant dots

    # ── QFont point sizes (base values at 100% scale) ────────────────
    PT_HEADLINE = 17   # Quadrant titles, task labels, task inputs
    PT_TITLE    = 14   # App title (Bold), dialog section headers (DemiBold)
    PT_CAPTION  = 11   # Title-bar buttons

    # ── Scale helpers ────────────────────────────────────────────────

    @classmethod
    def set_scale(cls, percent: int) -> None:
        """Set global font-size scale factor (clamped 80–150)."""
        cls._scale = max(80, min(150, percent)) / 100.0

    @classmethod
    def get_scale(cls) -> int:
        return round(cls._scale * 100)

    @classmethod
    def px(cls, base: int) -> int:
        """Return a CSS pixel size scaled by the current factor."""
        return round(base * cls._scale)

    @classmethod
    def pt(cls, base: int) -> int:
        """Return a QFont point size scaled by the current factor."""
        return round(base * cls._scale)

    @classmethod
    def font(cls, family: str, base_pt: int, weight: int = -1) -> QFont:
        """Create a QFont with a scaled point size."""
        return QFont(family, cls.pt(base_pt), weight)

    # ── Stylesheet generators ────────────────────────────────────────

    @classmethod
    def app_stylesheet(cls, bg_color: QColor, text_color_name: str,
                       opacity: float) -> str:
        """Master stylesheet for the main window (replaces _apply_full_style)."""
        bg = bg_color
        txt = text_color_name
        opa = opacity

        dr = max(bg.red() - 8, 0)
        dg = max(bg.green() - 8, 0)
        db = max(bg.blue() - 8, 0)
        lr = min(bg.red() + 20, 255)
        lg = min(bg.green() + 20, 255)
        lb = min(bg.blue() + 25, 255)

        title_px = cls.px(cls.FONT_DISPLAY)
        label_px = cls.px(cls.FONT_BODY)
        tip_px   = cls.px(cls.FONT_OVERLINE)

        return f"""
            #rootContainer {{
                background: qlineargradient(
                    x1:0, y1:0, x2:1, y2:1,
                    stop:0 rgba({bg.red()}, {bg.green()}, {bg.blue()}, {opa}),
                    stop:0.5 rgba({lr}, {lg}, {lb}, {opa}),
                    stop:1 rgba({bg.red()}, {bg.green()}, {max(bg.blue()+10,0)}, {opa})
                );
                border-radius: 14px;
                border: 1px solid rgba(255, 255, 255, 0.08);
            }}
            #titleBar {{
                background: rgba({dr}, {dg}, {db}, 0.95);
                border-top-left-radius: 14px;
                border-top-right-radius: 14px;
                border-bottom: 1px solid rgba(255, 255, 255, 0.04);
            }}
            #titleLabel {{
                color: {txt};
                font-size: {title_px}px;
                background: transparent;
                letter-spacing: 1px;
            }}
            #settingsBtn, #minimizeBtn, #closeBtn {{
                color: rgba(255, 255, 255, 0.5);
                background: transparent;
                border: none;
                border-radius: 6px;
                margin: 2px;
            }}
            #settingsBtn:hover, #minimizeBtn:hover {{
                background: rgba(255, 255, 255, 0.08);
                color: rgba(255, 255, 255, 0.9);
            }}
            #closeBtn:hover {{
                background: rgba(255, 80, 80, 0.85);
                color: white;
            }}
            #gridContainer {{ background: transparent; }}
            #gripContainer {{ background: transparent; }}
            QLabel {{
                color: {txt};
                font-size: {label_px}px;
                background: transparent;
            }}
            QLineEdit {{
                font-size: {label_px}px;
                font-family: "Segoe UI";
                color: {txt};
                background: rgba(255, 255, 255, 0.05);
                border: 1px solid rgba(255, 255, 255, 0.1);
                border-radius: 8px;
                padding: 7px 12px;
                selection-background-color: rgba(78, 205, 196, 0.4);
            }}
            QLineEdit:focus {{
                border: 1px solid rgba(78, 205, 196, 0.5);
                background: rgba(255, 255, 255, 0.07);
            }}
            QLineEdit::placeholder {{ color: rgba(255, 255, 255, 0.3); }}
            QCheckBox {{
                spacing: 8px;
                background: transparent;
                min-width: 28px; min-height: 28px;
            }}
            QCheckBox::indicator {{
                width: 22px; height: 22px;
                background: rgba(255, 255, 255, 0.08);
                border: 2px solid rgba(255, 255, 255, 0.25);
                border-radius: 6px;
            }}
            QCheckBox::indicator:hover {{
                border-color: rgba(78, 205, 196, 0.7);
                background: rgba(78, 205, 196, 0.12);
            }}
            QCheckBox::indicator:checked {{
                background: qlineargradient(
                    x1:0, y1:0, x2:1, y2:1,
                    stop:0 #4ECDC4, stop:1 #44B09E
                );
                border: 2px solid #4ECDC4;
                image: none;
            }}
            QScrollArea {{ background: transparent; border: none; }}
            QScrollBar:vertical {{
                background: transparent; width: 5px; margin: 4px 1px;
            }}
            QScrollBar::handle:vertical {{
                background: rgba(255, 255, 255, 0.12);
                border-radius: 2px; min-height: 30px;
            }}
            QScrollBar::handle:vertical:hover {{
                background: rgba(255, 255, 255, 0.22);
            }}
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
                height: 0px;
            }}
            QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {{
                background: transparent;
            }}
            QToolTip {{
                background: #1a1a2e; color: #E8E8F0;
                border: 1px solid rgba(255,255,255,0.1);
                border-radius: 6px; padding: 6px 10px;
                font-size: {tip_px}px;
            }}
        """

    @classmethod
    def dialog_stylesheet(cls) -> str:
        """Settings / general dialog stylesheet (replaces DIALOG_STYLE)."""
        s = cls.px(cls.FONT_BODY_SM)
        return f"""
            QDialog {{ background-color: #1e1e32; color: #E8E8F0; }}
            QTabWidget::pane {{
                background: #252540;
                border: 1px solid rgba(255,255,255,0.08);
                border-radius: 6px; top: -1px;
            }}
            QTabBar::tab {{
                background: rgba(255,255,255,0.04);
                color: rgba(255,255,255,0.55);
                border: none; padding: 8px 20px; margin-right: 2px;
                border-top-left-radius: 6px; border-top-right-radius: 6px;
                font-size: {s}px;
            }}
            QTabBar::tab:selected {{
                background: #252540; color: #E8E8F0; font-weight: bold;
            }}
            QTabBar::tab:hover:!selected {{
                background: rgba(255,255,255,0.08);
                color: rgba(255,255,255,0.8);
            }}
            QLabel {{
                color: #E8E8F0; font-size: {s}px; background: transparent;
            }}
            QLineEdit {{
                background: rgba(255,255,255,0.06);
                border: 1px solid rgba(255,255,255,0.12);
                border-radius: 5px; color: #E8E8F0;
                padding: 6px 10px; font-size: {s}px;
            }}
            QLineEdit:focus {{
                border-color: rgba(255,255,255,0.3);
                background: rgba(255,255,255,0.09);
            }}
            QSpinBox {{
                background: rgba(255,255,255,0.06);
                border: 1px solid rgba(255,255,255,0.12);
                border-radius: 5px; color: #E8E8F0;
                padding: 4px 8px; font-size: {s}px;
            }}
            QSpinBox::up-button, QSpinBox::down-button {{
                background: rgba(255,255,255,0.08); border: none; width: 18px;
            }}
            QSpinBox::up-button:hover, QSpinBox::down-button:hover {{
                background: rgba(255,255,255,0.15);
            }}
            QPushButton {{
                background: rgba(255,255,255,0.07);
                border: 1px solid rgba(255,255,255,0.1);
                border-radius: 6px; color: #E8E8F0;
                padding: 7px 18px; font-size: {s}px;
            }}
            QPushButton:hover {{
                background: rgba(255,255,255,0.12);
                border-color: rgba(255,255,255,0.2);
            }}
            QPushButton:pressed {{ background: rgba(255,255,255,0.05); }}
        """

    @classmethod
    def stats_stylesheet(cls) -> str:
        """Statistics dialog stylesheet (replaces STATS_STYLE)."""
        return """
            QDialog { background-color: #1e1e32; }
            QFrame {
                background-color: #252540; border-radius: 8px;
                border: 1px solid rgba(255,255,255,0.06);
                padding: 10px; margin: 0px;
            }
            QScrollArea { border: none; background-color: transparent; }
            QScrollBar:vertical {
                background-color: transparent; width: 6px;
            }
            QScrollBar::handle:vertical {
                background-color: rgba(255,255,255,0.15);
                border-radius: 3px; min-height: 20px;
            }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                height: 0px;
            }
            QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {
                background: transparent;
            }
            QLabel { padding: 1px; margin: 0px; background: transparent; }
        """
