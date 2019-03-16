consistentified_manufacturers = {
	#When getting publisher from SMDH, sometimes things are formatted in different ways than wanted (e.g. YELLING CASE), this is here to smooth things out
	#It's why we try to use licensee code instead, but that's not always there on 3DS
	#For what it's worth, it seems each publisher will format its own name consistently across all games it publishes, it just looks weird compared to how names are formatted elsewhere

	#Atlus USA, Inc. > Atlus USA?
	'CAPCOM': 'Capcom',
	'CIRCLE Ent.': 'Circle Entertainment',
	'SEGA': 'Sega',
	'Unspecified Author': None, #Homebrew might do this
	'VD-DEV': 'VD-Dev',
	'YouTube': 'Google', #Maybe I should change nintendo_common WB to YouTube. Oh well. Either way, this is the YouTube app, and hence Google
}
