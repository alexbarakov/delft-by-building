"""Quests: chains of riddles, each solved by finding a building on the map and clicking it.

Every riddle rests on a fact the map already carries and has checked: a story of a context layer (checked against
Wikipedia by s08_curated) or the map's own data (a year, a layer group). s12_quests.py resolves each answer to its
buildings, adds a hint with the answer's direction from the Markt, and checks that every step can be solved.

A step's answer is one of:
  ("story", layer id, address)  the buildings of that curated story
  ("rule", {...})               any building that meets every condition: groups=[(layer, group)], before=, after=
Optional per step: "photo" (today's photo of the answer as the clue), "layer" (the layer a hint opens),
"mode" (the colouring a hint switches to: period, floors, energy).
Levels: 1 easy (photos, plain hints), 2 medium (the layers do the work), 3 hard (fewer clues, rules).
"""


def T(en, nl):
    return dict(en=en, nl=nl)


def S(layer, address, riddle, hint, **kw):
    return dict(answer=("story", layer, address), layer=layer, riddle=riddle, hints=[hint], **kw)


QUESTS = [
    # ---------- easy ----------
    dict(id="markt", level=1,
         title=T("Around the Markt", "Rond de Markt"),
         intro=T("Five buildings on and around the great square. A gentle start.",
                 "Vijf gebouwen op en rond het grote plein. Een rustig begin."),
         steps=[
             S("trade", "Markt 11",
               T("The town weighed its goods here for centuries; the scales only stopped in 1960. The gable carries "
                 "the year 1770.",
                 "De stad woog hier eeuwenlang haar waren; pas in 1960 stopte het wegen. De gevel draagt het "
                 "jaartal 1770."),
               T("It is the town weigh house, the Waag, on the Markt.", "Het is de Waag, aan de Markt."), photo=True),
             S("secrets", "Markt 87",
               T("The town hall of 1618–1620 was built around something much older: Het Steen, the oldest "
                 "building in Delft, with the old torture chamber inside.",
                 "Het stadhuis van 1618–1620 werd gebouwd om iets dat veel ouder is: Het Steen, het oudste "
                 "gebouw van Delft, met de oude pijnkamer erin."),
               T("It closes one end of the Markt.", "Het sluit een kant van de Markt af."), photo=True),
             S("trade", "Markt 17",
               T("Delft butter changed hands in the town's own butter house, on the square.",
                 "Delftse boter werd verhandeld in het eigen boterhuis van de stad, aan het plein."),
               T("Look along the Markt for the Stadsboterhuis.", "Zoek langs de Markt het Stadsboterhuis.")),
             S("trade", "Markt 2",
               T("Two linked houses on a corner of the square are named after a candle maker; for almost two "
                 "hundred years one of them sold tobacco.",
                 "Twee verbonden huizen op een hoek van het plein heten naar een kaarsenmaker; bijna tweehonderd "
                 "jaar verkocht een ervan tabak."),
               T("They are called De Kaerskorf and De Maen.", "Ze heten De Kaerskorf en De Maen.")),
             S("orange", "Markt 80",
               T("Across the square from the town hall rises the burial church of the House of Orange. Its tower "
                 "is the second highest church tower in the Netherlands.",
                 "Tegenover het stadhuis staat de grafkerk van het Huis van Oranje. De toren is de op een na "
                 "hoogste kerktoren van Nederland."),
               T("The Nieuwe Kerk.", "De Nieuwe Kerk.")),
         ]),
    dict(id="vermeer", level=1,
         title=T("In Vermeer's footsteps", "In de voetsporen van Vermeer"),
         intro=T("Five places in the life of Johannes Vermeer, from his birth to his grave.",
                 "Vijf plekken uit het leven van Johannes Vermeer, van zijn geboorte tot zijn graf."),
         steps=[
             S("vermeer", "Voldersgracht 25",
               T("Begin where he began. In 1632 he was born at an inn his father ran, named after a flying animal, "
                 "on a canal just north of the Markt. Find the inn.",
                 "Begin waar hij begon. In 1632 werd hij geboren in de herberg van zijn vader, die naar een "
                 "vliegend dier heette, aan een gracht net ten noorden van de Markt. Vind de herberg."),
               T("The canal is the Voldersgracht; the inn is named after a fox with wings.",
                 "De gracht is de Voldersgracht; de herberg heet naar een vos met vleugels."), photo=True),
             S("vermeer", "Voldersgracht 21",
               T("A few doors along, the painters' guild of Saint Luke met from 1661, and he was one of its "
                 "headmen. The house there now is a replica of 2007: on the age map it looks young among old "
                 "neighbours.",
                 "Een paar deuren verder kwam vanaf 1661 het schildersgilde van Sint-Lucas bijeen, met hem als "
                 "een van de hoofdmannen. Het huis van nu is een replica uit 2007: op de kaart van bouwjaren is "
                 "het jong tussen oude buren."),
               T("Colour by period and look for a recent building on the Voldersgracht.",
                 "Kleur naar periode en zoek een nieuw gebouw aan de Voldersgracht."), mode="period"),
             S("vermeer", "Markt 80",
               T("He was baptised on 31 October 1632 in the church whose tower is the second highest in the "
                 "Netherlands.",
                 "Hij werd op 31 oktober 1632 gedoopt in de kerk met de op een na hoogste kerktoren van Nederland."),
               T("Its spire rises above everything else in the old town.",
                 "De spits steekt boven alles in de binnenstad uit.")),
             S("vermeer", "Vlamingstraat 42",
               T("In 2015 a historian identified the spot of his painting The Little Street: the house where his "
                 "aunt lived and sold tripe. Find it.",
                 "In 2015 vond een historicus de plek van zijn schilderij Het straatje: het huis waar zijn tante "
                 "woonde en pens verkocht. Vind het."),
               T("The street is the Vlamingstraat.", "De straat is de Vlamingstraat.")),
             S("vermeer", "Heilige Geestkerkhof 25",
               T("He died in December 1675 and was buried in the oldest church of the town, the one whose tower "
                 "leans.",
                 "Hij stierf in december 1675 en werd begraven in de oudste kerk van de stad, die met de scheve "
                 "toren."),
               T("Its tower, the second tallest in the old town, stands on the Oude Delft.",
                 "De toren, de op een na hoogste van de binnenstad, staat aan de Oude Delft."), photo=True),
         ]),
    dict(id="orange", level=1,
         title=T("Father of the fatherland", "Vader des vaderlands"),
         intro=T("William of Orange lived, worshipped and died in Delft. Follow him, and his family after him.",
                 "Willem van Oranje woonde, kerkte en stierf in Delft. Volg hem, en zijn familie na hem."),
         steps=[
             S("orange", "Sint Agathaplein 1",
               T("A former convent of Saint Agatha became his court in 1572. In 1584 he was shot here, and the "
                 "bullet holes are still in the wall.",
                 "Een voormalig klooster van Sint-Agatha werd in 1572 zijn hof. In 1584 werd hij hier "
                 "doodgeschoten, en de kogelgaten zitten nog in de muur."),
               T("It is the Prinsenhof, now the town museum.", "Het is het Prinsenhof, nu het stadsmuseum."),
               photo=True),
             S("orange", "Oude Delft 181",
               T("He went to church in the convent's chapel. After his death it went to the French-speaking "
                 "Walloon congregation.",
                 "Hij kerkte in de kapel van het klooster. Na zijn dood ging die naar de Franstalige Waalse "
                 "gemeente."),
               T("Look on the Oude Delft for the Waalse Kerk.", "Zoek aan de Oude Delft de Waalse Kerk.")),
             S("orange", "Oude Delft 167",
               T("A house of 1505 was later home to his son-in-law, Philips of Hohenlohe. Since 1645 the Delfland "
                 "water board has met in it.",
                 "Een huis uit 1505 was later het huis van zijn schoonzoon, Philips van Hohenlohe. Sinds 1645 "
                 "vergadert het hoogheemraadschap van Delfland er."),
               T("It is the Gemeenlandshuis, on the Oude Delft.", "Het is het Gemeenlandshuis, aan de Oude Delft.")),
             S("orange", "Markt 80",
               T("His tomb by Hendrick de Keyser was finished in 1623; beneath it lies the crypt of the House of "
                 "Orange-Nassau.",
                 "Zijn praalgraf van Hendrick de Keyser was in 1623 klaar; eronder ligt de grafkelder van het "
                 "Huis Oranje-Nassau."),
               T("The Nieuwe Kerk, on the Markt.", "De Nieuwe Kerk, aan de Markt.")),
             S("orange", "Heilige Geestkerkhof 25",
               T("On 24 April 2004, his birthday, a prince of the House of Orange married in the other great church of Delft.",
                 "Op 24 april 2004, zijn verjaardag, trouwde een prins uit het Huis van Oranje in de andere grote kerk van Delft."),
               T("The church with the leaning tower, the Oude Kerk.", "De kerk met de scheve toren, de Oude Kerk.")),
         ]),
    # ---------- medium ----------
    dict(id="delftblue", level=2,
         title=T("Blue and white", "Blauw en wit"),
         intro=T("How Chinese porcelain became Delft Blue, and where it went after that.",
                 "Hoe Chinees porselein Delfts blauw werd, en waar het daarna terechtkwam."),
         steps=[
             S("delftblue", "Oude Delft 39",
               T("Around 1631 the Delft chamber of the East India Company bought a house on the Oude Delft. The "
                 "Chinese porcelain it traded is what Delft potters copied.",
                 "Rond 1631 kocht de Delftse kamer van de VOC een huis aan de Oude Delft. Het Chinese porselein "
                 "waarin zij handelde, namen Delftse plateelbakkers na."),
               T("The Oost-Indisch Huis.", "Het Oost-Indisch Huis.")),
             S("delftblue", "Oosteinde 175",
               T("The pottery De Porceleyne Fles was founded in 1653 in a house that became a church in 1949. "
                 "Its hall is lined with glazed tiles.",
                 "Plateelbakkerij De Porceleyne Fles werd in 1653 gesticht in een huis dat in 1949 een kerk werd. "
                 "De hal is bekleed met geglazuurde tegels."),
               T("On the Oosteinde.", "Aan het Oosteinde.")),
             S("delftblue", "Rotterdamseweg 196",
               T("The same pottery became royal in 1919 and moved in the 1920s to the road to Rotterdam, where "
                 "Delft Blue is still made.",
                 "Dezelfde fabriek werd in 1919 koninklijk en verhuisde in de jaren 1920 naar de weg naar "
                 "Rotterdam, waar nog steeds Delfts blauw wordt gemaakt."),
               T("The Rotterdamseweg.", "De Rotterdamseweg.")),
             S("delftblue", "Wateringseweg 1",
               T("The walls of a head office of 1905 carry tile patterns and tableaux from that pottery. The "
                 "company it housed made yeast.",
                 "De wanden van een hoofdkantoor uit 1905 dragen tegels en tegeltableaus van die fabriek. Het "
                 "bedrijf dat er zat maakte gist."),
               T("The Gist en Spiritusfabriek, on the Wateringseweg.", "De Gist- en Spiritusfabriek, aan de Wateringseweg.")),
             S("delftblue", "Koornmarkt 81",
               T("A brewery house of about 1550 became miniature number 32 in the row of Delft Blue houses that "
                 "KLM gives its passengers.",
                 "Een brouwershuis van omstreeks 1550 werd huisje nummer 32 in de rij Delfts blauwe huisjes die "
                 "KLM aan passagiers geeft."),
               T("It is called De Handboog, on the Koornmarkt.", "Het heet De Handboog, aan de Koornmarkt.")),
         ]),
    dict(id="trade", level=2,
         title=T("Beer, meat and pawn tickets", "Bier, vlees en lommerdbriefjes"),
         intro=T("Before the potters, Delft lived on beer and markets. Find what is left of them.",
                 "Voor de plateelbakkers leefde Delft van bier en markten. Vind wat ervan over is."),
         steps=[
             S("trade", "Koornmarkt 64",
               T("A brewery house carries the year 1545 above its door; its brewery was one of the last in Delft "
                 "when it closed in 1848.",
                 "Een brouwershuis draagt het jaartal 1545 boven de deur; de brouwerij was een van de laatste van "
                 "Delft toen ze in 1848 sloot."),
               T("It is called Het Truweel, on the Koornmarkt.", "Het heet Het Truweel, aan de Koornmarkt.")),
             S("trade", "Voldersgracht 1",
               T("A meat hall was rebuilt in stone in 1650 over a medieval cellar. Carved animal heads look down "
                 "from its front; from 1871 it traded grain.",
                 "Een vleeshal werd in 1650 in steen herbouwd boven een middeleeuwse kelder. Gebeeldhouwde "
                 "dierenkoppen kijken neer van de gevel; vanaf 1871 werd er graan verhandeld."),
               T("The Vleeshal, now the Koornbeurs, on the Voldersgracht.",
                 "De Vleeshal, nu de Koornbeurs, aan de Voldersgracht.")),
             S("trade", "Burgwal 45",
               T("The town's pawn bank opened in 1676 and got its present front in 1769. It closed in 1922.",
                 "De stedelijke lommerd ging in 1676 open en kreeg in 1769 de huidige gevel. Hij sloot in 1922."),
               T("The Stadsleenbank, on the Burgwal.", "De Stadsleenbank, aan de Burgwal.")),
             S("trade", "Oude Delft 95",
               T("In 1717 Willem Hooft bought the brewery De Cimbel and replaced it with the largest patrician "
                 "house in Delft.",
                 "In 1717 kocht Willem Hooft brouwerij De Cimbel en zette er het grootste patriciërshuis van Delft "
                 "voor in de plaats."),
               T("It stands on the Oude Delft and is known by its number: 95.",
                 "Het staat aan de Oude Delft en heet naar zijn nummer: 95.")),
             S("trade", "Koornmarkt 67",
               T("A house that once belonged to the brewery Het Dubbelde Cruys was a painter's home from 1864 to "
                 "1894, and is now his museum.",
                 "Een huis van brouwerij Het Dubbelde Cruys was van 1864 tot 1894 het huis van een schilder, en is "
                 "nu zijn museum."),
               T("Museum Paul Tétar van Elven, on the Koornmarkt.", "Museum Paul Tétar van Elven, aan de Koornmarkt.")),
         ]),
    dict(id="powder", level=2,
         title=T("Powder, walls and gates", "Kruit, muren en poorten"),
         intro=T("How Delft stored its gunpowder, lost part of the town to it, and guarded itself.",
                 "Hoe Delft zijn kruit bewaarde, er een deel van de stad door verloor en zich verdedigde."),
         steps=[
             S("thunderclap", "Paardenmarkt 1",
               T("On 12 October 1654 the powder store of Holland, in a former convent, exploded and flattened the "
                 "north-east of the town. On the convent site an artillery magazine rose; the shooting range "
                 "beside it became a market for horses. Find the magazine.",
                 "Op 12 oktober 1654 ontplofte het kruitmagazijn van Holland in een voormalig klooster en "
                 "verwoestte het noordoosten van de stad. Op de kloosterplek verrees een artilleriemagazijn; de "
                 "schuttersdoelen ernaast werden een paardenmarkt. Vind het magazijn."),
               T("The square is still called the Paardenmarkt.", "Het plein heet nog steeds de Paardenmarkt.")),
             S("thunderclap", "Schiekade 1",
               T("After the blast the new powder house was built far outside the walls: two towers in a moat, "
                 "with copper fittings against sparks and a roof meant to blow off. This is how it looks today.",
                 "Na de ramp kwam het nieuwe kruithuis ver buiten de muren: twee torens in een gracht, met koperen "
                 "beslag tegen vonken en een dak dat moest wegvliegen. Zo ziet het er nu uit."),
               T("Beside the Schie, on the Schiekade.", "Aan de Schie, op de Schiekade."), photo=True),
             S("defences", "Oostpoort 1",
               T("Delft had eight town gates. Only one is left, and a copy of it stands in a theme park in Japan.",
                 "Delft had acht stadspoorten. Er is er nog één, en een kopie ervan staat in een pretpark in Japan."),
               T("It is called the East Gate: the Oostpoort.", "Hij heet de Oostpoort.")),
             S("defences", "Phoenixstraat 112",
               T("Fifteen windmills once stood on the town walls. The last one, built on a bastion in 1679, still "
                 "grinds grain.",
                 "Op de stadsmuren stonden ooit vijftien molens. De laatste, in 1679 op een bolwerk gebouwd, maalt "
                 "nog steeds graan."),
               T("Molen De Roos, on the Phoenixstraat.", "Molen De Roos, aan de Phoenixstraat.")),
             S("defences", "Korte Geer 1",
               T("In 1811 Napoleon visited the arsenal of the States of Holland and took two decorated cannons "
                 "back to Paris.",
                 "In 1811 bezocht Napoleon het arsenaal van de Staten van Holland en nam twee versierde kanonnen "
                 "mee naar Parijs."),
               T("Its name is Latin for arsenal: the Armamentarium, on the Korte Geer.",
                 "De naam is Latijn voor wapenhuis: het Armamentarium, aan de Korte Geer.")),
         ]),
    dict(id="science", level=2,
         title=T("Engineers' town", "Ingenieursstad"),
         intro=T("From a royal academy in a canal house to a reactor on the campus.",
                 "Van een koninklijke academie in een grachtenhuis tot een reactor op de campus."),
         steps=[
             S("science", "Oude Delft 95",
               T("From 1842 to 1952 the largest patrician house in Delft was the main building of the Royal "
                 "Academy and the schools that grew out of it.",
                 "Van 1842 tot 1952 was het grootste patriciërshuis van Delft het hoofdgebouw van de Koninklijke "
                 "Akademie en de scholen die eruit groeiden."),
               T("On the Oude Delft, number 95.", "Aan de Oude Delft, nummer 95.")),
             S("science", "Oude Delft 118",
               T("A chapel of around 1400 served as the university's aula from the 1920s until 1966.",
                 "Een kapel van omstreeks 1400 was van de jaren 1920 tot 1966 de aula van de hogeschool."),
               T("The Sint-Hippolytuskapel, on the Oude Delft.", "De Sint-Hippolytuskapel, aan de Oude Delft.")),
             S("science", "Julianalaan 134",
               T("A chemistry building of 1918–1923 was never fully used for chemistry. In 1939 it stored "
                 "yellowcake from the Belgian Congo; after 2008 the architecture faculty moved in.",
                 "Een scheikundegebouw uit 1918–1923 werd nooit helemaal voor scheikunde gebruikt. In 1939 lag er "
                 "yellowcake uit Belgisch-Congo; na 2008 trok de faculteit Bouwkunde erin."),
               T("The Rode Scheikunde, on the Julianalaan.", "De Rode Scheikunde, aan de Julianalaan.")),
             S("science", "Mekelweg 5",
               T("A concrete auditorium of 1966 juts out 34.5 metres and rests mainly on two columns.",
                 "Een betonnen zaal uit 1966 kraagt 34,5 meter uit en rust vooral op twee kolommen."),
               T("The Aula, on the Mekelweg. Colour by period: it falls in 1965–1984.",
                 "De Aula, aan de Mekelweg. Kleur naar periode: hij valt in 1965–1984."), mode="period"),
             S("science", "Mekelweg 15",
               T("Since 1963 the only nuclear reactor on a Dutch university campus has run here.",
                 "Sinds 1963 draait hier de enige kernreactor op een Nederlandse universiteitscampus."),
               T("The Hoger Onderwijs Reactor, on the Mekelweg.", "De Hoger Onderwijs Reactor, aan de Mekelweg.")),
         ]),
    # ---------- hard ----------
    dict(id="students", level=3,
         title=T("Students and secrets", "Studenten en geheimen"),
         intro=T("Student clubs, a hidden mark and a forger. The first hint only gives a direction.",
                 "Studentenclubs, een verborgen teken en een vervalser. De eerste hint geeft alleen een richting."),
         steps=[
             S("students", "Oude Delft 35",
               T("Students have lived here since 1891: it is the oldest student house still in use in the Netherlands.",
                 "Hier wonen sinds 1891 studenten: het is het oudste studentenhuis van Nederland dat nog in gebruik is."),
               T("Oude Delft, a low number.", "Oude Delft, een laag nummer.")),
             S("students", "Oude Delft 89",
               T("A student house since 1947 is named after the cheapest seats in a theatre.",
                 "Een studentenhuis sinds 1947 heet naar de goedkoopste plaatsen in de schouwburg."),
               T("Oude Delft again.", "Weer de Oude Delft.")),
             S("students", "Phoenixstraat 30",
               T("A students' society lost its building to fire in 1876 and began a new one the same year.",
                 "Een studentensociëteit verloor in 1876 haar gebouw door brand en begon datzelfde jaar aan een "
                 "nieuw."),
               T("The street shares its name with the bird that rises from its ashes.",
                 "De straat draagt de naam van de vogel die uit zijn as herrijst.")),
             S("secrets", "Oostplantsoen 140",
               T("A boathouse against a medieval wall tower was designed by the master forger Han van Meegeren, "
                 "for a rowing club.",
                 "Een botenhuis tegen een middeleeuwse muurtoren werd ontworpen door meestervervalser Han van "
                 "Meegeren, voor een roeivereniging."),
               T("The tower stands on the Oostplantsoen.", "De toren staat aan het Oostplantsoen.")),
             S("secrets", "Oude Delft 95",
               T("A main benchmark of the Dutch height datum is set into one facade, placed during the levelling "
                 "survey of 1875–1885. You may have met the house already.",
                 "In één gevel zit een hoofdpeilmerk van het NAP, geplaatst bij de waterpassing van 1875–1885. "
                 "Misschien ken je het huis al."),
               T("The largest patrician house on the Oude Delft.", "Het grootste patriciërshuis aan de Oude Delft.")),
         ]),
    dict(id="charity", level=3,
         title=T("Hidden faith, quiet charity", "Verborgen geloof, stille liefdadigheid"),
         intro=T("A shelter, an almshouse, an orphanage and two houses of prayer, one of them hidden from the street.",
                 "Een opvang, een hofje, een weeshuis en twee gebedshuizen, waarvan één verborgen voor de straat."),
         steps=[
             S("charity", "Molslaan 104",
               T("Built around 1465 as a shelter for the homeless, it survived the fire of 1536 and became a "
                 "home for foundlings in 1579.",
                 "Rond 1465 gebouwd als opvang voor daklozen, overleefde het de brand van 1536 en werd het in "
                 "1579 een vondelingenhuis."),
               T("Colour by period: it is among the very oldest. The street is the Molslaan.",
                 "Kleur naar periode: het hoort bij de alleroudste. De straat is de Molslaan."), mode="period"),
             S("charity", "Oranje Plantage 58",
               T("In 1605 the owners of a brewery founded a courtyard of almshouses for elderly Catholic women. "
                 "It carries the brewery's name.",
                 "In 1605 stichtten de eigenaren van een brouwerij een hofje voor oude katholieke vrouwen. Het "
                 "draagt de naam van de brouwerij."),
               T("The Oranje Plantage.", "De Oranje Plantage.")),
             S("charity", "Oude Delft 112",
               T("From 1578 to 1954, almost four hundred years, girls who had lost a parent grew up here.",
                 "Van 1578 tot 1954, bijna vierhonderd jaar, groeiden hier meisjes op die een ouder hadden "
                 "verloren."),
               T("The Oude Delft.", "De Oude Delft.")),
             S("faith", "Bagijnhof 21",
               T("A church of 1743 hidden behind a beguinage, reached through a house of the 1600s.",
                 "Een kerk uit 1743, verborgen achter een begijnhof en bereikbaar door een huis uit de 17e eeuw."),
               T("The Bagijnhof.", "Het Bagijnhof.")),
             S("faith", "Koornmarkt 12",
               T("A house of prayer of 1861–1862 fell out of use after 1945; since 2006 services are held in it "
                 "again.",
                 "Een gebedshuis uit 1861–1862 raakte na 1945 buiten gebruik; sinds 2006 worden er weer diensten "
                 "gehouden."),
               T("The Koornmarkt.", "De Koornmarkt.")),
         ]),
    dict(id="layers", level=3,
         title=T("Read the layers", "Lees de lagen"),
         intro=T("Riddles with many right answers. Only the map's colours and layers will get you there.",
                 "Raadsels met veel goede antwoorden. Alleen de kleuren en lagen van de kaart brengen je er."),
         steps=[
             dict(answer=("rule", dict(before=1536)), mode="period",
                  riddle=T("In 1536 a great fire destroyed much of Delft. Find any building that is older.",
                           "In 1536 verwoestte een grote brand een groot deel van Delft. Vind een gebouw dat ouder is."),
                  hints=[T("Colour by period and click 'Before 1536' to see only those.",
                           "Kleur naar periode en klik op 'Vóór 1536' om alleen die te zien.")]),
             dict(answer=("rule", dict(groups=[("gables", "klok")])), layer="gables",
                  riddle=T("The monument register names a bell or neck gable for only about a dozen houses in Delft. Find one.",
                           "Het monumentenregister noemt bij maar een stuk of twaalf huizen in Delft een klok- of "
                           "halsgevel. Vind er een."),
                  hints=[T("The Gables layer has a colour for each kind of top.",
                           "De laag Gevels heeft een kleur voor elk soort top.")]),
             dict(answer=("rule", dict(groups=[("kadaster1832", "drink")])), layer="kadaster1832",
                  riddle=T("In 1832 the land register named innkeepers, tavern keepers and distillers among the "
                           "owners. Find a building on one of their plots.",
                           "In 1832 noemde het kadaster kasteleins, tappers en branders onder de eigenaren. Vind een "
                           "gebouw op een van hun percelen."),
                  hints=[T("Open Delft in 1832 and keep only the inns and taverns.",
                           "Open Delft in 1832 en laat alleen de herbergen en tapperijen zien.")]),
             dict(answer=("rule", dict(groups=[("heritage", "Rijksmonument")], after=1900)), layer="heritage",
                  riddle=T("Not every national monument is old. Find one built after 1900.",
                           "Niet elk rijksmonument is oud. Vind er een van na 1900."),
                  hints=[T("Open Protected heritage and keep only the national monuments; the youngest are on "
                           "the right of the timeline.",
                           "Open Beschermd erfgoed en laat alleen de rijksmonumenten zien; de jongste staan rechts "
                           "op de tijdlijn.")]),
             dict(answer=("rule", dict(groups=[("heritage", "waardevol")], before=1700)), layer="heritage",
                  riddle=T("A few buildings older than 1700 are not listed at all; only the city's design rules count "
                           "them as worth keeping. Find one.",
                           "Een paar gebouwen van voor 1700 zijn helemaal geen monument; alleen de welstandsregels van "
                           "de gemeente noemen ze waardevol. Vind er een."),
                  hints=[T("In Protected heritage keep only 'Valued by the city', then look for the oldest.",
                           "Laat in Beschermd erfgoed alleen 'Cultuurhistorisch waardevol' zien en zoek de oudste.")]),
         ]),
]
