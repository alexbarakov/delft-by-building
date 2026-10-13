"""One striking fact or event per well-known Delft building, shown on its card as 'Did you know'.

Same format as the Amsterdam facts.py: (Wikipedia article, fact in English, fact in Dutch, strings the article must contain,
optional 'addr:Street N'). s11_facts.py matches checks case-insensitively against the article's plain-text extract;
all checks below were run against nl.wikipedia on 2026-10-13. Every entry carries an explicit 'addr:' because most
Delft rows in data/raw/wd_buildings.csv have no BAG id, so the Wikidata route would drop them; each address was
matched exactly by the PDOK Locatieserver. s11 keeps one fact per building, so no building appears twice.

Dropped during research:
- Praalgraf van Willem van Oranje (box with the intestines, 1997): same building as the Nieuwe Kerk; used in the
  curated 'secrets' layer instead.
- Gemeenschapshuis Agnetapark ('first community centre in the Netherlands'): no house number in the article; the
  address in curated_draft.py comes from the Wikidata coordinate only.
- Huetbank, Hugo de Groot statue: no house number.
- Reinier de Graaf Gasthuis ('oldest hospital in the Netherlands', 1252): the claim is about the institution; the
  present buildings are from 1968 onwards and the article gives no exact address.
"""

FACTS = [
    ("nl:Nieuwe Kerk (Delft)",
     "At 108.75 metres its tower is the second highest church tower in the Netherlands, after the Dom in Utrecht.",
     "Met 108,75 meter is de toren na de Domtoren in Utrecht de hoogste kerktoren van Nederland.",
     ("108,75", "Domtoren"), "addr:Markt 80"),
    ("nl:Oude Kerk (Delft)",
     "In 1843 the town council ordered the leaning tower to be pulled down to roof level; local builders prevented it. "
     "It now stands 1.96 metres out of plumb.",
     "In 1843 besloot de gemeenteraad de scheve toren tot aan het kerkdak te slopen; plaatselijke aannemers wisten dat "
     "te voorkomen. De toren staat nu 1,96 meter uit het lood.",
     ("1843", "1,96 meter"), "addr:Heilige Geestkerkhof 25"),
    ("nl:Stadhuis van Delft",
     "The town hall was rebuilt after a fire in 1618 around Het Steen, the oldest building in Delft, which still holds "
     "the old torture chamber.",
     "Het stadhuis werd na een brand in 1618 herbouwd rond Het Steen, het oudste gebouw van Delft, waar de oude "
     "martelkamer nog te zien is.",
     ("1618", "Het Steen", "martelkamer"), "addr:Markt 87"),
    ("nl:Sint-Agathaklooster (Delft)",
     "William of Orange was shot here in 1584; the bullet holes can still be seen in the wall.",
     "Willem van Oranje werd hier in 1584 doodgeschoten; de kogelgaten zijn nog in de muur te zien.",
     ("1584", "kogelgaten"), "addr:Sint Agathaplein 1"),
    ("nl:Oostpoort (Delft)",
     "The only one of Delft's eight town gates still standing; a replica stands in the Huis ten Bosch theme park in "
     "Japan.",
     "De enige van de acht Delftse stadspoorten die nog staat; in het Japanse themapark Huis ten Bosch staat een "
     "replica.",
     ("acht", "Huis ten Bosch"), "addr:Oostpoort 1"),
    ("nl:Kruithuis (Delft)",
     "All the locks and hinges are copper to avoid sparks, and the walls are thicker than the vault, so that in an "
     "explosion the roof would go up and the walls stay standing.",
     "Al het hang-en-sluitwerk is van koper om vonken te voorkomen, en de muren zijn dikker dan het gewelf, zodat bij "
     "een ontploffing het dak de lucht in zou gaan en de muren zouden blijven staan.",
     ("koper", "vonkvorming", "dak de lucht in"), "addr:Schiekade 1"),
    ("nl:Armamentarium (Delft)",
     "Napoleon visited in 1811 and took two richly decorated cannons, cast in Lübeck in 1669, back to Paris.",
     "Napoleon bezocht het arsenaal in 1811 en nam twee rijk versierde kanonnen, in 1669 in Lübeck gegoten, mee naar "
     "Parijs.",
     ("1811", "Napoleon", "Lübeck"), "addr:Korte Geer 1"),
    ("nl:Oude Delft 95",
     "A main benchmark of NAP, the Dutch height datum, is built into the facade.",
     "In de gevel is een hoofdmerk van het NAP gemetseld.",
     ("hoofdmerk van het NAP",), "addr:Oude Delft 95"),
    ("nl:Sint-Huybrechtstoren",
     "The boathouse against this medieval wall tower was designed by the master forger Han van Meegeren.",
     "Het boothuis tegen deze middeleeuwse waltoren is ontworpen door meestervervalser Han van Meegeren.",
     ("Han van Meegeren", "boothuis"), "addr:Oostplantsoen 140"),
    ("nl:De Roos (Delft)",
     "The last of the fifteen windmills that once stood on the town walls; Prince Claus reopened it after "
     "restoration in 1990.",
     "De laatste van de vijftien molens die ooit op de stadswallen stonden; prins Claus heropende hem na de "
     "restauratie in 1990.",
     ("vijftien", "Prins Claus", "1990"), "addr:Phoenixstraat 112"),
    ("nl:Laboratorium voor microchemie en metallografie",
     "For years a Foucault pendulum swung in its tall stairwell.",
     "In het rijzige trappenhuis hing geruime tijd de slinger van Foucault.",
     ("slinger van Foucault",), "addr:Mijnbouwplein 11"),
    ("nl:Rode Scheikunde",
     "Built for chemistry but never fully used for it, in 1939 it stored yellowcake from the Belgian Congo.",
     "Gebouwd voor scheikunde maar daarvoor nooit volledig gebruikt; in 1939 lag er yellowcake uit Belgisch Congo "
     "opgeslagen.",
     ("1939", "yellowcake", "Belgisch Congo"), "addr:Julianalaan 134"),
    ("nl:Aula (TU Delft)",
     "One of the few brutalist buildings left in the Netherlands; its 34.5-metre auditorium juts out on prestressed "
     "concrete.",
     "Een van de weinige resterende brutalistische gebouwen van Nederland; de zaalbak van 34,5 meter kraagt uit dankzij "
     "voorgespannen beton.",
     ("brutalistische", "34,5 meter", "voorgespannen beton"), "addr:Mekelweg 5"),
    ("nl:Hoger Onderwijs Reactor",
     "The only nuclear reactor in the Netherlands on a university campus, in use since 1963.",
     "De enige kernreactor in Nederland in een universitaire omgeving, in gebruik sinds 1963.",
     ("enige kernreactor", "1963"), "addr:Mekelweg 15"),
    ("nl:Koornbeurs (Delft)",
     "The carved animal heads on the facade were given new, real horns in the 2005 restoration.",
     "De dierkoppen op de voorgevel kregen bij de restauratie van 2005 nieuwe echte hoorns.",
     ("dierkoppen", "echte hoorns", "2005"), "addr:Voldersgracht 1"),
    ("nl:Visbank (Delft)",
     "The sign 'Sinds 1342' refers to the year the count let Delft levy dues on fish, not to the founding of the "
     "market.",
     "Het bord 'Sinds 1342' verwijst naar het jaar waarin de graaf Delft toestond leges op vis te heffen, niet naar de "
     "stichting van de markt.",
     ("Sinds 1342", "leges"), "addr:Cameretten 2"),
    ("nl:Sociëteit \"Tyche\"",
     "No other building in the Netherlands has served as a student society for longer: since 1803.",
     "Geen pand in Nederland doet langer dienst als sociëteit: sinds 1803.",
     ("langst", "1803"), "addr:Oude Delft 123"),
    ("nl:Oude Delft 35",
     "The oldest student house still in use in the Netherlands, lived in by students since 1891.",
     "Het oudste nog bestaande studentenhuis van Nederland, sinds 1891 door studenten bewoond.",
     ("oudste nog bestaande studentenhuis", "1891"), "addr:Oude Delft 35"),
    ("nl:Sint-Barbaraklooster (Delft)",
     "When students restored the ruined convent as their society, the Pope gave 5,000 guilders in 1950.",
     "Toen studenten het vervallen klooster tot sociëteit herstelden, gaf de paus in 1950 5.000 gulden.",
     ("Paus", "1950", "5.000 gulden"), "addr:Oude Delft 57"),
    ("nl:Het straatje",
     "In 2015 an art historian identified this as the spot Vermeer painted in The Little Street; the house had been "
     "KLM's 76th Delft Blue miniature since 1995.",
     "In 2015 wees een kunsthistoricus dit aan als de plek die Vermeer schilderde in Het straatje; het huis was al sinds "
     "1995 het 76e Delfts blauwe huisje van de KLM.",
     ("Vlamingstraat", "2015", "76e", "1995"), "addr:Vlamingstraat 42"),
    ("nl:De Handboog",
     "Its facade was already popular with English tourists in the 19th century, when it was a neglected warehouse.",
     "De gevel was in de negentiende eeuw al populair bij Engelse toeristen, toen het nog een verwaarloosd pakhuis was.",
     ("Engelse toeristen", "verwaarloosd pakhuis"), "addr:Koornmarkt 81"),
    ("nl:Lutherse kerk (Delft)",
     "The only church in Delft with a wooden roof older than the great fire of 1536.",
     "De enige Delftse kerk met een houten kap van voor de grote stadsbrand van 1536.",
     ("houten kap", "1536"), "addr:Noordeinde 4"),
    ("nl:Waag (Delft)",
     "From 1554 the rhetoricians' chamber De Rapenbloem used the attic of the weigh house.",
     "Vanaf 1554 gebruikte de rederijkerskamer De Rapenbloem de zolder van de Waag.",
     ("1554", "Rapenbloem", "zolder"), "addr:Markt 11"),
    ("nl:Stadsleenbank (Delft)",
     "The doorway still reads '1769 Den Ingangh van de Stadsleenbanck', the entrance of the town pawn bank.",
     "Boven de ingang staat nog '1769 Den Ingangh van de Stadsleenbanck'.",
     ("Den Ingangh van de Stadsleenbanck",), "addr:Burgwal 45"),
    ("nl:Molslaan 104 (Delft)",
     "One of the oldest buildings in Delft, built around 1465 and one of the few to survive the fire of 1536.",
     "Een van de oudste panden van Delft, rond 1465 gebouwd en een van de weinige die de stadsbrand van 1536 "
     "overleefden.",
     ("1465", "1536", "gespaard"), "addr:Molslaan 104"),
    ("nl:Kantoorgebouw Koninklijke Nederlandsche Gist- en Spiritusfabriek",
     "The walls of the entrance hall are covered with tiles and tile tableaux by De Porceleyne Fles.",
     "De wanden van de hal zijn bekleed met tegelpatronen en tegeltableaus van De Porceleyne Fles.",
     ("tegeltableaus", "De Porceleyne Fles"), "addr:Wateringseweg 1"),
    ("nl:Huis Van Meerten",
     "Lambert van Meerten wanted to leave his house to Delft as a museum, but went bankrupt three years before he "
     "died; a society set up by his friends bought it at auction.",
     "Lambert van Meerten wilde zijn huis na zijn dood als museum aan Delft schenken, maar ging drie jaar voor zijn dood "
     "failliet; een vereniging van zijn vrienden kocht het op de veiling.",
     ("failliet", "veiling"), "addr:Oude Delft 199"),
]
