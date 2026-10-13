"""Quests: chains of riddles, each solved by finding a building on the map and clicking it.

Every riddle rests on a fact the map already carries and has checked: a story of a context layer (checked against
Wikipedia by s08_curated), a 'Did you know' fact (s11_facts) or the map's own data (a year, a layer group).
s12_quests.py resolves each answer to its buildings and checks the hints point at a layer that contains them.

A step's answer is one of:
  ("story", layer id, address)   the buildings of that curated story
  ("group", layer id, group key) any building of a layer group
  ("before", year)               any building built before that year
Optional per step: "photo" (show today's photo of the answer as the clue), "layer" (the layer a hint opens),
"mode" (the colouring a hint switches to: period, floors, energy).
"""

QUESTS = [
    dict(
        id="vermeer",
        title=dict(en="In Vermeer's footsteps", nl="In de voetsporen van Vermeer"),
        intro=dict(en="Five places in the life of Johannes Vermeer, from his birth to his grave.",
                   nl="Vijf plekken uit het leven van Johannes Vermeer, van zijn geboorte tot zijn graf."),
        steps=[
            dict(answer=("story", "vermeer", "Voldersgracht 25"), layer="vermeer",
                 riddle=dict(en="Begin where he began. In 1632 a boy was born at an inn named after a flying animal, "
                                "on the canal of the cloth fullers just north of the Markt. Find the inn.",
                             nl="Begin waar hij begon. In 1632 werd een jongen geboren in een herberg die naar een "
                                "vliegend dier heette, aan de gracht van de lakenvolders net ten noorden van de Markt. "
                                "Vind de herberg."),
                 hints=[dict(en="The canal is the Voldersgracht; the inn's name is a fox with wings.",
                             nl="De gracht is de Voldersgracht; de herberg heet naar een vos met vleugels.")]),
            dict(answer=("story", "vermeer", "Voldersgracht 21"), layer="vermeer", mode="period",
                 riddle=dict(en="A few doors along, the painters' guild of Saint Luke met from 1661, and he was one of "
                                "its headmen. The house you can see is a replica of 2007: on the age map it looks young "
                                "among old neighbours.",
                             nl="Een paar deuren verder kwam vanaf 1661 het schildersgilde van Sint-Lucas bijeen, met "
                                "hem als een van de hoofdmannen. Het huis dat er nu staat is een replica uit 2007: op "
                                "de kaart van bouwjaren is het jong tussen oude buren."),
                 hints=[dict(en="Colour the city by period and look for a recent building on the same canal.",
                             nl="Kleur de stad naar periode en zoek een nieuw gebouw aan dezelfde gracht.")]),
            dict(answer=("story", "vermeer", "Markt 80"), layer="vermeer", mode="floors",
                 riddle=dict(en="He was baptised on 31 October 1632 in a church whose tower is the second highest in "
                                "the Netherlands.",
                             nl="Hij werd op 31 oktober 1632 gedoopt in een kerk met de op een na hoogste kerktoren "
                                "van Nederland."),
                 hints=[dict(en="Colour the city by floors: it is the tallest thing in the old town.",
                             nl="Kleur de stad naar verdiepingen: het is het hoogste van de binnenstad.")]),
            dict(answer=("story", "vermeer", "Vlamingstraat 42"), layer="vermeer",
                 riddle=dict(en="In 2015 a historian identified the spot of his painting The Little Street: the house "
                                "where his aunt lived and sold tripe, east of the Markt. Find it.",
                             nl="In 2015 vond een historicus de plek van zijn schilderij Het straatje: het huis waar zijn "
                                "tante woonde en pens verkocht, ten oosten van de Markt. Vind het."),
                 hints=[dict(en="The street is named after Flemish weavers: the Vlamingstraat.",
                             nl="De straat heet naar Vlaamse wevers: de Vlamingstraat.")]),
            dict(answer=("story", "vermeer", "Heilige Geestkerkhof 25"), layer="vermeer",
                 riddle=dict(en="He died in December 1675 and was buried in the oldest church of the town, the one "
                                "whose tower leans.",
                             nl="Hij stierf in december 1675 en werd begraven in de oudste kerk van de stad, die met de "
                                "scheve toren."),
                 hints=[dict(en="The tower stands 1.96 metres out of plumb, by the Oude Delft.",
                             nl="De toren staat 1,96 meter uit het lood, aan de Oude Delft.")]),
        ]),
    dict(
        id="powder",
        title=dict(en="Powder, walls and gates", nl="Kruit, muren en poorten"),
        intro=dict(en="How Delft stored its gunpowder, lost part of the town to it, and guarded itself.",
                   nl="Hoe Delft zijn kruit bewaarde, er een deel van de stad door verloor en zich verdedigde."),
        steps=[
            dict(answer=("story", "thunderclap", "Paardenmarkt 1"), layer="thunderclap",
                 riddle=dict(en="On 12 October 1654 the powder store of Holland, in a former convent, exploded and "
                                "flattened the north-east of the town. On the convent site an artillery magazine rose; "
                                "the shooting range beside it became a market for horses. Find the magazine.",
                             nl="Op 12 oktober 1654 ontplofte het kruitmagazijn van Holland in een voormalig klooster "
                                "en verwoestte het noordoosten van de stad. Op de kloosterplek verrees een "
                                "artilleriemagazijn; de schuttersdoelen ernaast werden een paardenmarkt. Vind het "
                                "magazijn."),
                 hints=[dict(en="The square is still called the Paardenmarkt.",
                             nl="Het plein heet nog steeds de Paardenmarkt.")]),
            dict(answer=("story", "thunderclap", "Schiekade 1"), layer="thunderclap", photo=True,
                 riddle=dict(en="After the blast the new powder house was built far outside the walls: two towers in a "
                                "moat, with copper fittings against sparks and a roof meant to blow off. This is how it "
                                "looks today.",
                             nl="Na de ramp kwam het nieuwe kruithuis ver buiten de muren: twee torens in een gracht, met "
                                "koperen beslag tegen vonken en een dak dat moest wegvliegen. Zo ziet het er nu uit."),
                 hints=[dict(en="Well south of the old town, beside the Schie.",
                             nl="Een flink eind ten zuiden van de binnenstad, aan de Schie.")]),
            dict(answer=("story", "defences", "Oostpoort 1"), layer="defences",
                 riddle=dict(en="Delft had eight town gates. Only one is left, and a copy of it stands in a theme park "
                                "in Japan.",
                             nl="Delft had acht stadspoorten. Er is er nog één, en een kopie ervan staat in een "
                                "pretpark in Japan."),
                 hints=[dict(en="It guards the east of the old town, over the water.",
                             nl="Hij staat aan de oostkant van de binnenstad, aan het water.")]),
            dict(answer=("story", "defences", "Phoenixstraat 112"), layer="defences",
                 riddle=dict(en="Fifteen windmills once stood on the town walls. The last one, built on a bastion in "
                                "1679, still grinds grain.",
                             nl="Op de stadsmuren stonden ooit vijftien molens. De laatste, in 1679 op een bolwerk "
                                "gebouwd, maalt nog steeds graan."),
                 hints=[dict(en="On the west side, where trams now run past the old wall.",
                             nl="Aan de westkant, waar nu trams langs de oude muur rijden.")]),
            dict(answer=("story", "defences", "Korte Geer 1"), layer="defences",
                 riddle=dict(en="In 1811 an emperor visited the arsenal of the States of Holland and took two "
                                "decorated cannons back to Paris.",
                             nl="In 1811 bezocht een keizer het arsenaal van de Staten van Holland en nam twee versierde "
                                "kanonnen mee naar Parijs."),
                 hints=[dict(en="Its Latin name means armoury; it stands on the Korte Geer.",
                             nl="De Latijnse naam betekent wapenhuis; het staat aan de Korte Geer.")]),
        ]),
    dict(
        id="layers",
        title=dict(en="Read the layers", nl="Lees de lagen"),
        intro=dict(en="Riddles with more than one right answer: use the map's colours and layers to find one.",
                   nl="Raadsels met meer dan één goed antwoord: gebruik de kleuren en lagen van de kaart."),
        steps=[
            dict(answer=("before", 1536), mode="period",
                 riddle=dict(en="In 1536 a great fire destroyed much of Delft. Find any building that is older.",
                             nl="In 1536 verwoestte een grote brand een groot deel van Delft. Vind een gebouw dat ouder "
                                "is."),
                 hints=[dict(en="Colour by period and click 'Before 1536' to see only those.",
                             nl="Kleur naar periode en klik op 'Vóór 1536' om alleen die te zien.")]),
            dict(answer=("group", "gables", "trap"), layer="gables",
                 riddle=dict(en="Find a listed house that climbs to its top in steps.",
                             nl="Vind een monumentaal huis waarvan de gevel in treden omhoog loopt."),
                 hints=[dict(en="The Gables layer has a colour for each kind of top.",
                             nl="De laag Gevels heeft een kleur voor elk soort top.")]),
            dict(answer=("group", "kadaster1832", "potter"), layer="kadaster1832",
                 riddle=dict(en="In 1832 the land register still listed Delftware potters among the owners. Find a "
                                "building on a plot that belonged to one.",
                             nl="In 1832 stonden er in het kadaster nog plateelbakkers als eigenaar. Vind een gebouw op "
                                "een perceel van een van hen."),
                 hints=[dict(en="Open the layer Delft in 1832 and keep only the potters.",
                             nl="Open de laag Delft in 1832 en laat alleen de plateelbakkers zien.")]),
            dict(answer=("story", "charity", "Van der Mastenstraat 24"), layer="charity",
                 riddle=dict(en="In 1575 Pieter Sasbout founded a courtyard of almshouses for married couples over fifty "
                                "without children. Find it.",
                             nl="In 1575 stichtte Pieter Sasbout een hofje voor kinderloze echtparen boven de vijftig. "
                                "Vind het."),
                 hints=[dict(en="It is in the layer of almshouses and orphanages.",
                             nl="Het staat in de laag hofjes en weeshuizen.")]),
            dict(answer=("story", "trade", "Cameretten 2"), layer="trade", photo=True,
                 riddle=dict(en="A sign here says 'Sinds 1342', but that is the year the count let Delft levy dues on "
                                "fish, not the start of the market. Fish was sold here for centuries, until 2025.",
                             nl="Een bord hier zegt 'Sinds 1342', maar dat is het jaar waarin de graaf Delft recht gaf "
                                "op vis te heffen, niet het begin van de markt. Hier werd eeuwenlang vis verkocht, tot "
                                "2025."),
                 hints=[dict(en="An open hall facing the old meat hall, a few steps from the Markt.",
                             nl="Een open hal tegenover de oude Vleeshal, een paar stappen van de Markt.")]),
        ]),
]
