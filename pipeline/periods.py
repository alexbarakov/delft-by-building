"""Delft periods. Boundaries follow the city's turning points, not decades."""
PERIODS = [
    # (key, label, start, end, colour) — oxblood brick for the oldest, through ochre and green, to slate and violet
    ("p1", "Before 1536",                        1000, 1535, "#4a1410"),
    ("p2", "1536–1653 After the great fire",     1536, 1653, "#8c1c13"),
    ("p3", "1654–1799 After the thunderclap",    1654, 1799, "#c0462b"),
    ("p4", "1800–1863",                          1800, 1863, "#d97a2b"),
    ("p5", "1864–1913 Polytechnic and factories", 1864, 1913, "#e5b13a"),
    ("p6", "1914–1940",                          1914, 1940, "#8e9f3c"),
    ("p7", "1941–1964",                          1941, 1964, "#3f8f6b"),
    ("p8", "1965–1984",                          1965, 1984, "#2c7391"),
    ("p9", "1985–1999",                          1985, 1999, "#3a4f9a"),
    ("p10", "2000–",                             2000, 2100, "#6a3f8f"),
]

def period_index(year: int) -> int:
    for i, (_, _, a, b, _) in enumerate(PERIODS):
        if a <= year <= b:
            return i
    return 0
