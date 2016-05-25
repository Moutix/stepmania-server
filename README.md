# Stepmania Server

Implementation of a stepmania server in python3

Still in progress

# TODO

## Packet not handle

### 003:	Game Start Request

> This command is called once after most loading is done, and again immediately before the sound starts.

Payload:

Size         | Description
------------ | -------------
MSN	|	Primary player difficulty (feet)   (0 for no player)
LSN	|	Secondary player difficulty (feet) (0 for no player)
MSN	|	Primary player difficulty (0=Beginner, 1=easy, etc.) 
LSN	|	Second player difficulty (0=Beginner, 1=easy, etc.)
MSN|		Start Position (0 is pre-sync, 1 is for sync)
LSN|		Reserved
NT|		Song Title
NT|		Song Subtitle
NT|		Song Artist   
NT|		Course Title     (If none exists; make it just a null)
NT|		Song Options (in string-format)
NT|		Primary Player's options (Null if non-existant)
NT|		Secondary Player's Options (Null if non-existant)


### 004:	Game Over Notice

> This command is sent when end of game is encounterd

 Payload:	None.
 
### 005:	Game Status update
 
>	Updates game info for each step

Size         | Description
------------ | -------------
MSN		|Player #
LSN		|StepID (1: HitMine, 2: AvoidMine, 3: Miss, 4: W5, 5: W4, 6: W3, 7: W2, 8: W1, 9: LetGo, 10: Held)
MSN	|	Projected Grade (StepMania enum int)
LSN	|	Reserved
4	|	Net-order long containing score.
2	|	Net-order int containing combo.
2	|	Net-order int containing health.
2	|	Net-order # containing offset (32767 would be DEAD on the note. If the user is hitting late, the # will be higher. It if the user is exactly 0.25 seconds off, the number will be different by 500, if 0.5, it will be different by 1000.)

### 008:	Request Start Game and Tell server existance/non existance of song.

> The user selected a song on a Net-enabled selection

Size         | Description
------------ | -------------
1	|	Usage of message (0: (in response to server 8) User has specified song, 1: (in response to server 8) User does NOT have specified song, 2: User requested a start game on given song)
NT|		Song Title    (As gotten by GetTranslitMainTitle)
NT|		Song Artist   (As Gotten by GetTranslitArtist)
NT|		Song Subtitle (As gotten by GetTranslitSubTitle)


### 011:	User has changed player options

Size         | Description
------------ | -------------
NT	|	Player 0's options
NT	|	Player 1's options


### (SMO) 003: Requests Room Info

Send whenever a client hover a room in room selection.

Size         | Description
------------ | -------------
NT |	Room Name

## Other things to do

* Chat plugin with color and function
* User privileges
 
