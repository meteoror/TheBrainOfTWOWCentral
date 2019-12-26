from Config._links import LINKS
from Config._const import PREFIX
from Config._functions import grammar_list

HELP = {
	"COOLDOWN": 1,
	"MAIN": "Provides useful links to community sheets and/or projects",
	"FORMAT": "(link)",
	"CHANNEL": 1,
	"USAGE": f"""Using `{PREFIX}link` returns a list of available links. Including one of those as the `(link)` 
	parameter will grant you that link, and information on it.""".replace("\n", "").replace("\t", "")
}

PERMS = 1 # Member
ALIASES = ["L"]
REQ = []

async def MAIN(message, args, level, perms):
	# Note: this takes data from Config/_links.py, which is where I store all link info

	if level == 1: # If it's just `tc/l`, provide a list of the links available
		await message.channel.send(f"Here's a list of link commands available:\n\n{grammar_list(list(LINKS.keys()))}")
		return

	if args[1].upper() not in LINKS.keys(): # The link does not exist
		await message.channel.send("That link cannot be found.")
		return
	
	requested = args[1].upper() # Provide the link and info on it
	await message.channel.send(f"{LINKS[requested]['INFO']}\n\n**Link :** {LINKS[requested]['MAIN']}")
	return