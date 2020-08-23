#!/usr/bin/env python3
subtitles = {
	'Baku Baku Animal': 'World Zookeeper Contest',
	'Bonk III': "Bonk's Big Adventure",
	'Catz': 'Your Virtual Petz Palz',
	'Clockwork Knight': "Pepperouchau's Adventure",
	'Clockwork Knight 2': "Pepperouchau's Adventure", #Why would the sequel have the same subtitle…
	'Croc': 'Legend of the Gobbos',
	'Cybernoid II': 'The Revenge',
	'Driver 2': 'Back on the Streets',
	'Ehrgeiz': 'God Bless the Ring',
	'F-22 Interceptor': 'Advanced Tactical Fighter',
	'Fantasy Zone II': 'The Tears of Opa-Opa',
	'Galaga': 'Demons of Death',
	'H.E.R.O.': 'Helicopter Emergency Rescue Operation',
	'Kirby 64': 'The Crystal Shards',
	"King's Quest V": 'Absence Makes the Heart Go Yonder',
	'Landstalker': 'The Treasures of King Nole',
	'LEGO Island 2': "The Brickster's Revenge",
	'Lode Runner II': 'The Bungeling Strikes Back',
	'Madou Monogatari I': '3-Tsu no Madoukyuu',
	'MegaMania': 'A Space Nightmare',
	'Metal Gear 2': 'Solid Snake',
	'Metal Slug 2': 'Super Vehicle-001/II',
	'Metal Slug': 'Super Vehicle-001',
	'Metal Slug X': 'Super Vehicle-001',
	'Miner 2049er': 'Starring Bounty Bob',
	"Montezuma's Revenge": 'Featuring Panama Joe',
	'My Paint': 'The Animated Paint Program!',
	'Myth': 'History in the Making',
	'Neo Drift Out': 'New Technology',
	'Neo DriftOut': 'New Technology', #It seems we have an alternate name formatting on our hands… I'll just treat these separately
	"Neo-Geo Cup '98": 'The Road to the Victory',
	'Persona 2': 'Eternal Punishment',
	'Pitfall II': 'Lost Caverns', #Sometimes seen with definite article
	'Pitfall!': "Pitfall Harry's Jungle Adventure",
	'Pit Fighter': 'The Ultimate Competition',
	'Pokemon Box': 'Ruby & Sapphire',
	'Pokemon XD': 'Gale of Darkness',
	'Prince of Persia 2': 'The Shadow and the Flame',
	'Rainbow Islands': 'The Story of Bubble Bobble 2',
	'Resident Evil 3': 'Nemesis',
	'Ristar': 'The Shooting Star',
	'San Francisco Rush': 'Extreme Racing',
	'SimAnt': 'The Electronic Ant Colony',
	'SimCity 2000': 'The Ultimate City Simulator',
	'SimEarth': 'The Living Planet',
	'Street Fighter Alpha': "Warriors' Dreams",
	'Street Fighter II': 'The World Warrior',
	'Super Air Zonk': 'Rockabilly-Paradise',
	'Super Mario RPG': 'Legend of the Seven Stars',
	'Super Street Fighter II': 'The New Challengers',
	'The 11th Hour': 'The Sequel to The 7th Guest',
	"The King of Fighters '98": 'The Slugfest',
	"The King of Fighters '99": 'Millennium Battle',
	'Virtua Tennis': 'Sega Professional Tennis',
	'Wave Race 64': 'Kawasaki Jet Ski', #Well sort of, I guess later releases (i.e. VC) have license removed
	'Ys III': 'Wanderers from Ys',
	'Zool': "Ninja of the 'Nth' Dimension",
	'Zooo': 'Action Puzzle Game',
}

non_standard_subtitles = {
	#Where it's not just separated by a - or :, maybe this doesn't belong here
	#Yeah nah like how would I use this, it's more for name_consistency if anything
	'Batman Forever The Arcade Game': 'Batman Forever',
	'Ys - Wanderers from Ys': 'Ys III',
	'Miner 2049er Starring Bounty Bob': 'Miner 2049er',
	'Chaotix Featuring Knuckles the Echidna': 'Knuckles\' Chaotix',
	'Circus Atari': 'Circus',
	'David Crane\'s Pitfall II - Lost Caverns': 'Pitfall II',
	'Q*bert for Game Boy': 'Q*bert',
	'Montezuma\'s Revenge featuring Panama Joe': 'Montezuma\'s Revenge',
	'Ironman Ivan Stewart\'s Super Off-Road': 'Super Off-Road',
	'Ivan \'Ironman\' Stewart\'s Super Off Road': 'Super Off-Road',
}

arcade_names_with_alternate_titles = {
	#This shouldn't exist and should be parsed by mame_machines
	'Art of Fighting / Ryuuko no Ken': 'Art of Fighting',
	'Voltage Fighter - Gowcaizer / Choujin Gakuen Gowcaizer': 'Voltage Fighter - Gowcaizer',
	'The King of Fighters \'98 - The Slugfest / King of Fighters \'98 - Dream Match Never Ends': 'The King of Fighters \'98',
	'Space Invaders / Space Invaders M': 'Space Invaders',
	'Puzzle Bobble 2 / Bust-A-Move Again': 'Puzzle Bobble 2',
	'Puzzle Bobble / Bust-A-Move': 'Puzzle Bobble',
	'Circus / Acrobat TV': 'Circus',
	'Blue\'s Journey / Raguy': 'Blue\'s Journey',
}

names_with_alternate_titles = {
	#This shouldn't exist and should be parsed in the roms stuff
	'After Burner Complete ~ After Burner': 'After Burner Complete',
	'Air-Sea Battle ~ Target Fun': 'Air-Sea Battle',
	'Bachelor Party ~ Gigolo': 'Bachelor Party',
	'Ballz 3D - Fighting at Its Ballziest ~ Ballz 3D - The Battle of the Ballz': 'Ballz 3D - Fighting at Its Ballziest',
	'Bare Knuckle - Ikari no Tekken ~ Streets of Rage': 'Streets of Rage',
	'US Ski Team Skiing ~ Skiing': 'US Ski Team Skiing',
	'The Earth Defense ~ Earth Defend': 'The Earth Defense',
	'Space War ~ Space Combat': 'Space War',
	'Stack-Up ~ Block': 'Stack-Up',
	'Sonic 3D Blast ~ Sonic 3D Flickies\' Island': 'Sonic 3D Blast',
	'Space Harrier 3-D ~ Space Harrier 3D': 'Space Harrier 3D',
	'Senjou no Ookami II ~ Mercs': 'Mercs',
	'Shadow Squadron ~ Stellar Assault': 'Stellar Assault',
	'G-Sonic ~ Sonic Blast': 'Sonic Blast',
	'Gyromite ~ Gyro': 'Gyromite',
	'Indy 500 ~ Race': 'Indy 500',
	'Breakout ~ Breakaway IV': 'Breakout',
	'Bubble Bobble ~ Dragon Maze': 'Bubble Bobble',
	'NASL Soccer ~ Soccer': 'NASL Soccer',
	'NBA Basketball ~ Basketball': 'NBA Basketball',
	'NFL Football ~ Football': 'NFL Football',
	'NHL Hockey ~ Hockey': 'Hockey',
	'Parasquad ~ Zaxxon\'s Motherbase 2000': 'Zaxxon\'s Motherbase 2000',
	'Chaotix ~ Knuckles\' Chaotix': 'Knuckles\' Chaotix',
	'Columns ~ Shapes and Columns': 'Columns',
	'Cyber Brawl ~ Cosmic Carnage': 'Cosmic Carnage',
	'Daimakaimura ~ Ghouls\'n Ghosts': 'Ghouls\'n Ghosts',
	'Major League Baseball ~ Baseball ~ Big League Baseball': 'Major League Baseball',
}
