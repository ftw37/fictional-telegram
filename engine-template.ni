"Inca Curse" by "Artic Computing (recovered C64 edition)"

Use scoring.
Use full-length room descriptions.
Use MAX_STATIC_DATA of 2000000.

[This is a recovered, table-driven port, not the lost original authoring source.
The game data below comes directly from the decompressed T64 payload.
The vintage two-word parser and numbered object states are intentional.
Save, restore, restart, undo, quit, and transcript use Inform's standard machinery.]

The Interpreter Room is a room. The description is "".
The player is in the Interpreter Room.

The current site is a number that varies. The current site is 0.
The game registers are a list of numbers that varies.
The game registers are {0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0}.
The first code is a number that varies. The first code is 255.
The second code is a number that varies. The second code is 255.
The condition encountered is a truth state that varies.
The adventure finished is a truth state that varies.
The fatal ending is a truth state that varies.
The adventure moves are a number that varies.

To decide what number is register (N - a number):
	decide on entry (N + 1) of the game registers.

To set register (N - a number) to (V - a number):
	now entry (N + 1) of the game registers is V.

To decrease register (N - a number):
	if register N > 0:
		set register N to (register N - 1).

To decide what number is whereabouts of (N - a number):
	choose row (N + 1) in the Table of Recovered Objects;
	decide on item-place entry.

To place item (N - a number) at (P - a number):
	choose row (N + 1) in the Table of Recovered Objects;
	now item-place entry is P.

To decide whether item (N - a number) is available:
	let P be whereabouts of N;
	if P is current site or P is 253 or P is 254, yes;
	no.

To decide whether item (N - a number) is held:
	let P be whereabouts of N;
	if P is 253 or P is 254, yes;
	no.

To print item (N - a number):
	choose row (N + 1) in the Table of Recovered Objects;
	say "[item-name entry]".

To print recovered message (N - a number):
	choose row (N + 1) in the Table of Recovered Messages;
	say "[message-text entry][line break]";
	if N is 25 or N is 26:
		now fatal ending is true;
	if N is 27:
		now fatal ending is false.

To describe the recovered location:
	if register 0 is not 0:
		decrease register 3;
		[The recovered C64 routine tests the lamp's room, not carried status.]
		if (whereabouts of 0) is not current site:
			say "EVERYTHING IS DARK. I CANT SEE[line break]";
			decrease register 4;
			stop;
	choose row (current site + 1) in the Table of Recovered Rooms;
	say "[site-description entry][line break]";
	let heading printed be false;
	repeat with N running from 0 to 47:
		if whereabouts of N is current site:
			if heading printed is false:
				say "I CAN ALSO SEE:[line break]";
				now heading printed is true;
			print item N;
			say line break.

To display recovered inventory:
	say "I HAVE WITH ME THE FOLLOWING[line break]";
	let found something be false;
	repeat with N running from 0 to 47:
		if item N is held:
			now found something is true;
			print item N;
			if whereabouts of N is 253:
				say " WHICH I AM WEARING";
			say line break;
	if found something is false:
		say "NOTHING AT ALL[line break]".

To decide what number is decimal value of BCD (N - a number):
	let tens be N divided by 16;
	let units be the remainder after dividing N by 16;
	decide on (tens * 10) + units.

To decide whether recovered conditions (program - a list of numbers) pass:
	let cursor be 1;
	while cursor <= the number of entries in program:
		let opcode be entry cursor of program;
		increment cursor;
		let operand be entry cursor of program;
		increment cursor;
		if opcode is 0 and current site is not operand, no;
		if opcode is 1 and not (item operand is available), no;
		if opcode is 2:
			let roll be a random number from 0 to 255;
			if roll >= operand, no;
		if opcode is 3 and item operand is available, no;
		if opcode is 4 and whereabouts of operand is 253, no;
		if opcode is 5 and register operand is 0, no;
		if opcode is 6:
			let expected be entry cursor of program;
			increment cursor;
			if register operand is not expected, no;
		if opcode is 7 and register operand is not 0, no;
		if opcode is 8 and not (item operand is held), no;
	yes.

To decide what number is execute recovered actions (program - a list of numbers):
	[Result: 0 requests another command; 1 redescribes; 2 ends the game.]
	let cursor be 1;
	while cursor <= the number of entries in program:
		let opcode be entry cursor of program;
		increment cursor;
		let operand be entry cursor of program;
		increment cursor;
		if opcode is 0:
			display recovered inventory;
			decide on 0;
		if opcode is 1:
			if whereabouts of operand is not 253:
				say "I AM NOT WEARING IT[line break]";
				decide on 0;
			if register 1 is 6:
				say "I CANT.MY HANDS ARE FULL[line break]";
				decide on 0;
			place item operand at 254;
			set register 1 to (register 1 + 1);
		if opcode is 2:
			if register 1 is 6:
				say "I CANT CARRY ANY MORE[line break]";
				decide on 0;
			if whereabouts of operand is not current site:
				if item operand is held:
					say "I ALREADY HAVE IT[line break]";
				otherwise:
					say "I DONT SEE IT HERE[line break]";
				decide on 0;
			place item operand at 254;
			set register 1 to (register 1 + 1);
		if opcode is 3:
			unless item operand is held:
				say "I DONT HAVE IT[line break]";
				decide on 0;
			if whereabouts of operand is 254:
				set register 1 to (register 1 - 1);
			place item operand at current site;
		if opcode is 4:
			if whereabouts of operand is 253:
				say "I AM ALREADY WEARING IT[line break]";
				decide on 0;
			if whereabouts of operand is not 254:
				say "I DONT HAVE IT[line break]";
				decide on 0;
			place item operand at 253;
			set register 1 to (register 1 - 1);
		if opcode is 5:
			print recovered message operand;
		if opcode is 6, decide on 1;
		if opcode is 7, decide on 0;
		if opcode is 8:
			now current site is operand;
		if opcode is 9:
			set register operand to 255;
		if opcode is 10:
			set register operand to 0;
		if opcode is 11:
			let saved place be whereabouts of operand;
			let next place be whereabouts of (operand + 1);
			place item operand at next place;
			place item (operand + 1) at saved place;
		if opcode is 12 or opcode is 14:
			now adventure finished is true;
			decide on 2;
		if opcode is 13:
			say "OK..[line break]";
			decide on 0;
		if opcode is 15:
			let new setting be entry cursor of program;
			increment cursor;
			set register operand to new setting;
		if opcode is 16:
			place item operand at current site;
		if opcode is 17:
			place item operand at 252;
		if opcode is 18:
			let high part be entry cursor of program;
			increment cursor;
			let change be decimal value of BCD operand;
			now change is change + (100 * (decimal value of BCD high part));
			now score is the remainder after dividing (score + change) by 10000;
		if opcode is 19:
			say "YOU HAVE A SCORE OF [score][line break]";
		if opcode is 20 or opcode is 22, decide on 0;
		if opcode is 21:
			decrease register 2;
			decrease register 5;
			decide on 0;
	decide on 0.

To run recovered automatic rules:
	repeat through the Table of Recovered Automatic Rules:
		let conditions be auto-conditions entry;
		let operations be auto-actions entry;
		if recovered conditions conditions pass:
			let result be execute recovered actions operations;
			if result is 1:
				describe the recovered location;
			stop.

To finish the recovered adventure:
	if fatal ending is true:
		end the story saying "The adventure has ended";
	otherwise:
		end the story finally saying "You have escaped the Inca temple".

To decide what number is vocabulary code of (W - text):
	let key be W in upper case;
	if the number of characters in key > 4:
		let short key be "";
		repeat with N running from 1 to 4:
			now short key is "[short key][character number N in key]";
		now key is short key;
	while the number of characters in key < 4:
		now key is "[key] ";
	repeat through the Table of Recovered Vocabulary:
		if key is word-key entry:
			decide on word-code entry;
	decide on 255.

To process recovered command (input - text):
	now first code is 255;
	now second code is 255;
	now condition encountered is false;
	let normalized input be input in lower case;
	if normalized input is "l":
		now normalized input is "redescribe";
	if normalized input is "x":
		now normalized input is "look";
	if normalized input matches the regular expression "^x ":
		replace the regular expression "^x " in normalized input with "look ";
	repeat with N running from 1 to the number of words in normalized input:
		let candidate be vocabulary code of word number N in normalized input;
		if candidate is not 255:
			if first code is 255:
				now first code is candidate;
			otherwise:
				now second code is candidate;
				break;
	if first code is 255:
		say "I DONT UNDERSTAND[line break]";
		stop;
	let destination be -1;
	repeat through the Table of Recovered Exits:
		if exit-source entry is current site and exit-verb entry is first code:
			now destination is exit-target entry;
			break;
	if destination >= 0:
		now current site is destination;
		describe the recovered location;
		stop;
	repeat through the Table of Recovered Command Rules:
		if rule-verb entry is first code or rule-verb entry is 255:
			if rule-noun entry is second code or rule-noun entry is 255:
				let conditions be rule-conditions entry;
				let operations be rule-actions entry;
				if recovered conditions conditions pass:
					let result be execute recovered actions operations;
					if result is 1:
						describe the recovered location;
					stop;
				otherwise:
					now condition encountered is true;
	if first code < 13:
		say "I CANT GO IN THAT DIRECTION[line break]";
	otherwise if condition encountered is true:
		say "I CANT DO THAT YET[line break]";
	otherwise:
		say "I CANT[line break]".

The initial room description rule is not listed in the startup rulebook.
The notify score changes rule is not listed in the turn sequence rulebook.

When play begins:
	now the command prompt is "> ";
	now the maximum score is 5650;
	say "WELCOME TO ADVENTURE B: INCA CURSE[paragraph break]";
	say "In this adventure you find yourself in a South American jungle near an, as yet, undisturbed Inca temple. Inside this temple you will find lots of treasure. Your aim is to get out with as much treasure as you can.[paragraph break]Beware, do not let greed be your downfall. Your adventure is complete when you have returned to the jungle clearing with treasure.[paragraph break]";
	say "Use the original short commands: NORTH, TAKE BRANCH, CUT LEAVES, WITH ROPE, LOOK DOOR, I, HELP, and R. SAVE and RESTORE use Inform saved games.[paragraph break]";
	describe the recovered location;
	run recovered automatic rules.

Playing the recovered adventure is an action applying to one topic.
Understand "inca [text]" as playing the recovered adventure.

Carry out playing the recovered adventure:
	let input be the substituted form of "[the topic understood]";
	process recovered command input;
	increment the adventure moves;
	now the turn count is the adventure moves;
	run recovered automatic rules;
	if adventure finished is true:
		finish the recovered adventure.

After reading a command:
	let input be the substituted form of "[the player's command]";
	let key be input in lower case;
	if key is "save" or key is "restore" or key is "restart" or key is "quit" or key is "q" or key is "undo" or key is "version" or key is "transcript" or key is "transcript on" or key is "transcript off" or key is "script on" or key is "script off":
		make no decision;
	change the text of the player's command to "inca [input]".

Rule for printing the name of the Interpreter Room:
	choose row (current site + 1) in the Table of Recovered Rooms;
	say "[site-title entry]".

@RECOVERED_TABLES@
