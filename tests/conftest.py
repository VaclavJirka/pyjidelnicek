import pytest
import xml.etree.ElementTree as ET
from pyjidelnicek.menu import BaseStrava, Strava5


@pytest.fixture
def sample_xml():
    """Sample XML for testing - loads from fixtures/sample_menu.xml."""
    import os

    fixture_path = os.path.join(
        os.path.dirname(__file__), "fixtures", "sample_menu.xml"
    )
    with open(fixture_path, "r", encoding="utf-8") as f:
        return f.read()


@pytest.fixture
def base_strava():
    """BaseStrava instance for testing."""
    return BaseStrava(4857)


@pytest.fixture
def strava5():
    """Strava5 instance for testing."""
    return Strava5(4857)


@pytest.fixture
def sample_day_element():
    """Sample day XML element."""
    xml = """<den datum="23-06-2025">
        <jidlo nazev="Celerová s krutony" druh="Polévka " alergeny="01a-Obiloviny - pšenice,07 -Mléko,09 -Celer" />
        <jidlo nazev="Čočka na kyselo, jogurtový párek, chléb, steril. okurka, zeleninový salát" druh="Oběd 1 " alergeny="" />
        <jidlo nazev="Čočka na kyselo, vejce, chléb, steril. okurka, zeleninový salát" druh="Oběd 2 " alergeny="" />
        <jidlo nazev="čaj, mléko, voda" druh="Doplněk " alergeny="" />
    </den>"""
    return ET.fromstring(xml)
