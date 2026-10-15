"""The city this build is for. Everything city-specific that is not a story lives here."""
SLUG = "delft"
NAME = "Delft"
GEMEENTE_CODE = "0503"            # BAG ids of the municipality start with this
WOONPLAATS = "Delft"              # PDOK Locatieserver filter
ORIGIN = (84440.0, 447540.0)      # RD New, the Markt between the town hall and the Nieuwe Kerk
BOUNDS = (79000, 441000, 90000, 452000)   # RD New, a box around the municipality
SITE = "https://stop-token.com/lab/delft/"
UA = {"User-Agent": f"{SLUG}-by-building/0.1 ({SITE})"}
WIKIDATA = "Q690"                 # the municipality, for P131* (located in)
ROUND_UNTIL = 1940                # round construction years before this are spread across their rounding step
# Where a walk can start, besides the walker's own location (RD New)
STARTS = [("Markt", "Markt", ORIGIN), ("Station", "Station", (84230.0, 447010.0))]
