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

Table of Recovered Rooms
site-id	site-title	site-description
0	"In A Jungle Clearing"	"I AM IN A JUNGLE CLEARING[line break]EXITS ARE SOUTH"
1	"On The Temple Steps"	"I AM ON THE TEMPLE STEPS[line break]EXITS ARE NORTH"
2	"In The Temple"	"I AM IN THE TEMPLE[line break]EXITS ARE NORTH"
3	"In The Hidden Hall"	"I AM IN THE HIDDEN HALL[line break]EXITS ARE DOWN,NORTH,EAST AND WEST"
4	"In A Cellar"	"I AM IN A CELLAR[line break]EXITS ARE SOUTH,EAST AND WEST"
5	"In The Sacrificial Chamber"	"I AM IN THE SACRIFICIAL CHAMBER[line break]EXITS ARE EAST AND WEST"
6	"In A Store Room"	"I AM IN A STORE ROOM[line break]EXITS ARE SOUTH AND WEST"
7	"In A Statue Room"	"I AM IN A STATUE ROOM[line break]EXITS ARE SOUTH AND EAST"
8	"In A Guilded Rest Room"	"I AM IN A GUILDED REST ROOM[line break]EXITS ARE NORTH,SOUTH AND EAST"
9	"In The Slaves Waiting Room"	"I AM IN THE SLAVES WAITING ROOM[line break]EXITS ARE NORTH"
10	"In A Small Room"	"I AM IN A SMALL ROOM[line break]EXITS ARE NORTH AND EAST"
11	"In A Painted Corridor"	"I AM IN A PAINTED CORRIDOR[line break]EXITS ARE SOUTH,EAST AND WEST"
12	"In A Rock Room"	"I AM IN A ROCK ROOM[line break]EXITS ARE DOWN,NORTH AND WEST"
13	"In The Wine Room"	"I AM IN THE WINE ROOM[line break]EXITS ARE DOWN,NORTH AND EAST"
14	"In The Hot Baths"	"I AM IN THE HOT BATHS[line break]EXITS ARE UP,DOWN AND WEST"
15	"On A Ledge"	"I AM ON A LEDGE[line break]EXITS ARE NORTH AND SOUTH"
16	"In The Armoury"	"I AM IN THE ARMOURY[line break]EXITS ARE DOWN AND EAST"
17	"In The Prison Torture Room"	"I AM IN THE PRISON TORTURE ROOM[line break]EXITS ARE UP,DOWN AND WEST"
18	"At A Pool Side"	"I AM AT A POOL SIDE[line break]TUNNELS LEAD ACROSS THE WATER SOUTH,WEST AND EAST"
19	"In The Priests Rest Room"	"I AM IN THE PRIESTS REST ROOM[line break]EXITS ARE UP AND WEST"
20	"In The Fire Room"	"I AM IN THE FIRE ROOM[line break]EXITS ARE UP"
21	"In The Robe Room"	"I AM IN THE ROBE ROOM[line break]EXITS ARE NORTH AND EAST"
22	"In The Slave Room"	"I AM IN THE SLAVE ROOM[line break]EXITS ARE EAST,WEST AND DOWN"
23	"In The Panelled Room"	"I AM IN THE PANELLED ROOM[line break]EXITS ARE UP AND WEST"
24	"In The Forgotten Room"	"I AM IN THE FORGOTTEN ROOM[line break]EXITS ARE UP"
25	"In A Sand Dungeon"	"I AM IN A SAND DUNGEON[line break]A PORTHOLE LEADS DOWNWARDS"
26	"In The Sacred Stone Room"	"I AM IN THE SACRED STONE ROOM[line break]EXITS ARE NORTH AND WEST"
27	"In The Eagle Hall"	"I AM IN THE EAGLE HALL[line break]EXITS ARE DOWN"
28	"In A Hall Of Gold"	"I AM IN A HALL OF GOLD[line break]EXITS ARE NORTH AND SOUTH"
29	"In The Traitors Hall"	"I AM IN THE TRAITORS HALL[line break]EXITS ARE NORTH AND SOUTH"
30	"In A Maze"	"I AM IN A MAZE[line break]THERE ARE PASSAGES EVERYWHERE"
31	"In A Maze"	"I AM IN A MAZE[line break]THERE ARE PASSAGES EVERYWHERE"
32	"In A Maze"	"I AM IN A MAZE[line break]THERE ARE PASSAGES EVERYWHERE"
33	"In A Maze"	"I AM IN A MAZE[line break]THERE ARE PASSAGES EVERYWHERE"
34	"In A Maze"	"I AM IN A MAZE[line break]THERE ARE PASSAGES EVERYWHERE"
35	"In A Maze"	"I AM IN A MAZE[line break]THERE ARE PASSAGES EVERYWHERE"
36	"In A Maze"	"I AM IN A MAZE[line break]THERE ARE PASSAGES EVERYWHERE"
37	"In A Maze"	"I AM IN A MAZE[line break]THERE ARE PASSAGES EVERYWHERE"
38	"In A Maze"	"I AM IN A MAZE[line break]THERE ARE PASSAGES EVERYWHERE"
39	"In The Golden Torture Room"	"I AM IN THE GOLDEN TORTURE ROOM[line break]EXITS ARE NORTH AND EAST"
40	"In A Living Room"	"I AM IN A LIVING ROOM[line break]EXITS ARE SOUTH AND WEST"
41	"In The Slave Eating Room"	"I AM IN THE SLAVE EATING ROOM[line break]EXITS ARE SOUTH"
42	"In The Wash Room"	"I AM IN THE WASH ROOM[line break]EXITS ARE NORTH AND SOUTH"
43	"In The Slaughter Room"	"I AM IN THE SLAUGHTER ROOM[line break]EXITS ARE NORTH AND WEST"
44	"In A Weapon Room"	"I AM IN A WEAPON ROOM[line break]EXITS ARE SOUTH,EAST AND WEST"
45	"In A Guard Room"	"I AM IN A GUARD ROOM[line break]EXITS ARE NORTH AND WEST"
46	"In A Furnace"	"I AM IN A FURNACE[line break]EXITS ARE DOWN AND EAST"
47	"In A Kitchen"	"I AM IN A KITCHEN[line break]EXITS ARE NORTH AND EAST"
48	"In The Emperors Corridor"	"I AM IN THE EMPERORS CORRIDOR[line break]EXITS ARE SOUTH,A PORTHOLE LEADS UPWARDS AND A SECRET PASSAGE LEADS WEST"
49	"In The Treasury"	"I AM IN THE TREASURY[line break]EXITS ARE SOUTH"
50	"In The Emperors Throne Room"	"I AM IN THE EMPERORS THRONE ROOM[line break]EXITS ARE NORTH AND EAST"
51	"In The Hall Of Halls"	"I AM IN THE HALL OF HALLS[line break]EXITS ARE SOUTH,EAST AND WEST"
52	"In The Mirror Room"	"I AM IN THE MIRROR ROOM[line break]EXITS ARE EAST"
53	"In The Emperors Bedroom"	"I AM IN THE EMPERORS BEDROOM[line break]EXITS ARE DOWN AND NORTH"
54	"In The Slave Preparation Room"	"I AM IN THE SLAVE PREPARATION ROOM[line break]EXITS ARE UP,DOWN AND EAST"
55	"In The Room Of Death"	"I AM IN THE ROOM OF DEATH[line break]EXITS ARE UP,DOWN AND WEST"
56	"In The Desolation Cell"	"I AM IN THE DESOLATION CELL[line break]EXITS ARE UP AND WEST"
57	"In A Boat"	"I AM IN A BOAT[line break]TUNNELS LEAD SOUTH,WEST AND EAST"

Table of Recovered Objects
item-id	item-name	item-place
0	"A LIT LAMP"	252
1	"A STICK"	252
2	"A ROCK"	2
3	"A KEY"	6
4	"A MAGIC BLANKET"	5
5	"A HIEROGLYPHIC TRANSLATOR"	9
6	"A LADDER"	10
7	"A GOLD BAR"	15
8	"A ROPE"	16
9	"A SMALL BOAT"	18
10	"A BLUE STONE"	24
11	"A RED STONE"	26
12	"A CHISEL"	11
13	"A SKULL"	27
14	"A MAGIC RING EMBEDDED IN FLINT"	20
15	"SOME SCALES"	21
16	"BLUE POWDER"	252
17	"RED POWDER"	252
18	"A MATCH"	12
19	"A DAMP MATCH"	252
20	"A USED MATCH"	252
21	"A LAMP"	20
22	"A BRANCH"	0
23	"A SIGN"	22
24	"A NOTICE"	26
25	"FIRE"	20
26	"SMOULDERING ASHES"	252
27	"OARS"	252
28	"*** GOLDEN EAGLE ***"	27
29	"*** GOLDEN CHANDELIERS ***"	28
30	"*** GOLD COINS ***"	49
31	"*** GOLDEN BRUSH ***"	52
32	"*** GOLDEN STATUE ***"	53
33	"*** GOLDEN BOWL ***"	54
34	"*** GOLDEN THUMBSCREW ***"	39
35	"*** GOLDEN KNIVES ***"	43
36	"AN OPEN DOOR UP THE STEPS"	252
37	"A BROKEN LOCK"	252
38	"AN OPEN DOOR"	252
39	"A DOOR WITH A LARGE LOCK"	2
40	"A WINDOW"	2
41	"OARS"	57
42	"A MAGIC RING"	252
43	"SLIGHTLY OPEN PANELS"	23
44	"HOLE IN PANELS"	252
45	"LOCKED PANEL"	23
46	"OPENING IN A PANEL"	252
47	"A LARGE LATCHED DOOR UP THE STEPS"	1

Table of Recovered Exits
exit-source	exit-verb	exit-target
0	4	1
1	3	0
2	3	1
3	2	14
3	3	2
3	5	4
3	6	7
4	4	10
4	5	5
4	6	3
5	5	6
5	6	4
6	4	12
6	6	5
7	4	8
7	5	3
8	3	7
8	4	13
8	5	9
9	3	8
10	3	4
10	5	11
11	4	16
11	5	12
11	6	10
12	2	17
12	3	6
12	6	11
13	2	18
13	3	8
13	5	14
14	1	3
14	2	19
14	6	13
15	3	7
15	4	4
16	2	23
16	5	17
17	1	12
17	2	24
17	6	16
19	1	14
19	6	18
21	3	18
21	5	22
22	5	23
22	6	21
23	1	16
23	6	22
24	1	17
26	3	12
26	6	25
27	2	49
28	3	48
28	4	29
29	3	28
29	4	30
30	1	30
30	2	30
30	3	31
30	4	32
30	5	30
30	6	30
31	1	31
31	2	31
31	3	31
31	4	33
31	5	31
31	6	31
32	1	32
32	2	32
32	3	36
32	4	32
32	5	32
32	6	32
33	1	33
33	2	33
33	3	33
33	4	33
33	5	34
33	6	35
34	1	34
34	2	34
34	3	34
34	4	34
34	5	34
34	6	50
35	1	35
35	2	35
35	3	35
35	4	35
35	5	29
35	6	35
36	1	36
36	2	36
36	3	36
36	4	36
36	5	37
36	6	38
37	1	37
37	2	37
37	3	37
37	4	37
37	5	37
37	6	52
38	1	38
38	2	38
38	3	38
38	4	38
38	5	51
38	6	38
39	3	40
39	5	55
40	4	39
40	6	54
41	4	42
42	3	41
42	4	43
43	3	42
43	5	56
44	4	45
44	5	51
44	6	46
45	3	44
45	6	47
46	2	47
46	5	44
47	3	46
47	5	45
48	4	28
49	4	50
50	3	49
50	5	30
51	4	53
51	5	44
51	6	30
52	5	31
53	2	54
53	3	51
54	1	53
54	2	55
54	5	40
55	1	54
55	2	56
55	6	39
56	1	55
56	6	43
57	4	21
57	5	19

Table of Recovered Vocabulary
word-key	word-code
"UP  "	1
"U   "	1
"DOWN"	2
"D   "	2
"NORT"	3
"N   "	3
"SOUT"	4
"S   "	4
"EAST"	5
"E   "	5
"WEST"	6
"W   "	6
"GET "	13
"PICK"	13
"TAKE"	13
"DROP"	14
"PUT "	14
"BRAN"	15
"REMO"	16
"STRI"	16
"CUT "	16
"LEAV"	17
"FOLI"	17
"CLIM"	18
"BOAR"	18
"STEP"	19
"ROCK"	20
"HIT "	21
"KNOC"	21
"LATC"	22
"USE "	23
"WITH"	23
"BREA"	24
"SMAS"	24
"LOCK"	25
"MAGI"	26
"BLAN"	26
"KEY "	27
"HYRO"	28
"SPAN"	28
"TRAN"	28
"LADD"	29
"CHIS"	30
"GOLD"	31
"BAR "	31
"ROPE"	32
"BOAT"	33
"BLUE"	34
"RED "	35
"SKUL"	36
"RING"	37
"FLIN"	37
"SCAL"	38
"MATC"	39
"LAMP"	40
"READ"	41
"SIGN"	42
"NOTI"	43
"SMOT"	44
"FIRE"	45
"FLAM"	45
"SMOU"	46
"ASHE"	46
"OARS"	47
"INVE"	48
"I   "	48
"HELP"	49
"QUIT"	50
"STOP"	50
"ABOR"	50
"YES "	51
"NO  "	52
"Y   "	51
"STRI"	53
"LIGH"	54
"LOOK"	55
"ROW "	56
"TUNN"	56
"PUSH"	57
"MIRR"	58
"KICK"	59
"BOOT"	59
"STIC"	15
"DOOR"	61
"WALL"	62
"LEDG"	63
"POOL"	64
"LAKE"	64
"SWIM"	65
"ONBO"	66
"KILL"	67
"ASCE"	68
"STAI"	69
"OPEN"	70
"PRIS"	70
"UNLO"	70
"PANE"	71
"HOLE"	72
"ENTE"	73
"WALK"	73
"PORT"	74
"EAGL"	75
"CHAN"	76
"COIN"	77
"BRUS"	78
"THUM"	79
"SCRE"	79
"KNIF"	80
"STAT"	81
"BOWL"	82
"REDE"	83
"R   "	83
"SCOR"	84
"WIND"	85

Table of Recovered Messages
message-id	message-text
0	"IT IS HEAVY WITH LOTS OF LEAVES"
1	"HOW?"
2	"WITH WHAT?"
3	"YOU HAVE ALREADY BROKEN IT"
4	"FOR WHAT?"
5	"THE BRICKS LOOK LOOSE"
6	"OUCH... THAT HURT MY FOOT"
7	"I CAN SEE A HIGH LEDGE"
8	"A BOAT IS BOBBING ON THE RIPPLES"
9	"IT IS BEAUTIFUL WITH A SMALL[line break]BOAT FLOATING ON IT"
10	"I CAN NOT SWIM AND AM NOW WET"
11	"IN WHICH DIRECTION?"
12	"IT FLARES UP... THEN FIZZLES OUT"
13	"THE FIRE BLOCKS THE STAIRCASE"
14	"THE SIGN SAYS: DO NOT DESCEND"
15	"THE NOTICE SAYS:DEATH AWAITS ALL[line break]WHO GO WEST UNPREPARED"
16	"I CANT READ IT....[line break]IT IS WRITTEN IN SPANISH.."
17	"I DONT UNDERSTAND...[line break]IT IS HIEROGLYPHICS.."
18	"I SEE A LIGHT OVERHEAD"
19	"YOU ARE NOT CARRYING THE [line break]CORRECT POSSESSIONS"
20	"I CAN SEE MY REFLECTION"
21	"REMOVE SOME OF THE PANELS"
22	"LOOK UP"
23	"USE SOMETHING TO CLIMB UP"
24	"TRY EXAMINING THINGS"
25	"I HAVE BEEN ROASTED ALIVE...[line break]THIS IS THE END OF THE ADVENTURE"
26	"THE DUNGEON HAS FILLED WITH SAND[line break]YOU HAVE SUFFOCATED..[line break]THIS IS THE END OF THE ADVENTURE"
27	"CONGRATULATIONS[line break][line break]YOU HAVE SUCCESFULLY COMPLETED [line break][line break]THIS ADVENTURE. WELL DONE[line break]NOW TRY OUR NEXT ONE:ADVENTURE C[line break]** ALIEN SPACE SHIP ADVENTURE **"
28	"HOW DO I CROSS THE POOL?"
29	"TRY CLIMBING ONBOARD FIRST"
30	"I SEE NOTHING SPECIAL"
31	"NO.. I AM NOT A VANDAL"
32	"I SEE A MESSAGE SAYING[line break]FOR HIGH QUALITY SOFTWARE FOR YOUR COMPUTER YOU SHOULD GO TO[line break]ARTIC COMPUTING[line break]MAIN STREET[line break]BRANDESBURTON[line break]OR ANY GOOD COMPUTER STORE"
33	"I AM UP TO MY NECK IN SAND..."
34	"MY SKIN IS BLISTERING..."
35	"TARZAN WOULD WEAR THEM SO WHY NOT STRIP THEM?"
36	"PUT THE FIRE OUT!"
37	"THE LATCH IS VERY FRAGILE"
38	"THE LOCK IS VERY WEAK"

Table of Recovered Automatic Rules
auto-verb	auto-noun	auto-conditions	auto-actions
255	255	{0, 26, 6, 5, 1}	{5, 26, 19, 14, 14, 0}
255	255	{0, 20, 6, 2, 1}	{5, 26, 19, 14, 14, 0}
255	255	{0, 0, 6, 6, 255}	{5, 27, 19, 14, 14, 0}
255	255	{}	{21, 0}

Table of Recovered Command Rules
rule-verb	rule-noun	rule-conditions	rule-actions
13	15	{1, 22}	{5, 0, 7, 0}
48	255	{}	{0, 0}
16	17	{1, 22}	{17, 22, 16, 1, 13, 0}
13	15	{1, 1}	{2, 1, 13, 0}
13	15	{1, 1}	{2, 1, 13, 0}
15	255	{1, 1}	{2, 1, 13, 0}
18	19	{0, 1, 1, 36}	{8, 2, 6, 0}
1	255	{0, 1, 1, 36}	{8, 2, 6, 0}
21	22	{0, 1, 3, 36}	{5, 2, 7, 0}
24	22	{0, 1, 3, 36}	{5, 1, 7, 0}
23	15	{0, 1, 3, 36, 1, 1}	{16, 36, 17, 47, 6, 0}
13	20	{1, 2}	{2, 2, 13, 0}
24	25	{0, 2, 3, 37}	{5, 2, 7, 0}
23	25	{0, 2, 3, 37}	{5, 1, 6, 0}
23	20	{0, 2, 3, 37}	{16, 37, 16, 38, 17, 39, 6, 0}
24	25	{1, 37, 0, 2}	{5, 3, 7, 0}
21	25	{1, 37, 0, 2}	{5, 3, 7, 0}
23	20	{0, 2, 1, 37}	{5, 4, 6, 0}
61	255	{0, 2, 1, 38}	{8, 3, 6, 0}
13	26	{1, 4}	{2, 4, 13, 0}
13	27	{1, 3}	{2, 3, 13, 0}
55	62	{0, 6}	{5, 5, 7, 0}
21	62	{0, 6}	{5, 2, 7, 0}
24	62	{0, 6}	{5, 1, 7, 0}
23	30	{0, 6, 1, 12}	{8, 27, 6, 0}
59	255	{}	{5, 6, 7, 0}
13	28	{1, 5}	{2, 5, 13, 0}
13	31	{1, 7}	{2, 7, 13, 0}
13	29	{1, 6}	{2, 6, 13, 0}
13	30	{1, 12}	{2, 12, 13, 0}
13	39	{1, 18}	{2, 18, 13, 0}
55	1	{0, 14}	{5, 7, 7, 0}
18	63	{0, 14}	{5, 1, 7, 0}
18	1	{0, 14}	{5, 1, 7, 0}
23	29	{0, 14, 1, 6}	{3, 6, 8, 15, 6, 0}
13	32	{1, 8}	{2, 8, 13, 0}
55	33	{1, 9}	{5, 8, 7, 0}
55	64	{0, 18}	{5, 9, 7, 0}
65	255	{0, 18, 8, 18}	{5, 10, 11, 18, 7, 0}
18	33	{0, 18}	{8, 57, 6, 0}
18	66	{0, 18}	{8, 57, 6, 0}
13	47	{1, 41}	{2, 41, 13, 0}
56	255	{0, 57, 1, 41}	{5, 11, 7, 0}
13	37	{1, 14}	{2, 14, 13, 0}
13	37	{1, 42}	{2, 42, 13, 0}
13	40	{1, 21}	{2, 21, 13, 0}
13	40	{1, 0}	{2, 22, 13, 0}
44	45	{1, 25, 1, 4}	{17, 25, 16, 26, 9, 0, 15, 2, 0, 6, 0}
67	45	{1, 25, 1, 4}	{17, 25, 16, 26, 9, 0, 15, 2, 0, 6, 0}
54	40	{1, 21}	{5, 2, 7, 0}
23	39	{8, 21, 8, 18}	{3, 21, 3, 18, 17, 21, 17, 18, 16, 0, 16, 20, 2, 0, 10, 0, 6, 0}
54	39	{1, 18}	{5, 12, 17, 18, 16, 20, 7, 0}
53	39	{1, 18}	{5, 12, 17, 18, 16, 20, 7, 0}
18	69	{0, 20, 3, 25, 1, 0}	{8, 7, 10, 0, 6, 0}
68	69	{0, 20, 3, 25, 1, 0}	{8, 7, 10, 0, 6, 0}
18	69	{0, 20, 1, 25}	{5, 13, 7, 0}
68	69	{0, 20, 1, 25}	{5, 13, 7, 0}
24	37	{1, 14}	{5, 2, 7, 0}
16	37	{1, 14}	{5, 2, 7, 0}
23	30	{8, 14, 8, 12}	{3, 14, 17, 14, 16, 42, 2, 42, 13, 0}
13	38	{1, 15}	{2, 15, 13, 0}
55	42	{0, 22, 1, 5}	{5, 14, 7, 0}
41	42	{0, 22, 1, 5}	{5, 14, 7, 0}
70	71	{0, 23, 1, 43}	{5, 1, 7, 0}
23	31	{0, 23, 1, 43}	{17, 43, 16, 44, 6, 0}
19	71	{0, 23, 1, 44}	{8, 24, 6, 0}
18	71	{0, 23, 1, 44}	{8, 24, 6, 0}
19	72	{0, 23, 1, 44}	{8, 24, 6, 0}
18	72	{0, 23, 1, 44}	{8, 24, 6, 0}
70	71	{0, 23, 1, 45}	{5, 2, 7, 0}
23	27	{0, 23, 1, 45}	{17, 45, 16, 46, 6, 0}
19	70	{0, 23, 1, 46}	{8, 26, 6, 0}
70	255	{0, 23, 1, 46}	{8, 26, 6, 0}
73	70	{0, 23, 1, 46}	{8, 26, 6, 0}
59	71	{0, 23}	{5, 6, 7, 0}
13	34	{1, 10}	{2, 10, 13, 0}
13	35	{1, 11}	{2, 11, 13, 0}
55	43	{0, 26, 1, 5}	{5, 15, 7, 0}
41	43	{0, 26, 1, 5}	{5, 15, 7, 0}
55	42	{0, 22, 3, 5}	{5, 16, 7, 0}
41	42	{0, 22, 3, 5}	{5, 16, 7, 0}
55	43	{0, 26, 3, 5}	{5, 17, 7, 0}
41	43	{0, 26, 3, 5}	{5, 17, 7, 0}
18	1	{0, 25}	{5, 1, 7, 0}
68	255	{0, 25}	{5, 1, 7, 0}
23	32	{0, 25, 8, 8}	{8, 22, 15, 5, 0, 6, 0}
55	1	{0, 25}	{5, 18, 7, 0}
73	74	{0, 25, 8, 10, 8, 42}	{8, 48, 15, 5, 0, 9, 6, 6, 0}
2	255	{0, 25, 8, 10, 8, 42}	{8, 48, 15, 5, 0, 9, 6, 6, 0}
2	255	{0, 25}	{5, 19, 7, 0}
5	255	{0, 23, 3, 42}	{5, 19, 7, 0}
1	255	{0, 48, 8, 10, 8, 42}	{8, 25, 6, 0}
1	255	{0, 48}	{5, 19, 7, 0}
1	255	{0, 48}	{5, 19, 7, 0}
73	74	{0, 48, 8, 10, 8, 42}	{8, 25, 15, 5, 7, 6, 0}
6	255	{0, 48, 8, 11}	{8, 27, 6, 0}
6	255	{0, 48}	{5, 19, 7, 0}
13	75	{1, 28}	{2, 28, 18, 0, 37, 13, 0}
13	76	{1, 29}	{2, 29, 18, 0, 2, 13, 0}
13	77	{1, 30}	{2, 30, 18, 0, 5, 13, 0}
13	78	{1, 31}	{2, 31, 18, 0, 5, 13, 0}
13	79	{1, 34}	{2, 34, 18, 0, 1, 13, 0}
13	80	{1, 35}	{2, 35, 18, 0, 1, 13, 0}
13	81	{1, 32}	{2, 32, 18, 0, 4, 13, 0}
13	82	{1, 33}	{2, 33, 18, 80, 1, 13, 0}
57	58	{0, 52}	{8, 46, 6, 0}
55	58	{0, 52}	{5, 20, 7, 0}
14	75	{8, 28}	{3, 28, 18, 0, 117, 13, 0}
14	76	{8, 29}	{3, 29, 18, 0, 152, 13, 0}
14	77	{8, 30}	{3, 30, 18, 0, 149, 13, 0}
14	78	{8, 31}	{3, 31, 18, 0, 149, 13, 0}
14	79	{8, 34}	{3, 34, 18, 0, 153, 13, 0}
14	80	{8, 35}	{3, 35, 18, 0, 150, 13, 0}
14	81	{8, 32}	{3, 32, 18, 0, 150, 13, 0}
14	82	{8, 33}	{3, 33, 18, 80, 152, 13, 0}
14	34	{8, 10}	{3, 10, 17, 10, 16, 16, 13, 0}
14	35	{8, 11}	{3, 11, 17, 11, 16, 17, 13, 0}
14	38	{8, 15}	{3, 15, 13, 0}
14	37	{8, 14}	{3, 14, 13, 0}
14	40	{8, 21}	{3, 21, 13, 0}
14	37	{8, 42}	{3, 42, 13, 0}
14	40	{8, 0}	{3, 0, 17, 0, 16, 21, 13, 0}
14	32	{8, 8}	{3, 8, 13, 0}
14	28	{8, 5}	{3, 5, 13, 0}
14	31	{8, 7}	{3, 7, 13, 0}
14	29	{8, 6}	{3, 6, 13, 0}
14	30	{8, 12}	{3, 12, 13, 0}
14	39	{8, 18}	{3, 18, 13, 0}
14	39	{8, 19}	{3, 19, 13, 0}
14	39	{8, 20}	{3, 20, 13, 0}
13	39	{1, 19}	{2, 19, 13, 0}
13	39	{1, 20}	{2, 10, 13, 0}
14	26	{8, 4}	{3, 4, 13, 0}
14	27	{8, 3}	{3, 3, 13, 0}
14	20	{8, 2}	{3, 2, 13, 0}
14	15	{8, 1}	{3, 1, 13, 0}
14	15	{8, 1}	{3, 1, 13, 0}
14	15	{8, 22}	{3, 0, 13, 0}
83	255	{}	{6, 0}
49	255	{0, 23}	{5, 21, 7, 0}
84	255	{}	{19, 7, 19, 14, 5, 22, 7, 0}
50	255	{}	{19, 14, 5, 22, 7, 0}
49	255	{0, 25}	{5, 22, 7, 0}
49	255	{0, 14}	{5, 23, 7, 0}
6	255	{0, 57}	{8, 20, 15, 2, 9, 6, 0}
6	255	{0, 26}	{8, 25, 15, 5, 7, 6, 0}
2	255	{0, 22}	{8, 25, 15, 5, 7, 6, 0}
4	255	{0, 18}	{5, 28, 7, 0}
5	255	{0, 18}	{5, 28, 7, 0}
6	255	{0, 18}	{5, 28, 7, 0}
23	33	{0, 18}	{5, 29, 7, 0}
55	85	{0, 2}	{5, 32, 7, 0}
65	255	{0, 18}	{5, 10, 7, 0}
56	33	{0, 18}	{5, 29, 7, 0}
1	255	{0, 20, 3, 25}	{8, 7, 6, 0}
1	255	{0, 20, 1, 25}	{5, 13, 7, 0}
24	85	{1, 40}	{5, 31, 7, 0}
49	255	{0, 0}	{5, 35, 7, 0}
49	255	{0, 20}	{5, 36, 7, 0}
55	255	{0, 1}	{5, 37, 7, 0}
55	255	{0, 2}	{5, 38, 7, 0}
49	255	{}	{5, 24, 7, 0}
49	255	{}	{5, 30, 7, 0}
