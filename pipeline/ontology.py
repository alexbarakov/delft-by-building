"""The city's ontology: people, events and organisations, tied to the buildings where they left a trace.

An entity is linked to a building when one of its patterns appears in a checked text about that building: a story of a
context layer (checked against Wikipedia by s08_curated), a 'Did you know' fact (s11_facts), or a resident's quote
(s09_residents). The text is kept on the link as its evidence, so every edge has a source. s13_graph.py builds the graph.

(id, type, English label, Dutch label, years, regex on the English text)
"""

PERSON, EVENT, ORG, ARCH = "person", "event", "organisation", "architect"

ENTITIES = [
    # people
    ("vermeer", PERSON, "Johannes Vermeer", "Johannes Vermeer", "1632–1675", r"\bVermeer\b"),
    ("thins", PERSON, "Maria Thins", "Maria Thins", "c. 1593–1680", r"Maria Thins"),
    ("william", PERSON, "William of Orange", "Willem van Oranje", "1533–1584", r"\bWilliam\b"),
    ("gerards", PERSON, "Balthasar Gerards", "Balthasar Gerards", "1557–1584", r"Gerards"),
    ("hohenlohe", PERSON, "Philips of Hohenlohe", "Philips van Hohenlohe", "1550–1606", r"Hohenlohe"),
    ("bernhard", PERSON, "Prince Bernhard", "Prins Bernhard", "1911–2004", r"Bernhard"),
    ("friso", PERSON, "Prince Friso", "Prins Friso", "1968–2013", r"Friso"),
    ("leeuwenhoek", PERSON, "Antoni van Leeuwenhoek", "Antoni van Leeuwenhoek", "1632–1723", r"Leeuwenhoek"),
    ("stevin", PERSON, "Simon Stevin", "Simon Stevin", "1548–1620", r"Stevin"),
    ("peter", PERSON, "Peter the Great", "Peter de Grote", "1672–1725", r"Peter the Great"),
    ("napoleon", PERSON, "Napoleon", "Napoleon", "1769–1821", r"Napoleon"),
    ("dekeyser", ARCH, "Hendrick de Keyser", "Hendrick de Keyser", "1565–1621", r"Hendrick de Keyser"),
    ("post", ARCH, "Pieter Post", "Pieter Post", "1608–1669", r"Pieter Post"),
    ("crabeth", PERSON, "Dirck and Wouter Crabeth", "Dirck en Wouter Crabeth", "", r"Crabeth"),
    ("terburgh", ARCH, "Nicolaas Terburgh", "Nicolaas Terburgh", "", r"Terburgh"),
    ("hartman", ARCH, "M.A.C. Hartman", "M.A.C. Hartman", "", r"Hartman"),
    ("vanmeegeren", PERSON, "Han van Meegeren", "Han van Meegeren", "1889–1947", r"Meegeren"),
    ("tetar", PERSON, "Paul Tétar van Elven", "Paul Tétar van Elven", "1823–1896", r"Tétar van Elven"),
    ("vanmeerten", PERSON, "Lambert van Meerten", "Lambert van Meerten", "", r"van Meerten"),
    ("thooft", PERSON, "Joost Thooft", "Joost Thooft", "", r"Thooft"),
    ("vanmarken", PERSON, "Jacques van Marken", "Jacques van Marken", "1845–1906", r"van Marken"),
    ("matthes", PERSON, "Agneta Matthes", "Agneta Matthes", "1847–1909", r"Agneta|Matthes"),
    ("sasbout", PERSON, "Pieter Sasbout", "Pieter Sasbout", "", r"Sasbout"),
    ("pauw", PERSON, "Elisabeth Pauw", "Elisabeth Pauw", "", r"Elisabeth Pauw"),
    ("hooft", PERSON, "Willem Hooft", "Willem Hooft", "", r"Willem Hooft"),
    ("schermerhorn", PERSON, "Willem Schermerhorn", "Willem Schermerhorn", "1894–1977", r"Schermerhorn"),
    # events
    ("fire1536", EVENT, "The great fire of 1536", "De stadsbrand van 1536", "1536", r"fire of 1536|1536 fire"),
    ("reformation", EVENT, "The Reformation", "De Reformatie", "1572", r"Reformation"),
    ("murder1584", EVENT, "The murder of William of Orange", "De moord op Willem van Oranje", "1584",
     r"shot (him|here)|murdered|bullet"),
    ("thunderclap", EVENT, "The Delft Thunderclap", "De Delftse donderslag", "1654", r"1654|blast|explosion|exploded"),
    ("academy1842", EVENT, "The founding of the Royal Academy", "De stichting van de Koninklijke Akademie", "1842",
     r"\b1842\b"),
    ("occupation", EVENT, "The German occupation", "De Duitse bezetting", "1940–1945",
     r"Germans|Wehrmacht|occupier|during the war|people in hiding|collaborators"),
    ("wedding2004", EVENT, "A royal wedding", "Een koninklijk huwelijk", "2004", r"married here"),
    # organisations
    ("orange", ORG, "House of Orange-Nassau", "Huis Oranje-Nassau", "", r"House of Orange|Orange-Nassau"),
    ("voc", ORG, "Dutch East India Company (VOC)", "Verenigde Oost-Indische Compagnie (VOC)", "1602–1799",
     r"\bVOC\b|East India Company"),
    ("states", ORG, "States of Holland", "Staten van Holland", "", r"States of Holland|powder store of Holland"),
    ("delfland", ORG, "Delfland water board", "Hoogheemraadschap van Delfland", "", r"Delfland"),
    ("guild", ORG, "Guild of Saint Luke", "Sint-Lucasgilde", "", r"Saint Luke|Sint-Lucasgilde"),
    ("fles", ORG, "De Porceleyne Fles (Royal Delft)", "De Porceleyne Fles (Royal Delft)", "1653–today",
     r"Porceleyne Fles|Royal Delft"),
    ("gist", ORG, "Yeast and spirits factory", "Gist- en Spiritusfabriek", "1869–",
     r"yeast|Gist en Spiritus"),
    ("academy", ORG, "Royal Academy, Polytechnic, TU Delft", "Koninklijke Akademie, Polytechnische School, TU Delft",
     "1842–today", r"Royal Academy|Polytechnic|Technische Hogeschool|university|academy's|TU Delft"),
    ("corps", ORG, "Delftsch Studenten Corps", "Delftsch Studenten Corps", "1848–today", r"Studenten Corps"),
    ("virgilius", ORG, "Sanctus Virgilius", "Sanctus Virgilius", "", r"Virgilius"),
    ("klm", ORG, "KLM's Delft Blue houses", "De Delfts blauwe huisjes van KLM", "1952–today", r"\bKLM\b"),
    ("walloon", ORG, "Walloon congregation", "Waalse gemeente", "1585–today", r"Walloon"),
]

# Residents found by s09 come in as people of their own (type person), linked by their quote.
