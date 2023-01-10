
################################


from Config._const import ALPHABET, ALPHANUM_UNDERSCORE, BRAIN
from Config._words import WORDS
from Config._screennames import SCREEN_NAMES
import time, discord, random, csv, asyncio, copy, math, textwrap, traceback, os, importlib
from Config._functions import grammar_list, word_count, formatting_fix
from discord.ui import Button, View, Select

def HELP(PREFIX):
	return {
		"COOLDOWN": 1,
		"MAIN": "Test your typing speed",
		"FORMAT": "",
		"CHANNEL": 0,
		"USAGE": f"""Using `{PREFIX}typingtest` will prompt you to type a sequence of random common English words,
		and will report your speed and accuracy when you finish. Using `{PREFIX}typingtest top (page)` will show 
		the all-time personal best leaderboard.""".replace("\n", "").replace("\t", ""),
		"HIDE" : 0,
		"CATEGORY" : "Fun"
	}

PERMS = 2
ALIASES = ["GENVOTING", "GENERATEVOTING"]
REQ = []

RESPONSES_SAVE_PATH = "Commands/votinggenresponses.tsv"
RESPONSE_IDS_SAVE_PATH = "Commands/vottinggenresponseids.tsv"
SCREENS_SAVE_PATH = "Commands/votinggenscreens.tsv"
TEXT_SCREEN_PATH = "Commands/votinggentextscreens.txt"

VOTE_CHRS = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz!\"#$%&'()*+,-./0123456789:;<=>?@^_{|}~"

VALID_RESPONSE = "✔️"
NOT_VALID_RESPONSE = "❌"

async def integer_input (user, channel, message: str, min: int, max: int):

	input = None
	while input == None:

		await channel.send(message)
	
		msg = await BRAIN.wait_for('message', check=lambda m: (m.author == user and m.channel == channel))
		try:

			if msg.content.lower() == "cancel":
				break

			i = int(msg.content)
			if i < min or i > max:
				raise ValueError
			else:
				input = i
				break

		except ValueError:
			channel.send(f"You must provide an integer higher than {min} and lower than {max} (inclusive)!")

	return input

async def boolean_input (user, channel, message: str):

	input = None
	while input == None:

		await channel.send(message)
	
		msg = await BRAIN.wait_for('message', check=lambda m: (m.author == user and m.channel == channel))
		try:

			if msg.content.lower() == "cancel":
				return

			if msg.content.lower() in ["y", "yes", "true"]:
				input = True
				return
			elif msg.content.lower() in ["n", "no", "false"]:
				input = False
				return
			else:
				raise ValueError

		except ValueError:
			channel.send(f"You must either input 'Y' or 'N'!")

	return input

async def MAIN(message, args, level, perms, SERVER):

	# Finding TSV attachment which has all the responses
	if len(message.attachments) == 0: 
		await message.channel.send("You must include a TSV file!")
		return

	attachment = message.attachments[0]

	tsv_list = []

	# Try save the tsv file
	try:
		await attachment.save(RESPONSES_SAVE_PATH)
	except:
		pass

	# Open TSV and store results in a dictionary
	try: 
		with open(RESPONSES_SAVE_PATH, 'r', encoding='UTF-8') as tsv_file:
			reader = csv.reader(tsv_file, delimiter = "\t")
			for row in list(reader):
				tsv_list.append(row)
	except Exception:
		await message.channel.send(f"Error occured while attempting to open this TSV file: ```python\n{traceback.format_exc()}```")
		return

	# Remove the first row 
	tsv_list.pop(0)

	# Iterate through all rows of the TSV file
	# This checks for the first empty row and cuts the
	# TSV file off right before the first empty row.
	for row_num in range(len(tsv_list)):
		targeted_tsv_row = tsv_list[row_num]
		if targeted_tsv_row[0] == "":
			slice_obj = slice(row_num)
			tsv_list = tsv_list[slice_obj]
			break

	# Retrieve every response ID and put it in a dictionary
	responses_dict = {}
	for row in tsv_list:
		response_id = row[0]
		name = row[1] # Name of contestant who submitted
		response = row[2] # Response submitted
		validity = row[3] # Whether or not the response follows requirements
		responses_dict[response_id] = [name, response, validity]

	# Let user input the amount of sections they want
	response_amount = len(responses_dict)
	section_amount = integer_input(message.author, message.channel, "**How many sections should be created?** (Must be between 1 and 6)", 1, 6)
	if section_amount == None:
		await message.channel.send("Voting generation cancelled.")
		return

	section_titles = [ALPHABET[i] for i in range(section_amount)]

	# Let user decide whether they want to generate a megascreen or not
	megascreen_generation = boolean_input(message.author, message.channel, "**Should a megascreen be generated?** (Y/N)")
	if megascreen_generation == None:
		await message.channel.send("Voting generation cancelled.")
		return

	normal_section_titles = [ALPHABET[i] for i in range(section_amount)]
	megascreen_section_title = ""

	if megascreen_generation:
		megascreen_section_title = normal_section_titles.pop(-1)

	# Ask for amount of screens
	joined_section_titles = ", ".join(normal_section_titles)
	screen_size_target = integer_input(message.author, message.channel, f"For sections **{joined_section_titles}, what screen size are you aiming for?**", 1, response_amount)
	if screen_size == None:
		await message.channel.send("Voting generation cancelled.")
		return

	# Calculate amount of responses for each screen
	screen_amount = round(response_amount / amount)

	screen_division = [0] * screen_amount
	screen_increment = 0
	for i in range(response_amount):
		screen_division[screen_increment] += 1
		screen_increment += 1
		if screen_increment == screen_amount:
			screen_increment = 0

	# Generate screens
	sections_list = []
	for sec_n in range(section_amount):
		section_screen_names = copy.deepcopy(SCREEN_NAMES[sec_n])
		responses_shuffled = copy.deepcopy(list(responses_dict.keys()))
		random.shuffle(responses_shuffled)
	

		section_screen_amounts = []
		if megascreen == True and sec_n + 1 == sections:
			section_screen_amounts.append(section_amount)
		else:
			section_screen_amounts = screen_division

		# Go through every screen
		section_dict = {}
		for screen_size in screen_division:
			# Get screen name
			screen_name_lowercase = random.choice(section_screen_names) # Randomize screen name
			section_screen_names.remove(screen_name_lowercase) # Remove screen name from list
			screen_name = screen_name_lowercase.upper()
			screen_response_dict = {}
			# Add responses to dictionary
			for letter_num in range(screen_size):
				response_letter = VOTE_CHRS[letter_num] # Get letter
				response_id = responses_shuffled[0]
				screen_response_dict[response_letter] = response_id
				responses_shuffled.pop(0)
			section_dict[screen_name] = screen_response_dict
		sections_list.append(section_dict)

	# Generate TSV files
	header = ["Response ID", "Name", "Response"]
	with open(RESPONSE_IDS_SAVE_PATH, 'w', encoding='UTF-8', newline='') as f:
		f.write('\ufeff')
		writer = csv.writer(f, delimiter = "\t")
		writer.writerow(header)
		for response_id in list(responses_dict.keys()):
			writer.writerow([response_id, responses_dict[response_id][0], responses_dict[response_id][1]])

	header = ["Response ID", "Name", "Response"]
	with open(SCREENS_SAVE_PATH, 'w', encoding='UTF-8', newline='') as f:
		f.write('\ufeff')
		writer = csv.writer(f, delimiter = "\t")
		for section in sections_list: # Go through each section
			for screen_name in list(section.keys()): # Go through each screen
				writer.writerow([screen_name]) # Write the screen name at the top 
				screen_dict = section[screen_name]
				for response_letter in list(screen_dict.keys()): # Go through each response
					response_id = screen_dict[response_letter]
					# Find the response that correlates to the response id
					response = responses_dict[response_id][1]
					writer.writerow([response_letter, response, response_id]) # Write down the response letter, the response and the response's id
				# Add a line break
				writer.writerow([])

	# Create text screens with discord formatting
	lines = []
	for section in sections_list: # Go through each section
		lines.append(f"```SECTION {list(section.keys())[0][0]}```") # Add title of section
		for screen_name in list(section.keys()): # Go through each screen
			lines.append(f"__**{screen_name}**__") # Write the screen name at the top 
			screen_dict = section[screen_name]
			for response_letter in list(screen_dict.keys()): # Go through each response
				response_id = screen_dict[response_letter]
				# Find the response that correlates to the response id
				response = responses_dict[response_id][1]
				# Find the validity of the response and the emoji correlating to it 
				if responses_dict[response_id][2].upper() == "TRUE":
					valid_emoji = VALID_RESPONSE
				elif responses_dict[response_id][2].upper() == "FALSE":
					valid_emoji = NOT_VALID_RESPONSE
				else:
					valid_emoji = ""
				lines.append(f"**`{response_letter}`**`{valid_emoji}` {response}")
			# Add a line break
			lines.append("")
	with open(TEXT_SCREEN_PATH, 'w', encoding='UTF-8', newline='') as f:
		for line in lines:
			f.write(line)
			f.write('\n')

	# Send messages with files
	file_list = [
		discord.File(RESPONSE_IDS_SAVE_PATH),
		discord.File(SCREENS_SAVE_PATH),
		discord.File(TEXT_SCREEN_PATH)
	]

	await message.channel.send(content = "**Generated voting!**", files = file_list)
	



	

