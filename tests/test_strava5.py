import pytest
from unittest.mock import Mock, patch
import xml.etree.ElementTree as ET
from requests.exceptions import RequestException
from pyjidelnicek.menu import Strava5


class TestStrava5:
    """Test cases for Strava5 class."""

    def test_init(self):
        """Test Strava5 initialization."""
        s5 = Strava5(4857)
        assert s5.cafeteria_id == 4857
        assert "4857" in s5.url

    def test_url_property(self, strava5):
        """Test URL property generation."""
        expected = "https://www.strava.cz/strava5/Jidelnicky/XML?zarizeni=4857"
        assert strava5.url == expected

    @patch("pyjidelnicek.menu.get")
    def test_fetch_xml_menu_success(self, mock_get, strava5, sample_xml):
        """Test successful XML menu fetching."""
        mock_response = Mock()
        mock_response.text = sample_xml
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response

        result = strava5.fetch_xml_menu()
        assert result == sample_xml
        mock_get.assert_called_once_with(strava5.url)

    @patch("pyjidelnicek.menu.get")
    def test_fetch_xml_menu_http_error(self, mock_get, strava5):
        """Test XML menu fetching with HTTP error."""
        mock_response = Mock()
        mock_response.raise_for_status.side_effect = RequestException(
            "404 Not Found"
        )
        mock_get.return_value = mock_response

        with pytest.raises(
            ValueError, match="Failed to fetch or parse XML menu"
        ):
            strava5.fetch_xml_menu()

    @patch("pyjidelnicek.menu.get")
    def test_fetch_xml_menu_empty_response(self, mock_get, strava5):
        """Test XML menu fetching with empty response."""
        mock_response = Mock()
        mock_response.text = ""
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response

        with pytest.raises(ValueError, match="Received empty response"):
            strava5.fetch_xml_menu()

    @patch("pyjidelnicek.menu.get")
    def test_fetch_xml_menu_invalid_root(self, mock_get, strava5):
        """Test XML menu fetching with invalid root element."""
        invalid_xml = "<invalid>content</invalid>"
        mock_response = Mock()
        mock_response.text = invalid_xml
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response

        with pytest.raises(ValueError, match="Unexpected root element"):
            strava5.fetch_xml_menu()

    def test_parse_day_basic(self, strava5, sample_day_element):
        """Test basic day parsing."""
        result = strava5.parse_day(sample_day_element, lookup_allergens=False)

        assert result["date"] == "23-06-2025"
        assert len(result["meals"]) == 4

        meal = result["meals"][0]
        assert meal["name"] == "celerová s krutony"
        assert meal["type"] == "polévka"
        assert meal["allergens"] == ["01a", "07", "09"]

    def test_parse_day_with_allergen_lookup(self, strava5, sample_day_element):
        """Test day parsing with allergen name lookup."""
        result = strava5.parse_day(sample_day_element, lookup_allergens=True)

        meal = result["meals"][0]
        assert any(
            "pšenice" in allergen.lower() for allergen in meal["allergens"]
        )

    def test_whole_menu(self, strava5, sample_xml):
        """Test complete menu parsing."""
        result = strava5.whole_menu(sample_xml)

        assert result["cafeteria_id"] == 4857
        assert len(result["days"]) == 5
        assert result["days"][0]["date"] == "23-06-2025"
        assert result["days"][1]["date"] == "24-06-2025"

    def test_whole_menu_invalid_xml(self, strava5):
        """Test whole menu parsing with invalid XML."""
        with pytest.raises(ValueError, match="Failed to parse XML"):
            strava5.whole_menu("invalid xml")

    def test_closest_day_menu(self, strava5, sample_xml):
        """Test closest day menu extraction."""
        result = strava5.closest_day_menu(sample_xml)

        assert result["date"] == "23-06-2025"
        assert len(result["meals"]) == 4

    def test_closest_day_menu_no_days(self, strava5):
        """Test closest day menu with no day elements."""
        empty_xml = "<jidelnicky></jidelnicky>"

        with pytest.raises(ValueError, match="No 'den' element found"):
            strava5.closest_day_menu(empty_xml)

    def test_date_menu_found(self, strava5, sample_xml):
        """Test date menu extraction for existing date."""
        result = strava5.date_menu(sample_xml, "24-06-2025")

        assert result["date"] == "24-06-2025"
        assert len(result["meals"]) == 4

    def test_date_menu_not_found(self, strava5, sample_xml):
        """Test date menu extraction for non-existing date."""
        result = strava5.date_menu(sample_xml, "01-01-1970")
        assert result == {}

    def test_date_menu_invalid_format(self, strava5, sample_xml):
        """Test date menu with invalid date format."""
        with pytest.raises(ValueError, match="Invalid date format"):
            strava5.date_menu(sample_xml, "2025-06-20")

    def test_date_menu_invalid_xml(self, strava5):
        """Test date menu with invalid XML."""
        with pytest.raises(ValueError, match="Failed to parse XML"):
            strava5.date_menu("invalid xml", "20-06-2025")
