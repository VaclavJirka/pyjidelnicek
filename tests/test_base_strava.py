import pytest
from pyjidelnicek.menu import BaseStrava


class TestBaseStrava:
    """Test cases for BaseStrava class."""

    def test_init(self):
        """Test BaseStrava initialization."""
        bs = BaseStrava(4857)
        assert bs.cafeteria_id == 4857

    @pytest.mark.parametrize(
        "allergen_str,expected",
        [
            (
                "01a-Obiloviny - pšenice,03 -Vejce,09 -Celer",
                ["01a", "03", "09"],
            ),
            ("01,02,03", ["01", "02", "03"]),
            ("", []),
            (None, []),
            ("No allergens here", []),
            ("01a", ["01a"]),
            ("07 -Mléko", ["07"]),
        ],
    )
    def test_extract_allergen_codes(self, base_strava, allergen_str, expected):
        """Test allergen code extraction."""
        result = base_strava.extract_allergen_codes(allergen_str)
        assert result == expected

    def test_allergen_code_to_name_valid(self, base_strava):
        """Test allergen code to name conversion with valid codes."""
        assert "pšenice" in base_strava.allergen_code_to_name("01a")
        assert "vejce" in base_strava.allergen_code_to_name("03")
        assert "mléko" in base_strava.allergen_code_to_name("07")

    def test_allergen_code_to_name_invalid(self, base_strava):
        """Test allergen code to name conversion with invalid codes."""
        with pytest.raises(ValueError, match="Unknown allergen code: 99"):
            base_strava.allergen_code_to_name("99")

    def test_allergen_code_to_name_empty(self, base_strava):
        """Test allergen code to name conversion with empty string."""
        with pytest.raises(ValueError):
            base_strava.allergen_code_to_name("")
