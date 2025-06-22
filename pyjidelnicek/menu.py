"""Strava menu parser for fetching and parsing cafeteria menus.

This module provides classes for fetching XML menu data from Strava.cz
cafeteria systems and parsing it into structured Python dictionaries.
"""

import json
from importlib import resources
import re
import xml.etree.ElementTree as ET
from datetime import datetime

from requests import get


ALLERGENS: dict[str, str] = json.loads(
    resources.read_text(__package__, "allergens.json")
)


class BaseStrava:
    """Base class for Strava menu parsers.

    This class provides the basic structure and methods for parsing allergen
    codes from menu data.
    """

    def __init__(self, cafeteria_id: int):
        """Initialize the parser with a cafeteria ID.

        Args:
            cafeteria_id: Unique identifier for the cafeteria.
        """
        self.cafeteria_id = cafeteria_id

    def extract_allergen_codes(self, allergen_str: str) -> list:
        """Extract numeric allergen codes from a string.

        Args:
            allergen_str: String containing allergen information.

        Returns:
            List of allergen codes (e.g., ['01a', '03', '07']).
        """
        if not allergen_str or len(allergen_str) == 0:
            return []
        codes = re.findall(r"\b\d{2}[a-zA-Z]?|\b\d{2}", allergen_str)
        return codes

    def allergen_code_to_name(self, code: str) -> str:
        """Convert an allergen code to its human-readable name.

        Args:
            code: Allergen code (e.g., '01a', '03').

        Returns:
            Human-readable allergen name.

        Raises:
            ValueError: If the allergen code is not recognized.
        """
        if code in ALLERGENS:
            return ALLERGENS[code]
        raise ValueError(f"Unknown allergen code: {code}")


class Strava5(BaseStrava):
    """Parser for Strava 5 menu format.

    This class fetches and parses the XML menu from a Strava 5. It provides
    methods to fetch the menu, parse it, and extract meal info.
    """

    url_template = "https://www.strava.cz/strava5/Jidelnicky/XML?zarizeni={}"

    @property
    def url(self) -> str:
        return self.url_template.format(self.cafeteria_id)

    def fetch_xml_menu(self) -> str:
        """Fetch the XML menu data from the Strava5.

        Returns:
            Raw XML string containing menu data.

        Raises:
            ValueError: If the request fails or XML is invalid.
        """
        try:
            response = get(self.url)
            response.raise_for_status()
            xml_text = response.text
            if not xml_text or len(xml_text.strip()) == 0:
                raise ValueError("Received empty response from the server.")

            root = ET.fromstring(xml_text)
            if root.tag != "jidelnicky":
                raise ValueError(f"Unexpected root element: '{root.tag}'")

            return xml_text

        except Exception as e:
            raise ValueError(f"Failed to fetch or parse XML menu: {e}")

    def parse_day(
        self, day_element: ET.Element, lookup_allergens: bool = False
    ) -> dict:
        """Parse a single day element from the XML menu.

        Args:
            day_element: XML element representing a day.
            lookup_allergens: If True, convert allergen codes to names.

        Returns:
            Dictionary containing date and meals for the day.
        """
        day = {"date": day_element.get("datum").strip(), "meals": []}
        for meal in day_element.findall("jidlo"):
            raw_allergens = meal.get("alergeny", "")
            if len(raw_allergens) > 0:
                allergens = self.extract_allergen_codes(raw_allergens)
                if lookup_allergens:
                    allergens = [
                        self.allergen_code_to_name(code) for code in allergens
                    ]
            else:
                allergens = []
            day["meals"].append(
                {
                    "name": meal.get("nazev", "").strip().lower(),
                    "type": meal.get("druh", "").strip().lower(),
                    "allergens": allergens,
                }
            )
        return day

    def whole_menu(
        self, xml_menu: str, lookup_allergens: bool = False
    ) -> dict:
        """Parse the complete menu from XML.

        Args:
            xml_menu: Raw XML string.
            lookup_allergens: If True, convert allergen codes to names.

        Returns:
            Dictionary containing cafeteria_id and list of days with menus.

        Raises:
            ValueError: If XML parsing fails.
        """
        try:
            root = ET.fromstring(xml_menu)
            menu = {"cafeteria_id": self.cafeteria_id, "days": []}
            for day_element in root.findall("den"):
                day = self.parse_day(day_element, lookup_allergens)
                menu["days"].append(day)
            return menu
        except ET.ParseError as e:
            raise ValueError(f"Failed to parse XML: {e}")

    def closest_day_menu(
        self, xml_menu: str, lookup_allergens: bool = False
    ) -> dict:
        """Get the menu of the closest day from the XML.

        Args:
            xml_menu: Raw XML string.
            lookup_allergens: If True, convert allergen codes to names.

        Returns:
            Dictionary representing the menu of the closest day.

        Raises:
            ValueError: If no day elements found or XML parsing fails.
        """
        try:
            root = ET.fromstring(xml_menu)
            day_element = root.find("den")
            if day_element is None:
                raise ValueError("No 'den' element found in the XML menu.")
            return self.parse_day(day_element, lookup_allergens)

        except ET.ParseError as e:
            raise ValueError(f"Failed to parse XML: {e}")

    def date_menu(
        self, xml_menu: str, target_date: str, lookup_allergens: bool = False
    ) -> dict:
        """Get menu for a specific date.

        Args:
            xml_menu: Raw XML string.
            target_date: Date in DD-MM-YYYY format (e.g., '01-01-1970').
            lookup_allergens: If True, convert allergen codes to names.

        Returns:
            Dictionary representing the day's menu, or empty dict if date not found.

        Raises:
            ValueError: If XML parsing fails or date format is invalid.
        """
        try:
            datetime.strptime(target_date, "%d-%m-%Y")

            root = ET.fromstring(xml_menu)
            day_element = root.find(f"den[@datum='{target_date}']")
            if day_element is None:
                return {}
            return self.parse_day(day_element, lookup_allergens)

        except ValueError as e:
            if "time data" in str(e):
                raise ValueError(
                    f"Invalid date format. Expected DD-MM-YYYY, got: {target_date}"
                )
            raise
        except ET.ParseError as e:
            raise ValueError(f"Failed to parse XML: {e}")
