# coding: utf-8
import requests
import re
import json


print 'Loading cards...'
r = requests.get('http://mtgjson.com/json/AllCards.json') #database of all cards in Magic: The Gathering
res = r.json()
while True:
	target_data = {}
	target = raw_input('Choose a card:')
	print 'Collecting target data...'
	for card in res:
		card = res[card]
		if card['name'] == target or card['name'].lower() == target:
			target_data['name'] = card['name']
			try:
				target_data['text'] = card['text']
			except: 
				target_data['text'] = ''
			try:
				target_data['colors'] = card['colors']
			except:
				pass
			try:
				target_data['cmc'] = card['cmc']  
			except:
				pass
			try:
				target_data['type'] = card['types']
			except:
				pass
			try:
				target_data['subtype'] = card['subtypes']
			except: 
				pass
			if target_data['type'] == ["Artifact", "Creature"] or target_data['type'] == ["Enchantment", "Creature"] or target_data['type'] == ["Creature"]:
				target_data['power'] = card['power']
				target_data['toughness'] = card['toughness']
	print target_data
	try:
		text1 = re.search('.*(?=\()', target_data['text'], re.DOTALL).group()
		text2 = re.search('(?<=\)).*', target_data['text'], re.DOTALL).group()
		text3 = text1 + text2
		target_data['text'] = text3
	except:
		pass

	#Card Score explanation:
	#The score for any given card starts at 100, and is raised or lowered based on it's similarity to the target card.
	#Card similarity is based on a number of weighted qualities:
	#	Type: If the type of the card matches then the score is increased by 2
	#	Converted Mana Cost: The score is decreased by the difference in converted mana cost (ex: a 4 mana card will lose 2 points if target card costs 2 mana)
	#	Subtype: If the card has a matching subtype then the score is increased by 1
	#	Power/Toughness: If the card is a creature, then the score is decreased by the difference in the card's power and toughness vs the target card.
	#	Color: The score is increased by 2 for each matching color.	
	#	Rules Text: The score is increased by 6 for each matching word.

	card_scores = {} 
	print 'Comparing cards...'
	for card in res:
		card = res[card]
		#remove cards that are not used in normal gameplay
		if card['layout'] != 'token' and card['layout'] != 'plane' and card['layout'] != 'scheme' and card['layout'] != 'phenomenon' and card['layout'] != 'vanguard':
			score = 100
			if card['name'] != target_data['name']:
				#type
				p = False
				for sub in card['types']:
					for su in target_data['type']: 
						if sub == su: 
							p = True
				if p != False:
					score += 2
				#converted mana cost
				try:
					score -= abs(target_data['cmc'] - card['cmc'])
				except:
					pass

				#subtype
				try:
					p = False
					for sub in card['subtypes']:
						for su in target_data['subtype']:
							if sub == su: 
								p = True
					if p != False:
						score += 1
						
				except:
					pass
				#power/toughness
				if (card['type'] == ["Artifact", "Creature"] or card['type'] == ["Enchantment", "Creature"] or card['type'] == ["Creature"]) and (target_data['type'] == ["Artifact", "Creature"] or target_data['type'] == ["Enchantment", "Creature"] or target_data['type'] == ["Creature"]):
					score -= abs(target_data['power'] - card['power'])
					score -= abs(target_data['toughness'] - card['toughness'])
				
				#color
				try:
					for color in card['colors']:
						for colorr in target_data['colors']:
							if color == colorr: 
								score += 2
				except:
					pass

				#rules text
				#parse out the card's rules text
				try:
					text1 = re.search('.*(?=\()', card['text'], re.DOTALL).group()
					text2 = re.search('(?<=\)).*', card['text'], re.DOTALL).group()
					text3 = text1 + text2
					card['text'] = text3
				except:
					pass
				#find number of matching words
				try:
					matches = set(target_data['text'].split()) & set(card['text'].split())
					score += len(matches) * 6
				except:
					pass
				card_scores[card['name']] = score
	results = sorted(card_scores, key=card_scores.__getitem__)
	results.reverse()
	for i in results[:10]:
		print i.encode('ascii','backslashreplace'), card_scores[i]
	
