# PyJídelníček - Python Library for Strava.cz Menus

**Unofficial Python library for downloading and parsing menus from Strava.cz**

🍽️ **Key Features:**
- Download XML menus from Strava.cz
- Parse daily menus with allergens
- Support for Czech allergen codes

## 📦 Installation

```bash
pip install git+https://github.com/VaclavJirka/pyjidelnicek.git
```

## 📖 Preparation
You need to find out, which Stravné version is your cafeteria using. The easiest way is to check those urls:
- Strava 5: `https://www.strava.cz/strava5/Jidelnicky/XML?zarizeni=<cafeteria_id>`
- Strava 4: `https://www.strava.cz/foxisapi/foxisapi.dll/istravne.istravne.process?xmljidelnickyA&zarizeni=<cafeteria_id>`
You can determine the version by trying both URLs with your cafeteria ID. The one that returns a valid XML response is the version you should use.

## 🚀 Quick Start - Strava.cz API

```python
from pyjidelnicek import Strava5

# Create instance for specific cafeteria (find ID in Strava.cz URL)
strava = Strava5(cafeteria_id=4857)

# Download and parse menu
xml_menu = strava.fetch_xml_menu()
weekly_menu = strava.whole_menu(xml_menu)

# Display menu
for day in weekly_menu['days']:
    print(f"📅 Date: {day['date']}")
    for meal in day['meals']:
        print(f"  🍽️ {meal['type']}: {meal['name']}")
        if meal['allergens']:
            print(f"    ⚠️ Allergens: {', '.join(meal['allergens'])}")
```

## 🔬 Additional Features

### Allergen Code Conversion
```python
# Automatic conversion of allergen codes to readable names
menu_with_allergens = strava.whole_menu(xml_menu, lookup_allergens=True)
for day in menu_with_allergens['days']:
    for meal in day['meals']:
        if meal['allergens']:
            print(f"{meal['name']}: {', '.join(meal['allergens'])}")
```

### Menu for Specific Date
```python
# Get menu for specific date
specific_menu = strava.date_menu(xml_menu, "24-06-2025")
if specific_menu:
    print(f"Menu found for {specific_menu['date']}")
```

## 🚨 Supported Allergens (EU Regulation)

Library recognizes all standard allergens:

| Code | Allergen |
|-----|---------|
| 01, 01a-01f | Obiloviny obsahující lepek (pšenice, žito, ječmen, oves) |
| 02 | Korýši |
| 03 | Vejce |
| 04 | Ryby |
| 05 | Arašídy |
| 06 | Sójové boby |
| 07 | Mléko |
| 08 | Ořechy |
| 09 | Celer |
| 10 | Hořčice |
| 11 | Sezam |
| 12 | Siřičitany |
| 13 | Lupina |
| 14 | Měkkýši |

## 🛠️ Development and Testing

```bash
# Clone repository
git clone https://github.com/VaclavJirka/pyjidelnicek.git
cd pyjidelnicek

# Install in development mode
pip install -e .
```

## 🧪 Testing

```bash
# Run tests
pytest
```

## 📋 Technical Requirements

- **Python 3.8+** - Python version
- **requests** - HTTP library for API calls
- **XML parsing** - built-in Python modules

## 🏷️ Key Terms

- **Strava.cz** - Czech platform for school catering
- **Jídelníček parser** - automatic menu downloading
- **Školní jídelny** - primary use case
- **XML API** - data format from Strava.cz
- **Python library** - programming tool
- **Menu automation** - automated menu fetching

## ⚖️ License

MIT License - open source code

## ⚠️ Disclaimer

This is an **unofficial library**. Author is not affiliated with **Strava.cz** company.

**Use at your own risk** - please respect Strava.cz terms of service.

---

**Tags:** `python` `strava.cz` `jidelnicek` `menu` `parser` `xml` `skolni-jidelna` `kantyna` `alergeny` `automation` `api` `canteen` `cafeteria` `school`
