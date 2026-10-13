"""Hand-curated layers for Delft: buildings standing today, grouped by theme, each with a short story and a source.

Same format as the Amsterdam curated.py: every entry names the Wikipedia article it rests on; s08_curated.py checks that
every string in `checks` appears (case-sensitive) in the article's plain-text extract, then geocodes the address
(PDOK Locatieserver, woonplaats Delft). All checks below were run against the nl.wikipedia extracts on 2026-10-13,
and every address was matched exactly by the PDOK Locatieserver. House numbers come from the article itself or,
where the article has none, from the rijksmonumenten register (nl:Lijst van rijksmonumenten in Delft).

Dropped during research (not verifiable, or not standing / no exact address):
- Herberg Mechelen (Markt, Vermeer's parents' inn): demolished in 1885.
- Het Serpent as a building: demolished c. 1835; kept only as the story of the Maria van Jessekerk on its site.
- Stadsherberg Buyten (where Vermeer is said to have painted the View of Delft): demolished c. 1985.
- De Delftse Pauw pottery: in Rijswijk, outside the municipality.
- De Grieksche A pottery (Lange Geer 44-46): the article speaks of it in the past tense and Wikidata places it at
  Lange Geer 62; no way to tell what still stands.
- Den vliegenden hert (Koornmarkt 77, former brewery site): Koornmarkt 77 does not exist in the BAG.
- Oost-Indisch Pakhuis (1653): no house number in Wikipedia; it is part of the Armamentarium complex (Korte Geer 1),
  which is already in the defences layer.
- Hofje van Almonde (Bagijnhof): no house number in Wikipedia and not a rijksmonument.
- Stationsgebouw (Van Leeuwenhoeksingel 41): address not in the BAG.
- Choorstraat inn De Diamant (Balthasar Gerards' lodging in 1584): no evidence it survives.
- Van Leeuwenhoek's parental house (by the Leeuwenpoort), Carel Fabritius' studio (Doelenstraat), the original
  Sint-Lucasgilde building: none survive (the guild house was rebuilt as a replica in 2007, kept as such).
- Huetbank, Hugo de Groot statue: monuments without a house number.
- Nederlandse Kabelfabriek, Calvé, Bacinol (original), Stationskoffiehuis: demolished or no address.
- Jewish Delft as its own layer: only one building (the synagogue) is documented; it sits in the faith layer.

Doubts to check before publishing:
- De Vliegende Vos: en.wikipedia says Reynier Vos lived on "Voldersgracht 25 or 26"; Voldersgracht 25 is the
  address nearest the Wikidata coordinate. The nl article names only the street.
- De Lindenhof (Zocherweg 9) and Gemeenschapshuis Agnetapark (Zocherweg 2): addresses taken from the nearest
  BAG address to the Wikidata coordinate (5 m and 10 m); the articles give no number.
- Zuiderkerk (Achterom 50): same method (1 m); the article gives no street.
- Vlamingstraat 42: the present house dates from 1875 (rijksmonument 525344); the painting's site is plots 40-42.
- Vermeer Centrum (Voldersgracht 21) is a 2007 reconstruction, so the building-age map will show it as new.
- 13 layers, one over the 8-12 target; 'secrets' or 'war' are the easiest to fold or drop.
"""

# (name, address, story, wikipedia "lang:Title", checks) — every string in `checks` must appear in the article.
CURATED = [
    dict(
        id="vermeer", section="Art and craft", title="Vermeer's Delft", era="1632–1675",
        intro=("Johannes Vermeer was born, worked and was buried in Delft and hardly ever left it. Most of the houses "
               "he knew are gone, but the churches of his baptism and burial, the street he may have painted and the "
               "corner where he lived are still there."),
        entries=[
            ("De Vliegende Vos", "Voldersgracht 25",
             "Vermeer's father ran an inn called the Flying Fox on the Voldersgracht, and Vermeer was born there in "
             "1632. Since 2018 a hotel under the old name has occupied the building.",
             "nl:De Vliegende Vos", ("Voldersgracht", "1632", "2018")),
            ("Nieuwe Kerk", "Markt 80",
             "Vermeer was baptised here on 31 October 1632. His birth date is not known.",
             "nl:Johannes Vermeer", ("31 oktober 1632", "Nieuwe Kerk")),
            ("Vermeer Centrum (Sint-Lucasgilde)", "Voldersgracht 21",
             "From 1661 the painters' guild of Saint Luke met here; Vermeer, a member since 1653, was one of its "
             "headmen. The guild house was pulled down for a school and rebuilt as a replica in 2007.",
             "nl:Sint-Lucasgilde (Delft)", ("Voldersgracht 21", "1661", "2007", "1653")),
            ("Oude Langendijk 25", "Oude Langendijk 25",
             "One of two corner houses where Vermeer may have lived with his mother-in-law Maria Thins from about "
             "1660 until his death; nobody knows which side of the corner it was.",
             "nl:Oude Langendijk 25", ("Oude Langendijk 25", "Maria Thins", "1660")),
            ("Maria van Jessekerk", "Burgwal 18",
             "The church stands on the site of Het Serpent, the other house on the Oude Langendijk corner where "
             "Vermeer may have lived and worked.",
             "nl:Het Serpent", ("Oude Langendijk", "Maria van Jessekerk", "Vermeer")),
            ("Het Straatje", "Vlamingstraat 42",
             "In 2015 art historian Frans Grijzenhout argued that Vermeer's Little Street shows the plots at "
             "Vlamingstraat 40-42, where Vermeer's aunt lived and sold tripe.",
             "nl:Het straatje", ("Vlamingstraat", "40-42", "2015", "Grijzenhout")),
            ("Oude Kerk", "Heilige Geestkerkhof 25",
             "Vermeer collapsed in December 1675 and died a day and a half later; he was buried in the Oude Kerk.",
             "nl:Johannes Vermeer", ("15 december begraven in de Oude Kerk",)),
        ]),
    dict(
        id="orange", section="House of Orange", title="William of Orange", era="1572–2004",
        intro=("William of Orange made Delft his base in the revolt against Spain and was murdered here in 1584. "
               "Because Breda, the family seat, was in Spanish hands, he was buried in Delft, and the Nieuwe Kerk "
               "became the burial church of the House of Orange."),
        entries=[
            ("Prinsenhof", "Sint Agathaplein 1",
             "The former convent of Saint Agatha was William's court from 1572. Balthasar Gerards shot him here in "
             "1584; the bullet holes are still in the wall.",
             "nl:Sint-Agathaklooster (Delft)", ("Sint Agathaplein", "1572", "1584", "Balthasar Gerards", "kogelgaten")),
            ("Waalse Kerk", "Oude Delft 181",
             "The convent chapel where William attended services. After his death it was given to the French-speaking "
             "Walloon congregation, whose first minister arrived in 1585.",
             "nl:Waalse kerk (Delft)", ("Willem van Oranje", "Waalse", "1585")),
            ("Nieuwe Kerk", "Markt 80",
             "William's tomb by Hendrick de Keyser was finished in 1623. Beneath it lies the crypt of the House of "
             "Orange-Nassau, where Prince Bernhard was the last to be interred, in 2004.",
             "nl:Nieuwe Kerk (Delft)", ("Hendrick de Keyser", "1623", "Prins Bernhard", "2004")),
            ("Gemeenlandshuis", "Oude Delft 167",
             "This 1505 house was later home to Philips of Hohenlohe, husband of William's daughter Maria of Nassau. "
             "The Delfland water board has met here since 1645.",
             "nl:Gemeenlandshuis (Delfland)", ("Oude Delft 167", "1505", "Maria van Nassau", "1645")),
            ("Oude Kerk", "Heilige Geestkerkhof 25",
             "Prince Friso and Princess Mabel married here on 24 April 2004, the birthday of William of Orange.",
             "nl:Oude Kerk (Delft)", ("24 april 2004", "Willem van Oranje")),
        ]),
    dict(
        id="thunderclap", section="War and disaster", title="The Delft Thunderclap", era="1654–1707",
        intro=("At a quarter past ten on 12 October 1654 the gunpowder store of Holland, hidden in the former convent "
               "of Saint Clare, exploded. At least a hundred people died and the north-east of the town was flattened; "
               "the shooting range was never rebuilt and became the Paardenmarkt."),
        entries=[
            ("Paardenmarkt artillery magazine", "Paardenmarkt 1",
             "The powder had been stored in the Saint Clare convent since 1637. After the blast an artillery magazine "
             "rose on the convent site, and the cleared shooting range became the Paardenmarkt.",
             "nl:Delftse donderslag", ("Sint-Claraklooster", "Artillerie-magazijn", "Paardenmarkt", "1637")),
            ("Kruithuis", "Schiekade 1",
             "The new powder house of 1660 was put far outside the walls, with copper fittings against sparks and a "
             "roof meant to blow off while the walls stood.",
             "nl:Kruithuis (Delft)", ("1660", "Delftse donderslag", "Pieter Post")),
            ("Hofje van Gratie", "Van der Mastenstraat 24",
             "The almshouse moved here when the Armamentarium expanded; the ground was given free, and the "
             "explosion of 1654 is part of why it was available.",
             "nl:Hofje van Gratie (Delft)", ("Van der Mastenstraat", "12 oktober 1654", "Delftse donderslag")),
            ("Nieuwe Kerk", "Markt 80",
             "The blast destroyed all the church's stained-glass windows, painted by the brothers Dirck and Wouter "
             "Crabeth.",
             "nl:Nieuwe Kerk (Delft)", ("1654", "Delftse donderslag", "Crabeth")),
            ("Sociëteit Tyche", "Oude Delft 123",
             "The blast caused heavy damage around the Paardenmarkt; this house on the Oude Delft got off with some broken glass.",
             "nl:Sociëteit \"Tyche\"", ("1654", "glasschade", "Paardenmarkt")),
            ("Hofje van Pauw", "Paardenmarkt 54",
             "Eight almshouses round a garden, completed in 1707 on the Paardenmarkt from the will of Elisabeth Pauw.",
             "nl:Elisabeth Pauw", ("Paardenmarkt", "1707", "acht")),
        ]),
    dict(
        id="science", section="Science and learning", title="Scientists and engineers", era="1586–1966",
        intro=("Simon Stevin tested falling bodies from a Delft church tower and Antoni van Leeuwenhoek sent his "
               "microscope observations to the Royal Society from 1674. In 1842 the engineering academy was founded "
               "that grew into TU Delft, first on the Oude Delft and later in its own quarter south of the old town."),
        entries=[
            ("Nieuwe Kerk", "Markt 80",
             "Around 1586 Simon Stevin and Jan Cornets de Groot dropped two lead balls, one ten times heavier, from "
             "the tower and heard them land together.",
             "nl:Nieuwe Kerk (Delft)", ("Simon Stevin", "1586", "valproef")),
            ("Oude Kerk", "Heilige Geestkerkhof 25",
             "Antoni van Leeuwenhoek, who was baptised in the Nieuwe Kerk four days after Vermeer, was buried here in "
             "1723.",
             "nl:Antoni van Leeuwenhoek", ("1723 in de Oude Kerk", "vier dagen na Vermeer")),
            ("Kruithuis", "Schiekade 1",
             "In 1697 Tsar Peter the Great visited the powder house and met Van Leeuwenhoek, who showed him his "
             "optical instruments.",
             "nl:Kruithuis (Delft)", ("1697", "Peter de Grote", "Antoni van Leeuwenhoek")),
            ("Oude Delft 95", "Oude Delft 95",
             "Built in 1720 as the largest patrician house in Delft; from 1842 to 1952 it was the main building of the "
             "Royal Academy and its successors, the Polytechnic and the Technische Hogeschool.",
             "nl:Oude Delft 95", ("1720", "1842", "1952", "Koninklijke Akademie")),
            ("Sint-Hippolytuskapel", "Oude Delft 118",
             "A chapel from around 1400 that served as the aula of the university from the 1920s until 1966.",
             "nl:Sint-Hippolytuskapel", ("Oude Delft", "aula van de TU Delft", "1966")),
            ("Laboratory of Mechanical and Shipbuilding Engineering", "Ezelsveldlaan 61",
             "Built 1905-1911 by government architect J.A.W. Vrijman; until 2008 it housed the Techniek Museum Delft.",
             "nl:Voormalig laboratorium voor de afdeling Werktuig- en Scheepsbouwkunde",
             ("Ezelsveldlaan 61", "1905-1911", "2008")),
            ("Laboratory for Microchemistry", "Mijnbouwplein 11",
             "Completed in 1930 for technical physics; a Foucault pendulum hung in its tall stairwell for years.",
             "nl:Laboratorium voor microchemie en metallografie", ("Mijnbouwplein 11", "1930", "slinger van Foucault")),
            ("Rode Scheikunde (BKCity)", "Julianalaan 134",
             "Built 1918-1923 for chemistry but never fully used for it; in 1939 it stored yellowcake from the Belgian "
             "Congo. Architecture moved in after its own building burned in 2008.",
             "nl:Rode Scheikunde", ("Julianalaan 134", "1939", "yellowcake", "2008")),
            ("Aula", "Mekelweg 5",
             "The 1966 aula by Van den Broek and Bakema: a 34.5-metre cantilevered concrete auditorium resting mainly "
             "on two columns, made possible by prestressed concrete.",
             "nl:Aula (TU Delft)", ("1966", "Bakema", "34,5 meter", "voorgespannen beton")),
            ("Hoger Onderwijs Reactor", "Mekelweg 15",
             "A 2 MW research reactor in use since 1963, the only nuclear reactor in the Netherlands on a university "
             "campus.",
             "nl:Hoger Onderwijs Reactor", ("Mekelweg 15", "1963", "enige kernreactor")),
        ]),
    dict(
        id="delftblue", section="Art and craft", title="Delft Blue", era="1647–today",
        intro=("When civil war in China stopped VOC imports of porcelain after 1647, Delft potters began imitating it "
               "in tin-glazed earthenware. Around 1700 the town had some thirty potteries; De Porceleyne Fles, founded "
               "in 1653, still works, and Delft Blue turns up in museums, offices and KLM's miniature houses."),
        entries=[
            ("Oost-Indisch Huis", "Oude Delft 39",
             "The Delft chamber of the VOC bought its house on the Oude Delft around 1631. Its trade in Chinese "
             "porcelain is what Delft potters copied when imports stopped after 1647.",
             "nl:VOC-Kamer Delft", ("Oude Delft", "1631", "1647", "plateelbakkers")),
            ("Oosteinde 175", "Oosteinde 175",
             "The first home of De Porceleyne Fles, founded in 1653. The house became a church in 1949; its hall is "
             "lined with glazed tiles.",
             "nl:Oosteinde 175", ("De Porceleyne Fles", "1949", "tegels")),
            ("De Porceleyne Fles (Royal Delft)", "Rotterdamseweg 196",
             "Founded in 1653. Joost Thooft revived hand-painted Delft Blue after buying the pottery in 1876; it "
             "became royal in 1919 and moved here in the 1920s.",
             "nl:De Porceleyne Fles", ("Rotterdamseweg", "1653", "1876", "1919")),
            ("Gist en Spiritusfabriek head office", "Wateringseweg 1",
             "The 1905 head office of the yeast factory; its hall walls carry tile patterns and tableaux by De "
             "Porceleyne Fles.",
             "nl:Kantoorgebouw Koninklijke Nederlandsche Gist- en Spiritusfabriek",
             ("Wateringseweg 1", "1905", "De Porceleyne Fles")),
            ("Huis van Meerten", "Oude Delft 199",
             "Collector Lambert van Meerten built this house in 1893; as a museum it showed Delft earthenware and the "
             "tile collection of Jan Schouten.",
             "nl:Huis Van Meerten", ("Oude Delft 199", "1893", "Delfts aardewerk", "tegelverzameling")),
            ("Museum Prinsenhof", "Sint Agathaplein 1",
             "The town museum, founded in 1897, shows Delft Blue alongside Delft scientists and painters.",
             "nl:Museum Prinsenhof Delft", ("Delfts blauw", "1897")),
            ("De Handboog", "Koornmarkt 81",
             "A brewery house from about 1550, made into KLM's Delft Blue miniature house number 32 in 1967.",
             "nl:De Handboog", ("Koornmarkt", "1550", "KLM", "1967")),
            ("Het Straatje", "Vlamingstraat 42",
             "The house in Vermeer's painting became KLM's 76th Delft Blue miniature in 1995.",
             "nl:Het straatje", ("76e", "KLM", "1995")),
        ]),
    dict(
        id="trade", section="Trade and industry", title="Markets, beer and trade", era="1342–1922",
        intro=("Before pottery, beer was Delft's big trade, and many potteries later moved into old brewery buildings. "
               "The market square and the streets behind the town hall kept the halls for meat, fish, butter and "
               "weighing, and the VOC ran one of its chambers from the Oude Delft."),
        entries=[
            ("Waag", "Markt 11",
             "The town weigh house, probably built after the fire of 1536; the rhetoricians' chamber De Rapenbloem "
             "used its attic from 1554. The gable is dated 1770, and weighing went on until 1960.",
             "nl:Waag (Delft)", ("1536", "Rapenbloem", "1770", "1960")),
            ("Stadsboterhuis", "Markt 17",
             "The town butter house, where Delft butter was traded.",
             "nl:Stadsboterhuis", ("Delftse boter",)),
            ("Vleeshal (Koornbeurs)", "Voldersgracht 1",
             "A meat hall over a medieval cellar, rebuilt in stone in 1650; its facade carries carved animal heads. "
             "From 1871 it was the grain exchange.",
             "nl:Koornbeurs (Delft)", ("1650", "1871", "dierkoppen", "Voldersgracht")),
            ("Visbank", "Cameretten 2",
             "Fish was sold at this open hall against the meat hall for centuries; the trade ended on 11 January 2025.",
             "nl:Visbank (Delft)", ("Vleeshal", "Camaretten", "11 januari 2025")),
            ("Stadsleenbank", "Burgwal 45",
             "The municipal pawn bank, set up in 1676 and given its present front in 1769; it closed in 1922.",
             "nl:Stadsleenbank (Delft)", ("Burgwal 45", "1676", "1769", "1922")),
            ("De Kaerskorf and De Maen", "Markt 2",
             "Two linked houses on the corner of the square, named after a candle maker; for almost 200 years a "
             "tobacco shop traded in De Maen.",
             "nl:De Kaerskorf/De Maen", ("Markt 2-4", "kaarsenmaker", "Tabak-Snuif")),
            ("Oost-Indisch Huis", "Oude Delft 39",
             "The house of the Delft chamber of the VOC from 1631. In the 18th century almost 11,000 Delft people "
             "sailed for the company.",
             "nl:VOC-Kamer Delft", ("1631", "11.000")),
            ("Het Truweel", "Koornmarkt 64",
             "A brewery house dated 1545 above the door; the brewery was one of the last in Delft when it closed in "
             "1848.",
             "nl:Het Truweel", ("Koornmarkt", "1545", "1848", "brouwerij")),
            ("De Handboog", "Koornmarkt 81",
             "Until 1625 part of the brewery of Cornelis van der Wel; in the 18th century a VOC paymaster lived here.",
             "nl:De Handboog", ("Koornmarkt", "1625", "brouwerij", "VOC")),
            ("Oude Delft 95", "Oude Delft 95",
             "In 1717 Willem Hooft bought the brewery De Cimbel on this plot and replaced it with the largest "
             "patrician house in Delft.",
             "nl:Oude Delft 95", ("1717", "de Cimbel", "grootste patriciërshuis")),
            ("Museum Paul Tétar van Elven", "Koornmarkt 67",
             "In the 16th century this house belonged to the brewery Het Dubbelde Cruys; the painter Paul Tétar van "
             "Elven lived here from 1864 to 1894.",
             "nl:Museum Paul Tétar van Elven", ("Koornmarkt 67", "Het Dubbelde Cruys", "1864-1894")),
        ]),
    dict(
        id="charity", section="Faith and community", title="Almshouses and orphanages", era="1465–1968",
        intro=("Delft once had seven hofjes, courtyards of almshouses left by wealthy citizens in their wills; four "
               "remain. Orphanages, a foundling house and a madhouse were run by the town and by charitable boards."),
        entries=[
            ("Molslaan 104", "Molslaan 104",
             "Built around 1465 as a shelter for the homeless, one of the few buildings to survive the fire of 1536; "
             "from 1579 it was the foundling house.",
             "nl:Molslaan 104 (Delft)", ("1465", "1536", "1579", "vondelingenhuis")),
            ("Hofje van Gratie", "Van der Mastenstraat 24",
             "Founded in 1575 by Pieter Sasbout for married couples over fifty without children.",
             "nl:Hofje van Gratie (Delft)", ("1575", "Pieter Sasbout", "50 jaar")),
            ("Klaeuwshofje", "Oranje Plantage 58",
             "Founded in 1605 by the owners of the brewery De Klaeuw for elderly Catholic women.",
             "nl:Klaeuwshofje", ("1605", "Klaeuw", "rooms-katholieke")),
            ("Hofje van Pauw", "Paardenmarkt 54",
             "Built in 1707 under the will of Elisabeth Pauw for poor people; in 2007 its eight houses were home to "
             "people with learning disabilities.",
             "nl:Hofje van Pauw", ("1707", "Elisabeth Pauw", "acht huisjes")),
            ("Meisjeshuis", "Oude Delft 112",
             "From 1578 to 1954 an orphanage for girls who had lost one parent; the present building by Nicolaas "
             "Terburgh opened in 1769.",
             "nl:Meisjeshuis (Delft)", ("1578", "1954", "1769", "Terburgh")),
            ("Jongenshuis", "Oude Delft 137",
             "A patrician house built in 1892, used as an orphanage from 1926 to 1968; it faces the old Meisjeshuis.",
             "nl:Jongenshuis (Delft)", ("Oude Delft 137", "1892", "1926", "1968")),
            ("Sint-Barbaraklooster", "Oude Delft 57",
             "A convent founded in 1405 on the Oude Delft that became the orphanage of the Reformed church after the "
             "Reformation.",
             "nl:Sint-Barbaraklooster (Delft)", ("1405", "Oude Delft", "Weeshuis der Gereformeerden")),
            ("Lutherse Kerk", "Noordeinde 4",
             "The 15th-century chapel of the Sint-Jorisgasthuis, used for a time as a madhouse, then as an artillery "
             "store, and as a Lutheran church since 1768.",
             "nl:Lutherse kerk (Delft)", ("Noordeinde", "Sint-Jorisgasthuis", "dolhuis", "1768")),
            ("Sint Joris Gasthuis", "Sint Jorisweg 2",
             "In the 1890s the Sint Joris asylum moved out of town; its hospital building of 1895 by M.A.C. Hartman "
             "is part of a symmetrical complex of eight pavilions.",
             "nl:Sint Joris Gasthuis", ("1895", "Hartman", "acht paviljoens")),
            ("Villa Maria", "Oostsingel 185",
             "Built in 1894 for the director of the Sint Jorisgasthuis asylum next door; owners restored it to its "
             "original state in thirteen years.",
             "nl:Villa Maria (Delft)", ("Oostsingel 185", "1894", "dertien jaar")),
        ]),
    dict(
        id="faith", section="Faith and community", title="Churches, open and hidden", era="1246–2006",
        intro=("In 1572 Delft chose the Reformation and the two great churches became Protestant. Catholics, "
               "Remonstrants and others worshipped in hidden churches behind house fronts; the first Catholic church "
               "back in the centre opened in 1882."),
        entries=[
            ("Oude Kerk", "Heilige Geestkerkhof 25",
             "The oldest church in Delft, from 1246. Its tower, built half on a filled-in canal, leans 1.96 metres.",
             "nl:Oude Kerk (Delft)", ("1246", "Heilige Geestkerkhof 25", "1,96 meter")),
            ("Nieuwe Kerk", "Markt 80",
             "Dedicated to Saint Ursula before the Reformation; at 108.75 metres its tower is the second highest "
             "church tower in the Netherlands.",
             "nl:Nieuwe Kerk (Delft)", ("Ursula", "108,75 meter", "Domtoren")),
            ("Maria en Ursulakerk", "Bagijnhof 21",
             "A hidden church of 1743 behind the Bagijnhof, reached through a 17th-century house; it is now Old "
             "Catholic.",
             "nl:H.H. Maria en Ursulakerk", ("Bagijnhof", "1743", "schuilkerk", "oudkatholieke")),
            ("Maria van Jessekerk", "Burgwal 18",
             "Built 1875-1882 in the old Catholic quarter, the first Catholic church back in the centre; its two "
             "towers recall the two medieval churches.",
             "nl:Maria van Jessekerk", ("1875 - 1882", "eerste katholieke kerk", "Papenhoek")),
            ("Génestetkerk", "Oude Delft 102",
             "A Remonstrant church of 1896 behind a gate on the Oude Delft, on the site of a hidden church of 1638.",
             "nl:Génestetkerk", ("1896", "Oude Delft", "schuilkerk", "1638")),
            ("Lutherse Kerk", "Noordeinde 4",
             "Lutheran since 1768, and the only Delft church whose wooden roof is older than the fire of 1536.",
             "nl:Lutherse kerk (Delft)", ("1768", "1536", "houten kap")),
            ("Waalse Kerk", "Oude Delft 181",
             "The convent chapel of Saint Agatha, used since 1585 by the French-speaking Walloon Reformed "
             "congregation; it was enlarged when Huguenots arrived in the 17th century.",
             "nl:Waalse kerk (Delft)", ("1585", "Waalse", "hugenoten")),
            ("Sint-Hippolytuskapel", "Oude Delft 118",
             "Built around 1400 as the chapel of a house of sisters; Catholic again since 1972, when parishioners of "
             "the demolished Hippolytuskerk bought it.",
             "nl:Sint-Hippolytuskapel", ("1400", "1972", "Heilige Geestzusterhuis")),
            ("Synagogue", "Koornmarkt 12",
             "A neoclassical synagogue of 1861-1862. It fell out of use after 1945; since 2006 a Jewish congregation "
             "holds services here again.",
             "nl:Synagoge (Delft)", ("1861-1862", "1945", "2006")),
            ("Zuiderkerk", "Achterom 50",
             "A Reformed church of 1888 in a courtyard; it was sold to an ironmonger in 1965 and has been an "
             "evangelical church since 1992.",
             "nl:Zuiderkerk (Delft)", ("1888", "1965", "ijzerhandel", "1992")),
        ]),
    dict(
        id="defences", section="War and disaster", title="Walls, gates and arsenals", era="1359–1900",
        intro=("Delft had eight gates and a ring of walls with towers and windmills. Most gates were pulled down around "
               "1840; one gate, three wall towers and one mill remain, together with the arsenals of the "
               "States of Holland."),
        entries=[
            ("Oostpoort", "Oostpoort 1",
             "The only one of Delft's eight town gates left. It was rebuilt after 1359, raised in 1519 and spared "
             "around 1840 because it stood in a corner where it was in nobody's way.",
             "nl:Oostpoort (Delft)", ("acht", "1359", "1519", "1840")),
            ("Bagijnetoren", "Phoenixstraat 85",
             "A watchtower in the wall from around 1500; it was already rented out as a dwelling in 1538. Trams now "
             "run past it on the Phoenixstraat.",
             "nl:Bagijnetoren", ("1500", "1538", "Phoenixstraat")),
            ("Rietveldse Toren", "Oosterstraat 94",
             "One of three surviving wall towers, at the end of the Oosterstraat. In 1582 a woman living in it ran a "
             "ropewalk over the wall.",
             "nl:Rietveldse Toren", ("drie overgebleven waltorens", "Oosterstraat", "1582")),
            ("Sint-Huybrechtstoren", "Oostplantsoen 140",
             "An early-16th-century wall tower where arms and powder were kept, reached by a tunnel that was "
             "uncovered in 2020.",
             "nl:Sint-Huybrechtstoren", ("16e eeuw", "kruit", "2020")),
            ("Molen De Roos", "Phoenixstraat 112",
             "The last of fifteen windmills that stood on the town walls; it was built on a bastion in 1679 and still "
             "grinds grain.",
             "nl:De Roos (Delft)", ("vijftien", "1679", "rondeel")),
            ("Armamentarium", "Korte Geer 1",
             "Arsenal of the States of Holland, built from 1601 with a north wing dated 1692. Napoleon visited in 1811 "
             "and took two decorated cannons to Paris.",
             "nl:Armamentarium (Delft)", ("1601", "1692", "1811", "Napoleon")),
            ("Artilleriekazerne", "Paardenmarkt 1",
             "Artillery barracks of 1845, raised in 1863 and in military use until 1927; next to it stands a stone "
             "magazine of the States of Holland from 1671.",
             "nl:Artilleriekazerne (Delft)", ("1845", "1863", "1927", "1671")),
            ("Kruithuis", "Schiekade 1",
             "Two powder towers in a moat, designed by Pieter Post in 1660; they could hold 400,000 pounds of powder.",
             "nl:Kruithuis (Delft)", ("Pieter Post", "1660", "400.000 pond")),
            ("Het Wapen van Savoyen", "Oude Delft 169",
             "A stepped-gable house of 1565 that served as an artillery barracks from 1787 to 1807, later as the "
             "town archive.",
             "nl:Het Wapen van Savoyen", ("1565", "artilleriekazerne", "1787 tot 1807", "Gemeentearchief")),
        ]),
    dict(
        id="students", section="Science and learning", title="Student Delft", era="1803–today",
        intro=("The engineering school of 1842 brought students to Delft, and their clubs took over canal houses, a "
               "meat hall and a convent. Some of these societies have been in the same building for well over a "
               "century."),
        entries=[
            ("Oude Delft 35", "Oude Delft 35",
             "The oldest student house still in use in the Netherlands: students have lived here since 1891, as a "
             "house of the Delftsch Studenten Corps since 1896.",
             "nl:Oude Delft 35", ("oudste nog bestaande studentenhuis", "1891", "1896")),
            ("Sociëteit Tyche", "Oude Delft 123",
             "The building in longest use as a student society in the country: Standvastigheid from 1803, the "
             "Delftsche Studenten Bond since 1953.",
             "nl:Sociëteit \"Tyche\"", ("Oude Delft 123", "1803", "1953", "langst")),
            ("Sociëteit Phoenix", "Phoenixstraat 30",
             "The society of the Delftsch Studenten Corps (founded 1848). Its previous building burned down in 1876 "
             "and work on this one began the same year.",
             "nl:Delftsch Studenten Corps", ("Phoenixstraat 30", "1876", "1848")),
            ("Oude Delft 18", "Oude Delft 18",
             "A house of 1785 bought by the Catholic student society Sanctus Virgilius, which moved in in 1922.",
             "nl:Oude Delft 18", ("1785", "Sanctus Virgilius", "1922")),
            ("Sint-Barbaraklooster (Alcuin)", "Oude Delft 57",
             "The ruined convent was taken over by Sanctus Virgilius in 1947 and restored by the students; the Pope "
             "gave 5,000 guilders in 1950.",
             "nl:Sint-Barbaraklooster (Delft)", ("1947", "Paus", "5.000 gulden")),
            ("De Engelenbak", "Oude Delft 89",
             "Part of the academy's school buildings when it opened in 1842; since 1947 a student house, the first of the foundation that "
             "became DUWO. Its name refers to the cheapest seats in the theatre.",
             "nl:Studentenheerenhuisch de Engelenbak", ("Oude Delft 89", "1842", "1947", "DUWO")),
            ("Koornbeurs", "Voldersgracht 1",
             "The old meat hall has been the society of the student association now called OJV de Koornbeurs since "
             "1945.",
             "nl:Koornbeurs (Delft)", ("1945", "OJV de Koornbeurs")),
            ("De Handboog", "Koornmarkt 81",
             "A brewery house of about 1550, now part of a row of student houses.",
             "nl:De Handboog", ("1550", "studentenhuizen")),
            ("Kruithuis", "Schiekade 1",
             "Since 1964 the powder house is used by scouts; the student scout group Delftsche Zwervers has its den in "
             "the west tower.",
             "nl:Kruithuis (Delft)", ("1964", "Delftsche Zwervers")),
        ]),
    dict(
        id="war", section="War and disaster", title="Occupation 1940–1945", era="1939–1948",
        intro=("In November 1940 Delft students went on strike against the dismissal of Jewish professors, one of the "
               "first protests against the occupation; the Germans closed the school. Some 180 Delft students and "
               "staff died in the war."),
        entries=[
            ("Koornbeurs", "Voldersgracht 1",
             "In 1939 the cellar became the command post of Delft's air-raid protection, with gas- and bomb-proof "
             "doors that are still the entrance; the Germans took it over in 1940.",
             "nl:Koornbeurs (Delft)", ("1939", "luchtbescherming", "bomdeuren", "1940")),
            ("Sociëteit Tyche", "Oude Delft 123",
             "In 1941 the Wehrmacht requisitioned the society building as a bar for soldiers; it was returned "
             "wrecked in 1945.",
             "nl:Sociëteit \"Tyche\"", ("1941", "Wehrmacht", "1945")),
            ("Oude Delft 18", "Oude Delft 18",
             "The occupier dissolved Sanctus Virgilius at the end of 1940 and seized its house, which became a labour "
             "office in 1942.",
             "nl:Oude Delft 18", ("1940", "in beslag genomen", "arbeidsbureau", "1942")),
            ("Rode Scheikunde", "Julianalaan 134",
             "The Germans stored artillery shells in one wing while people in hiding were sheltered in another.",
             "nl:Rode Scheikunde", ("Duitse artilleriegranaten", "onderduikers")),
            ("Sint-Barbaraklooster", "Oude Delft 57",
             "During the war people in hiding took refuge in the ruined convent.",
             "nl:Sint-Barbaraklooster (Delft)", ("onderduikers", "ruïne")),
            ("Armamentarium", "Korte Geer 1",
             "After the war the arsenal served for about three years as a prison for collaborators.",
             "nl:Armamentarium (Delft)", ("Tweede Wereldoorlog", "gevangenis")),
            ("Nieuwe Kerk", "Markt 80",
             "On 19 September 1945 a service here remembered the Delft students who had died; Prime Minister "
             "Schermerhorn spoke.",
             "nl:Verzet van Delftse studenten en docenten tijdens de Tweede Wereldoorlog",
             ("19 september 1945", "Nieuwe Kerk", "Schermerhorn", "180")),
        ]),
    dict(
        id="industry", section="Trade and industry", title="Factories and the garden village", era="1869–2008",
        intro=("Jacques van Marken, the Polytechnic's first graduate in technology, founded the yeast and spirits "
               "factory in 1869 and built a park village for its workers. A zinc works, a soap factory and a water "
               "tower are other traces of industrial Delft."),
        entries=[
            ("Gist en Spiritusfabriek head office", "Wateringseweg 1",
             "Head office of the yeast factory founded by Jacques van Marken and Agneta Matthes, built in 1905 by "
             "Karel Muller and Bastiaan Schelling.",
             "nl:Kantoorgebouw Koninklijke Nederlandsche Gist- en Spiritusfabriek",
             ("Wateringseweg 1", "1905", "Karel Muller")),
            ("De Lindenhof (De Tent)", "Zocherweg 9",
             "The community building of the Agnetapark, built in 1914 to a design by Henri Evers. The park, completed "
             "in 1884, is seen as the first garden village in the Netherlands.",
             "nl:Agnetapark", ("De Tent", "1914", "Henri Evers", "eerste tuindorp")),
            ("Gemeenschapshuis Agnetapark", "Zocherweg 2",
             "Built in 1892 as a community house with a nursery school, sewing lessons and a library; described as "
             "the first community centre in the Netherlands.",
             "nl:Gemeenschapshuis Agnetapark", ("1892", "eerste buurthuis van Nederland")),
            ("Zeepfabriek Bousquet", "Voorstraat 92",
             "A 19th-century soap works with a steam engine and chimney behind Voorstraat 90-92; it closed in 2003 and "
             "became flats.",
             "nl:Zeepfabriek Bousquet", ("Voorstraat 90 en 92", "schoorsteen", "2003")),
            ("Bacinol 2 (Braat)", "Hooikade 13",
             "The 1932 office of Braat's zinc works, since 2009 called Bacinol 2. Bacinol was the wartime code name "
             "for the penicillin the yeast factory worked on in secret.",
             "nl:Bacinol", ("Hooikade", "1932", "penicilline", "2009")),
            ("Watertoren", "Kalverbos 22",
             "A 29-metre water tower of 1895 by town architect M.A.C. Hartman, built for Delft's drinking water.",
             "nl:Watertoren (Delft Wateringsevest)", ("1895", "29 m", "Hartman")),
            ("Villa Vrijenban", "Nieuwe Plantage 58",
             "Town hall of the municipality of Vrijenban from 1878; after Vrijenban joined Delft in 1921 it was the "
             "mayor's residence until 1965.",
             "nl:Villa Vrijenban", ("Nieuwe Plantage 58", "1878", "1921", "1965")),
            ("De Porceleyne Fles (Royal Delft)", "Rotterdamseweg 196",
             "The pottery's factory and offices of the 1920s on the Rotterdamseweg, a listed complex where Delft Blue "
             "is still made.",
             "nl:De Porceleyne Fles", ("Rotterdamseweg", "rijksmonument")),
        ]),
    dict(
        id="secrets", section="Discover", title="Secrets of the city", era="1342–today",
        intro=("Small things that are easy to walk past: a bell that is hardly ever rung, a box nobody may open, a "
               "boathouse by a forger and a sign that does not mean what it says."),
        entries=[
            ("Nieuwe Kerk", "Markt 80",
             "During a restoration in 1997 a small box was found inside William of Orange's tomb, probably holding "
             "his intestines. It was put back unopened.",
             "nl:Praalgraf van Willem van Oranje", ("1997", "ingewanden", "ongeopend")),
            ("Oude Kerk", "Heilige Geestkerkhof 25",
             "The Trinitas bell of 1570 weighs almost 9,000 kilos and is rung only on special occasions, because its "
             "vibrations could damage the leaning tower.",
             "nl:Oude Kerk (Delft)", ("Trinitasklok", "1570", "9000 kilo")),
            ("Sint-Huybrechtstoren boathouse", "Oostplantsoen 140",
             "The boathouse built against the wall tower was designed by the master forger Han van Meegeren for the "
             "rowing club De Delftsche Sport.",
             "nl:Sint-Huybrechtstoren", ("Han van Meegeren", "boothuis", "De Delftsche Sport")),
            ("Visbank", "Cameretten 2",
             "The sign says 'Sinds 1342', but that is the year the count let Delft levy dues on fish, not the start "
             "of the market.",
             "nl:Visbank (Delft)", ("Sinds 1342", "Willem IV", "leges")),
            ("Oude Delft 95", "Oude Delft 95",
             "A main benchmark of NAP, the Dutch height datum, is set into the facade, placed during the levelling "
             "survey of 1875-1885.",
             "nl:Oude Delft 95", ("hoofdmerk van het NAP", "1875 tot 1885")),
            ("Stadhuis", "Markt 87",
             "The town hall of 1618-1620 by Hendrick de Keyser was built around Het Steen, the oldest building in "
             "Delft, which holds the old torture chamber and prison.",
             "nl:Stadhuis van Delft", ("Hendrick de Keyser", "Het Steen", "martelkamer")),
            ("Oostpoort", "Oostpoort 1",
             "A replica of the gate and its drawbridge stands in the Huis ten Bosch theme park in Japan.",
             "nl:Oostpoort (Delft)", ("Huis ten Bosch", "replica")),
            ("Koornbeurs", "Voldersgracht 1",
             "The carved animal heads on the facade got new, real horns in the restoration finished in 2005.",
             "nl:Koornbeurs (Delft)", ("dierkoppen", "echte hoorns", "2005")),
            ("Het Straatje", "Vlamingstraat 42",
             "The ivy on the left of Vermeer's painting looks blue because the yellow pigment he mixed into it has "
             "faded.",
             "nl:Het straatje", ("klimop", "blauwe kleur", "schijtgeel")),
        ]),
]
