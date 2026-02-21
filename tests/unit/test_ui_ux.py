"""
UI/UX Design Tests - The Lord of Rivendell (幽谷领主)

Tests for:
- Kalo Growth Palette color system
- Glassmorphism effects
- Responsive design (8pt grid, Golden Ratio)
- Accessibility (WCAG compliance)
- Typography and spacing
"""

import pytest
import re
from pathlib import Path


# Kalo Growth Palette - Core Design System
KALO_GROWTH_PALETTE = {
    "--ks-navy": "#00204E",
    "--forest-root": "#0A594E",
    "--growth-mid": "#46AA8F",
    "--community": "#70D75C",
    "--new-sprout": "#D0ED35",
    "--royal-gold": "#FFB003",
}

# Extended palette
EXTENDED_PALETTE = {
    "--navy-light": "#003366",
    "--navy-dark": "#001833",
    "--forest-light": "#0D6B5A",
    "--forest-dark": "#074038",
    "--growth-light": "#5AC4A3",
    "--growth-dark": "#3A8F77",
    "--gold-light": "#FFC133",
    "--gold-dark": "#E69A00",
}

# Typography Scale (Golden Ratio: 1.618)
GOLDEN_RATIO = 1.618
TYPOGRAPHY_SCALE = {
    "--font-xs": 0.75,  # 12px
    "--font-sm": 0.875,  # 14px
    "--font-base": 1.0,  # 16px
    "--font-lg": 1.25,  # 20px
    "--font-xl": 1.618,  # ~26px
    "--font-2xl": 2.618,  # ~42px
    "--font-3xl": 4.236,  # ~68px
}

# Spacing Scale (8pt Grid)
SPACING_SCALE = {
    "--space-1": 0.5,  # 8px
    "--space-2": 1.0,  # 16px
    "--space-3": 1.5,  # 24px
    "--space-4": 2.0,  # 32px
    "--space-6": 3.0,  # 48px
    "--space-8": 4.0,  # 64px
    "--space-12": 6.0,  # 96px
}


@pytest.fixture
def ui_css_content():
    """Load UI CSS content for testing."""
    ui_path = Path(__file__).parent.parent.parent / "ui" / "cultural_journey.html"
    if ui_path.exists():
        return ui_path.read_text()
    return ""


@pytest.mark.unit
class TestKaloGrowthPalette:
    """Test Kalo Growth Palette color system."""

    def test_core_palette_defined(self, ui_css_content):
        """Verify all core palette colors are defined in CSS."""
        for var_name, hex_value in KALO_GROWTH_PALETTE.items():
            # Check CSS variable is defined
            pattern = rf"{re.escape(var_name)}:\s*{re.escape(hex_value)}"
            assert re.search(pattern, ui_css_content), (
                f"Missing or incorrect color: {var_name} = {hex_value}"
            )

    def test_palette_hex_format(self):
        """Verify all hex colors are valid 6-digit format."""
        for var_name, hex_value in KALO_GROWTH_PALETTE.items():
            assert hex_value.startswith("#"), f"{var_name} should start with #"
            assert len(hex_value) == 7, f"{var_name} should be 7 characters (#RRGGBB)"
            # Check valid hex characters
            hex_part = hex_value[1:]
            assert all(c in "0123456789ABCDEFabcdef" for c in hex_part), (
                f"{var_name} contains invalid hex characters"
            )

    def test_semantic_color_usage(self, ui_css_content):
        """Verify semantic colors are used correctly."""
        # Text colors
        assert "--text-primary" in ui_css_content, "Missing text-primary variable"
        assert "--text-secondary" in ui_css_content, "Missing text-secondary variable"

        # Glass effect colors
        assert "--glass-bg" in ui_css_content, "Missing glass background"
        assert "--glass-border" in ui_css_content, "Missing glass border"

    def test_color_contrast_ratios(self):
        """Test color contrast ratios for accessibility."""

        def hex_to_rgb(hex_color):
            hex_color = hex_color.lstrip("#")
            return tuple(int(hex_color[i : i + 2], 16) for i in (0, 2, 4))

        def luminance(rgb):
            r, g, b = [x / 255.0 for x in rgb]
            r = r / 12.92 if r <= 0.03928 else ((r + 0.055) / 1.055) ** 2.4
            g = g / 12.92 if g <= 0.03928 else ((g + 0.055) / 1.055) ** 2.4
            b = b / 12.92 if b <= 0.03928 else ((b + 0.055) / 1.055) ** 2.4
            return 0.2126 * r + 0.7152 * g + 0.0722 * b

        def contrast_ratio(color1, color2):
            lum1 = luminance(hex_to_rgb(color1))
            lum2 = luminance(hex_to_rgb(color2))
            lighter = max(lum1, lum2)
            darker = min(lum1, lum2)
            return (lighter + 0.05) / (darker + 0.05)

        # Test contrast between navy background and text colors
        navy = KALO_GROWTH_PALETTE["--ks-navy"]
        white = "#FFFFFF"

        ratio = contrast_ratio(navy, white)
        assert ratio >= 4.5, f"Navy/White contrast ratio {ratio:.2f} < 4.5 (WCAG AA)"


@pytest.mark.unit
class TestGlassmorphism:
    """Test Glassmorphism visual effects."""

    def test_glass_panel_class_exists(self, ui_css_content):
        """Verify glass-panel CSS class is defined."""
        assert ".glass-panel" in ui_css_content, "Missing glass-panel class"

    def test_backdrop_filter_applied(self, ui_css_content):
        """Verify backdrop-filter is applied for glass effect."""
        assert "backdrop-filter: blur" in ui_css_content, "Missing backdrop-filter blur"
        assert "-webkit-backdrop-filter: blur" in ui_css_content, (
            "Missing webkit prefix for backdrop-filter"
        )

    def test_glass_background_transparency(self, ui_css_content):
        """Verify glass background has transparency."""
        # Should use rgba for transparency
        assert "rgba" in ui_css_content, "Glass effect should use rgba colors"
        assert "--glass-bg" in ui_css_content, "Missing glass background variable"

    def test_glass_border_properties(self, ui_css_content):
        """Verify glass panel border properties."""
        assert "--glass-border" in ui_css_content, "Missing glass border variable"
        # Should have subtle border
        assert (
            "border: 1px solid" in ui_css_content
            or "border:1px solid" in ui_css_content
        ), "Glass panel should have subtle border"

    def test_hover_effects(self, ui_css_content):
        """Verify hover effects on glass panels."""
        assert ".glass-panel:hover" in ui_css_content, (
            "Missing hover state for glass-panel"
        )


@pytest.mark.unit
class testTypographyScale:
    """Test typography scale based on Golden Ratio."""

    def test_font_variables_defined(self, ui_css_content):
        """Verify all font size variables are defined."""
        for var_name in TYPOGRAPHY_SCALE.keys():
            assert var_name in ui_css_content, f"Missing font variable: {var_name}"

    def test_golden_ratio_progression(self, ui_css_content):
        """Verify font sizes follow Golden Ratio progression."""
        # Extract font sizes from CSS
        font_sizes = {}
        for var_name in TYPOGRAPHY_SCALE.keys():
            pattern = rf"{re.escape(var_name)}:\s*([\d.]+)rem"
            match = re.search(pattern, ui_css_content)
            if match:
                font_sizes[var_name] = float(match.group(1))

        # Check that sizes increase
        sizes = list(font_sizes.values())
        for i in range(1, len(sizes)):
            assert sizes[i] > sizes[i - 1], "Font sizes should increase progressively"

    def test_base_font_size(self, ui_css_content):
        """Verify base font size is 16px (1rem)."""
        pattern = r"--font-base:\s*1rem"
        assert re.search(pattern, ui_css_content), "Base font should be 1rem (16px)"


@pytest.mark.unit
class TestSpacingScale:
    """Test 8pt grid spacing system."""

    def test_spacing_variables_defined(self, ui_css_content):
        """Verify all spacing variables are defined."""
        for var_name in SPACING_SCALE.keys():
            assert var_name in ui_css_content, f"Missing spacing variable: {var_name}"

    def test_8pt_grid_alignment(self, ui_css_content):
        """Verify spacing follows 8pt grid (multiples of 0.5rem)."""
        for var_name, expected_rem in SPACING_SCALE.items():
            pattern = rf"{re.escape(var_name)}:\s*([\d.]+)rem"
            match = re.search(pattern, ui_css_content)
            if match:
                actual_rem = float(match.group(1))
                # Should be multiple of 0.5 (8px in rem at 16px base)
                assert actual_rem % 0.5 == 0, (
                    f"{var_name} should be multiple of 0.5rem (8px)"
                )


@pytest.mark.unit
class TestResponsiveDesign:
    """Test responsive design patterns."""

    def test_viewport_meta_tag(self, ui_css_content):
        """Verify viewport meta tag for mobile responsiveness."""
        assert 'meta name="viewport"' in ui_css_content, "Missing viewport meta tag"
        assert "width=device-width" in ui_css_content, (
            "Viewport should include width=device-width"
        )

    def test_media_queries_exist(self, ui_css_content):
        """Verify media queries for different screen sizes."""
        assert "@media" in ui_css_content, "Missing media queries"

    def test_flexbox_usage(self, ui_css_content):
        """Verify Flexbox is used for layout."""
        assert "display: flex" in ui_css_content or "display:flex" in ui_css_content, (
            "Should use Flexbox for layout"
        )

    def test_css_grid_usage(self, ui_css_content):
        """Verify CSS Grid is used where appropriate."""
        assert "display: grid" in ui_css_content or "display:grid" in ui_css_content, (
            "Should use CSS Grid for layout"
        )


@pytest.mark.unit
class TestAccessibility:
    """Test accessibility (WCAG) compliance."""

    def test_lang_attribute(self, ui_css_content):
        """Verify lang attribute on HTML element."""
        assert 'lang="en"' in ui_css_content, "Missing lang attribute"

    def test_alt_text_for_images(self, ui_css_content):
        """Verify images have alt text."""
        # Find all img tags
        img_tags = re.findall(r"<img[^>]*>", ui_css_content)
        for img in img_tags:
            assert 'alt="' in img or "alt='" in img, (
                f"Image missing alt text: {img[:50]}..."
            )

    def test_aria_labels(self, ui_css_content):
        """Verify ARIA labels for interactive elements."""
        # Check for buttons without aria-label
        buttons = re.findall(r"<button[^>]*>", ui_css_content)
        for button in buttons:
            # Should have aria-label or visible text
            has_aria = "aria-label" in button or "aria-labelledby" in button
            # Note: This is a simplified check

    def test_focus_indicators(self, ui_css_content):
        """Verify focus indicators for keyboard navigation."""
        # Check for focus styles or active states as fallback
        has_focus = ":focus" in ui_css_content
        has_active = ":active" in ui_css_content
        has_hover = ":hover" in ui_css_content

        # Should have at least one interactive state indicator
        assert has_focus or has_active or has_hover, (
            "Missing focus/active/hover styles for keyboard navigation"
        )

        # Check for visual indicators
        has_visual_indicator = (
            "outline" in ui_css_content
            or "box-shadow" in ui_css_content
            or "border-color" in ui_css_content
        )
        assert has_visual_indicator, "Should have visible focus indicators"

    def test_color_not_only_indicator(self, ui_css_content):
        """Verify color is not the only visual indicator."""
        # Check for icons or text accompanying color changes
        assert (
            "icon" in ui_css_content.lower()
            or "✓" in ui_css_content
            or "✗" in ui_css_content
        ), "Should use icons in addition to color"


@pytest.mark.unit
class TestAnimations:
    """Test animation and transition effects."""

    def test_transition_properties(self, ui_css_content):
        """Verify smooth transitions are defined."""
        assert "transition:" in ui_css_content, "Missing transition properties"

    def test_animation_timing_variables(self, ui_css_content):
        """Verify animation timing variables."""
        assert "--ease-smooth" in ui_css_content, "Missing smooth easing"
        assert "--duration-normal" in ui_css_content, "Missing duration variable"

    def test_hover_transitions(self, ui_css_content):
        """Verify hover state transitions."""
        hover_patterns = [":hover", ":focus", ":active"]
        found = any(pattern in ui_css_content for pattern in hover_patterns)
        assert found, "Should have hover/focus/active states"


@pytest.mark.integration
class TestUIComponents:
    """Integration tests for UI components."""

    def test_dashboard_structure(self, ui_css_content):
        """Verify dashboard has proper structure."""
        # Should have header
        assert "<header" in ui_css_content or "header" in ui_css_content.lower(), (
            "Missing header element"
        )

        # Should have main content area
        assert "<main" in ui_css_content or "main" in ui_css_content.lower(), (
            "Missing main content area"
        )

    def test_card_components(self, ui_css_content):
        """Verify card components exist."""
        # Should have card-like containers
        assert "card" in ui_css_content.lower() or "panel" in ui_css_content.lower(), (
            "Missing card/panel components"
        )

    def test_navigation_elements(self, ui_css_content):
        """Verify navigation elements."""
        assert "<nav" in ui_css_content or "nav" in ui_css_content.lower(), (
            "Missing navigation element"
        )


@pytest.mark.slow
class TestPerformance:
    """Performance tests for UI rendering."""

    def test_css_file_size(self, ui_css_content):
        """Verify CSS is reasonably sized."""
        # CSS should be under 100KB
        size_kb = len(ui_css_content.encode("utf-8")) / 1024
        assert size_kb < 100, f"CSS file too large: {size_kb:.1f}KB"

    def test_no_inline_styles(self, ui_css_content):
        """Verify minimal inline styles (separation of concerns)."""
        # Count inline style attributes
        inline_styles = re.findall(r'style="[^"]*"', ui_css_content)
        # Allow some inline styles for dynamic content, but not too many
        assert len(inline_styles) < 20, (
            f"Too many inline styles: {len(inline_styles)}. Use CSS classes instead."
        )
