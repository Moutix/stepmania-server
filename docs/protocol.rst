Stepmania Protocol
==================

Introduction
------------

Stepmania use his own protocol SMLan. It's composed of 3 parts.

Size|Command|Payload

* Size: size of packets.
* Command: Command to use
* Paylaod: data which depend of the command used.

Size type:

* MSN: Most signifiant 4 bits. Eg. 11110000 -> 1111 represents the 4 most signifiant bits (15 in decimal)
* LSN: least signifiant 4 bits. EG. 00001111 -> 1111 represents the 4 least signifiant bits (15 in decimal)
* NT: Null terminating string.
* X: Integer store in X bytes.

SMClient Packet
-------------------------

000: Ping
*********

This command will cause server to respond with a PingR response.

Payload: None.

001: PingR
**********

This command is used to respong to a ping packet.

Payload: None.

002: Hello
**********

This is the first packet from a client to server. It introduce the client to the server.

Payload:

+------+------------------------------+
| Size | Description                  |
+======+==============================+
| 1    |  Client protocol version     |
+------+------------------------------+
| NT   | Name of the stepmania build  |
+------+------------------------------+

003: Game Start Request
***********************

This command is called once after most loading is done, and again immediately before the sound starts.

Payload:

+-------+---------------------------------------------------------------------+
| Size  | Description                                                         |
+=======+=====================================================================+
| MSN   | Primary player difficulty (feet)   (0 for no player)                |
+-------+---------------------------------------------------------------------+
| LSN   | Secondary player difficulty (feet) (0 for no player)                |
+-------+---------------------------------------------------------------------+
| MSN   | Primary player difficulty (0=Beginner, 1=easy, etc.)                |
+-------+---------------------------------------------------------------------+
| LSN   | Second player difficulty (0=Beginner, 1=easy, etc.)                 |
+-------+---------------------------------------------------------------------+
| MSN   |  Start Position (0 is pre-sync, 1 is for sync)                      |
+-------+---------------------------------------------------------------------+
| LSN   |  Reserved                                                           |
+-------+---------------------------------------------------------------------+
| NT    |  Song Title                                                         |
+-------+---------------------------------------------------------------------+
| NT    |  Song Subtitle                                                      |
+-------+---------------------------------------------------------------------+
| NT    |  Song Artist                                                        |
+-------+---------------------------------------------------------------------+
| NT    |  Course Title (If none exists; make it just a null)                 |
+-------+---------------------------------------------------------------------+
| NT    |  Song Options (in string-format)                                    |
+-------+---------------------------------------------------------------------+
| NT    |  Primary Player's options (Null if non-existant)                    |
+-------+---------------------------------------------------------------------+
| NT    |  Secondary Player's Options (Null if non-existant)                  |
+-------+---------------------------------------------------------------------+

004: Game Over Notice
*********************

This command is sent when end of game is encounterd

Payload: None.

005: Game Status update
***********************

Updates game info for each step

+-------+---------------------------------------------------------------------+
| Size  | Description                                                         |
+=======+=====================================================================+
| MSN   | Player #                                                            |
+-------+---------------------------------------------------------------------+
| LSN   | StepID:                                                             |
|       |                                                                     |
|       | - 1: HitMine                                                        |
|       | - 2: AvoidMine                                                      |
|       | - 3: Miss                                                           |
|       | - 4: W5                                                             |
|       | - 5: W4                                                             |
|       | - 6: W3                                                             |
|       | - 7: W2                                                             |
|       | - 8: W1                                                             |
|       | - 9: LetGo                                                          |
|       | - 10: Held                                                          |
+-------+---------------------------------------------------------------------+
| MSN   | Projected Grade (StepMania enum int)                                |
+-------+---------------------------------------------------------------------+
| LSN   | Reserved                                                            |
+-------+---------------------------------------------------------------------+
| 4     | Net-order long containing score.                                    |
+-------+---------------------------------------------------------------------+
| 2     | Net-order int containing combo.                                     |
+-------+---------------------------------------------------------------------+
| 2     | Net-order int containing health.                                    |
+-------+---------------------------------------------------------------------+
| 2     | Net-order # containing offset.                                      |
|       | 32767 would be DEAD on the note. If the user is hitting late, the # |
|       | will be higher.                                                     |
|       | It if the user is exactly 0.25 seconds off, the number will be      |
|       | different by 500, if 0.5, it will be different by 1000.)            |
+-------+---------------------------------------------------------------------+

006: Style Update
*****************

This is sent when a profile is choosed. It also indicates the number of players in the local client. (1 or 2)

Payload:

+-------+---------------------------------------------------------------------+
| Size  | Description                                                         |
+=======+=====================================================================+
| 1     | Number of players in the client (1 or 2)                            |
+-------+---------------------------------------------------------------------+
| 1     | Player id. (0 or 1)                                                 |
+-------+---------------------------------------------------------------------+
| NT    | Player name for this id                                             |
+-------+---------------------------------------------------------------------+

007: Chat message
*****************

Sent when a user type a message on the general chat

Payload:

+-------+---------------------------------------------------------------------+
| Size  | Description                                                         |
+=======+=====================================================================+
| NT    | Message                                                             |
+-------+---------------------------------------------------------------------+

008: Request Start Game and Tell server existance/non existance of song.
************************************************************************

The user selected a song on a Net-enabled selection

Payload:

+-------+---------------------------------------------------------------------+
| Size  | Description                                                         |
+=======+=====================================================================+
| 1     | Usage of message                                                    |
|       |                                                                     |
|       | - 0: (in response to server 8) User has specified song,             |
|       | - 1: (in response to server 8) User does NOT have specified song,   |
|       | - 2: User requested a start game on given song)                     |
+-------+---------------------------------------------------------------------+
| NT    | Song Title    (As gotten by GetTranslitMainTitle)                   |
+-------+---------------------------------------------------------------------+
| NT    | Song Artist   (As Gotten by GetTranslitArtist)                      |
+-------+---------------------------------------------------------------------+
| NT    | Song Subtitle (As gotten by GetTranslitSubTitle)                    |
+-------+---------------------------------------------------------------------+

009: reserved
*************

nothing

010: User status
*****************

Indicate where the user is.

Payload:

+-------+---------------------------------------------------------------------+
| Size  | Description                                                         |
+=======+=====================================================================+
| 1     | Indicate where the user is:                                         |
|       |                                                                     |
|       | - 0: exited ScreenNetSelectMusic                                    |
|       | - 1: entered ScreenNetSelectMusic                                   |
|       | - 2: Not Sent                                                       |
|       | - 3: entered options screen                                         |
|       | - 4: exited the evaluation screen                                   |
|       | - 5: entered evaluation screen                                      |
|       | - 6: exited ScreenNetRoom                                           |
|       | - 7: entered ScreenNetRoom                                          |
+-------+---------------------------------------------------------------------+

011: User has changed player options
************************************

Payload:

+-------+---------------------------------------------------------------------+
| Size  | Description                                                         |
+=======+=====================================================================+
| NT    | Player 0's options                                                  |
+-------+---------------------------------------------------------------------+
| NT    | Player 1's options                                                  |
+-------+---------------------------------------------------------------------+

012: SMOnline Packet
********************

Use to send custom SMO client packet.

Payload:

+-----------+-----------------------------------------------------------------+
| Size      | Description                                                     |
+===========+=================================================================+
| SMOPacket | A SMO packet (Command + SMO payload).                           |
+-----------+-----------------------------------------------------------------+

013: reserved
*************

Nothing

014: reserved
*************

Nothing

015: XMLPacket
**************

This packet contains XML data. Don't know yet when it is used.

Payload:

+------+----------------------------------------------------------------------+
| Size | Description                                                          |
+======+======================================================================+
| NT   | XML Data                                                             |
+------+----------------------------------------------------------------------+



(SMO) 000: Login
****************

> Send login information. If provide, the salt is the key sent with the Server Hello command

Payload:

Size         | Description
------------ | -------------
1| Player Number
1| Encryption text  (0: MD5 hash, 1: MD5 ( MD5 hash + salt ))
NT| Username
NT| Password

### (SMO) 001: Enter Room

> User asks to enter in a room

Payload:

Size         | Description
------------ | -------------
1| Enter/Exit? (0: User wishes to exit room, 1: User wishes to enter room )
NT| Room Name (Used when entering rooms)
NT| Password (Empty if password not used)

### (SMO) 002: Create Room

> User asks to create a room (and enter in it if succeeded)

Payload:

Size         | Description
------------ | -------------
1|Room Type (0: Normal room (has sub rooms), 1: Game room (no sub rooms))
NT|Room Title
NT|Room Description
NT|Room Password (blank if no password)

### (SMO) 003: Requests Room Info

Send whenever a client hover a room in room selection.

Payload:

Size         | Description
------------ | -------------
NT | Room Name

