"""Local geocoder: an exact street and house number to its BAG building, from data/raw/addresses.json.

'Oude Delft 39' matches 39, 39A and 39-1; when the number has several buildings (a letter each), the
plain number wins. Faster than the Locatieserver and never lands on a near miss."""
import json
import re
from functools import cache


def key(street, number):
    return f"{street} {number}".lower()


@cache
def index():
    out = {}
    for a in json.load(open("data/raw/addresses.json")):
        k = key(a["openbare_ruimte"], a["huisnummer"])
        plain = not (a["huisletter"] or a["toevoeging"])
        if k not in out or plain and not out[k][3]:
            out[k] = (a["pandidentificatie"], tuple(a["xy"]), f'{a["openbare_ruimte"]} {a["huisnummer"]}', plain)
    return out


@cache
def streets():
    return sorted({a["openbare_ruimte"] for a in json.load(open("data/raw/addresses.json"))}, key=len, reverse=True)


def lookup(address):
    """'Street 12' or 'Street 12a' → (pand id, (x, y) in RD, 'Street 12') or None."""
    m = re.match(r"^(.*\D)\s+(\d{1,5})\s*[A-Za-z]?(?:-\w+)?$", address.strip())
    hit = m and index().get(key(m.group(1).strip(), int(m.group(2))))
    return hit[:3] if hit else None
