Stepmania Protocol
==================

Introduction
------------

Stepmania use his own protocol SMLan. It's composed of 3 parts.

Size|Command|Payload

* Size: size of packets.
* Command: Command to use
* Payload: data which depend of the command used.

Size type:

* MSN: Most signifiant 4 bits. Eg. 11110000 -> 1111 represents the 4 most signifiant bits (15 in decimal)
* LSN: Least signifiant 4 bits. EG. 00001111 -> 1111 represents the 4 least signifiant bits (15 in decimal)
* NT: Null terminating string.
* X: Integer store in X bytes.

The protocol is implemented in :mod:`smserver.smutils.smpacket` module

SMClient Packet
---------------

000: Ping
*********

This command will cause server to respond with a PingR response.

Payload: None.

See :class:`smserver.smutils.smpacket.SMPacketClientNSCPing`

001: PingR
**********

This command is used to respond to a ping packet.

Payload: None.

See :class:`smserver.smutils.smpacket.SMPacketClientNSCPingR`

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

See :class:`smserver.smutils.smpacket.SMPacketClientNSCHello`

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

See :class:`smserver.smutils.smpacket.SMPacketClientNSCGSR`

004: Game Over Notice
*********************

This command is sent when end of game is encounterd

Payload: None.

See :class:`smserver.smutils.smpacket.SMPacketClientNSCGON`

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

See :class:`smserver.smutils.smpacket.SMPacketClientNSCGSU`

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

See :class:`smserver.smutils.smpacket.SMPacketClientNSCSU`

007: Chat message
*****************

Sent when a user type a message on the general chat

Payload:

+-------+---------------------------------------------------------------------+
| Size  | Description                                                         |
+=======+=====================================================================+
| NT    | Message                                                             |
+-------+---------------------------------------------------------------------+

See :class:`smserver.smutils.smpacket.SMPacketClientNSCCM`

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

See :class:`smserver.smutils.smpacket.SMPacketClientNSCRSG`

009: reserved
*************

nothing

See :class:`smserver.smutils.smpacket.SMPacketClientNSCUUL`


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

See :class:`smserver.smutils.smpacket.SMPacketClientNSSCSMS`

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

See :class:`smserver.smutils.smpacket.SMPacketClientNSCUOpts`

012: SMOnline Packet
********************

Use to send custom SMO client packet.

Payload:

+-----------+-----------------------------------------------------------------+
| Size      | Description                                                     |
+===========+=================================================================+
| SMOPacket | A SMO packet (Command + SMO payload).                           |
+-----------+-----------------------------------------------------------------+


See :class:`smserver.smutils.smpacket.SMPacketClientNSSMONL`

013: reserved
*************

Nothing

See :class:`smserver.smutils.smpacket.SMPacketClientNSCFormatted`

014: reserved
*************

Nothing

See :class:`smserver.smutils.smpacket.SMPacketClientNSCAttack`

015: XMLPacket
**************

This packet contains XML data. Don't know yet when it is used.

Payload:

+------+----------------------------------------------------------------------+
| Size | Description                                                          |
+======+======================================================================+
| NT   | XML Data                                                             |
+------+----------------------------------------------------------------------+

See :class:`smserver.smutils.smpacket.SMPacketClientXMLPacket`

SMServer Packet
---------------

The command start at 128 for server response.

128: Ping
*********

This command will cause client to respond with a PingR command

Payload: None.

See :class:`smserver.smutils.smpacket.SMPacketServerNSCPing`

129: PingR
**********

This command is used to respond to a Ping command.

Payload: None.

See :class:`smserver.smutils.smpacket.SMPacketServerNSCPingR`

130: Hello
**********

This command introduces the server. (In response of Client Hello command)

Payload:

+-------+---------------------------------------------------------------------+
| Size  | Description                                                         |
+=======+=====================================================================+
| 1     | Server protocol version (128 for SMOnline server)                   |
+-------+---------------------------------------------------------------------+
| NT    | Server name                                                         |
+-------+---------------------------------------------------------------------+
| 4     | Random key (at the moment only used for hash password on login)     |
+-------+---------------------------------------------------------------------+

See :class:`smserver.smutils.smpacket.SMPacketServerNSCHello`

131: Allow Start
****************

This will cause the client to start the game

Payload: None

See :class:`smserver.smutils.smpacket.SMPacketServerNSCGSR`

132: Game Over Stats
********************

This packet is send in response to the game over packet. It contains information regarding how well each player did.

Payload:

+-------+---------------------------------------------------------------------+
| Size  | Description                                                         |
+=======+=====================================================================+
| 1     | NB of players sent in this packet. This determine the lenght of all |
|       | the list send after                                                 |
+-------+---------------------------------------------------------------------+
| - 1   | - First player's index                                              |
| - 1   | - Second player's index                                             |
| - 1   | - ...                                                               |
| - 1   | - Last player's index                                               |
+-------+---------------------------------------------------------------------+
| 4..4  | Player's scores                                                     |
+-------+---------------------------------------------------------------------+
| 1..1  | Player's grades:                                                    |
|       |                                                                     |
|       | - 0: AAAA                                                           |
|       | - 1: AAA                                                            |
|       | - 2: AA                                                             |
|       | - 3: A                                                              |
|       | - 4: B                                                              |
|       | - 5: C                                                              |
|       | - 6: D                                                              |
|       | - 7: F                                                              |
+-------+---------------------------------------------------------------------+
| 1..1  | Player's difficulties:                                              |
|       |                                                                     |
|       | - 0: Beginner                                                       |
|       | - 1: Easy                                                           |
|       | - 2: Medium                                                         |
|       | - 3: Hard                                                           |
|       | - 4: Expert                                                         |
+-------+---------------------------------------------------------------------+
| 2..2  | NB of Player's flawless                                             |
+-------+---------------------------------------------------------------------+
| 2..2  | NB of Player's perfect                                              |
+-------+---------------------------------------------------------------------+
| 2..2  | NB of Player's great                                                |
+-------+---------------------------------------------------------------------+
| 2..2  | NB of Player's good                                                 |
+-------+---------------------------------------------------------------------+
| 2..2  | NB of Player's boo                                                  |
+-------+---------------------------------------------------------------------+
| 2..2  | NB of Player's miss                                                 |
+-------+---------------------------------------------------------------------+
| 2..2  | NB of Player's held                                                 |
+-------+---------------------------------------------------------------------+
| 2..2  | NB of Player's max_combo                                            |
+-------+---------------------------------------------------------------------+
| NT..NT| Player's Options                                                    |
+-------+---------------------------------------------------------------------+

See :class:`smserver.smutils.smpacket.SMPacketServerNSCGON`

133: Scoreboard update
**********************

This will update the client's scoreboard.

Payload:

+-------+---------------------------------------------------------------------+
| Size  | Description                                                         |
+=======+=====================================================================+
| 1     | Which section to update in the scoreboard                           |
|       |                                                                     |
|       | - 0: Update the names                                               |
|       | - 1: Update the combos                                              |
|       | - 2: Update the grade                                               |
+-------+---------------------------------------------------------------------+
| 1     | NB of players sent in this packet. This determine the lenght of all |
|       | the list send after                                                 |
+-------+---------------------------------------------------------------------+
| 1..1  | If usage is names:                                                  |
|       |                                                                     |
|       | List of player's index (determine by the NSCUUL packet)             |
+-------+---------------------------------------------------------------------+
| 2..2  | If usage is combos:                                                 |
|       |                                                                     |
|       | List of player's combo                                              |
+-------+---------------------------------------------------------------------+
| 1..1  | If usage is grades:                                                 |
|       |                                                                     |
|       | List of player's grades                                             |
+-------+---------------------------------------------------------------------+

See :class:`smserver.smutils.smpacket.SMPacketServerNSCGSU`

134: System Message
*******************

Send a system message to user

Payload:

+-------+---------------------------------------------------------------------+
| Size  | Description                                                         |
+=======+=====================================================================+
| NT    | Message                                                             |
+-------+---------------------------------------------------------------------+

See :class:`smserver.smutils.smpacket.SMPacketServerNSCSU`

135: Chat message
*****************

Add a chat message to the chat window on some StepMania screens.

Payload:

+-------+---------------------------------------------------------------------+
| Size  | Description                                                         |
+=======+=====================================================================+
| NT    | Message                                                             |
+-------+---------------------------------------------------------------------+

See :class:`smserver.smutils.smpacket.SMPacketServerNSCCM`

136: Request Start Game
***********************

Tell client to start song/ask if client has song

Payload:

+-------+---------------------------------------------------------------------+
| Size  | Description                                                         |
+=======+=====================================================================+
| 1     | Usage of message                                                    |
|       |                                                                     |
|       | - 0: see if client has song                                         |
|       | - 1: see if client has song, if so, scroll to song                  |
|       | - 2: See if client has song, if so, scroll to song, and play that   |
|       | song                                                                |
|       | - 3: Blindly start song                                             |
+-------+---------------------------------------------------------------------+
| NT    | Song Title    (As gotten by GetTranslitMainTitle)                   |
+-------+---------------------------------------------------------------------+
| NT    | Song Artist   (As Gotten by GetTranslitArtist)                      |
+-------+---------------------------------------------------------------------+
| NT    | Song Subtitle (As gotten by GetTranslitSubTitle)                    |
+-------+---------------------------------------------------------------------+

See :class:`smserver.smutils.smpacket.SMPacketServerNSCRSG`

137: Update User List
*********************

This sends all the users currently connected

Pay attention of the user's order in this packet. The index of each user will server for NSCGON and NSCGSU packet.

+-------+---------------------------------------------------------------------+
| Size  | Description                                                         |
+=======+=====================================================================+
| 1     | Number max of player's allowed                                      |
+-------+---------------------------------------------------------------------+
| 1     | NB of players sent in this packet. This determine the lenght of all |
|       | the list send after                                                 |
+-------+---------------------------------------------------------------------+
| 1     | First player's status                                               |
|       |                                                                     |
|       | - 0: Inactive (no info on this user yet)                            |
|       | - 1: Active (You know who is is)                                    |
|       | - 2: In music selection screen                                      |
|       | - 3: In options                                                     |
|       | - 4: In evaluation                                                  |
+-------+---------------------------------------------------------------------+
| NT    | First player's name                                                 |
+-------+---------------------------------------------------------------------+
| ...   |                                                                     |
+-------+---------------------------------------------------------------------+
| 1     | Last player's status                                                |
+-------+---------------------------------------------------------------------+
| NT    | Last player's name                                                  |
+-------+---------------------------------------------------------------------+

See :class:`smserver.smutils.smpacket.SMPacketServerNSCCUUL`


138: Change to Select Music Screen
**********************************

Force change to Networking select music screen.

Payload:

+-------+---------------------------------------------------------------------+
| Size  | Description                                                         |
+=======+=====================================================================+
| NT    | Set specified gametype                                              |
+-------+---------------------------------------------------------------------+
| NT    | Set specified style                                                 |
+-------+---------------------------------------------------------------------+

See :class:`smserver.smutils.smpacket.SMPacketServerNSSCSMS`

139: Reserved
*************

Reserved

See :class:`smserver.smutils.smpacket.SMPacketServerNSCUOpts`

140: SMOnline Packet
********************

The SMLan packet 140 is a wrapper for the SMOnline packet.

Payload:

+-----------+-----------------------------------------------------------------+
| Size      | Description                                                     |
+===========+=================================================================+
| SMOPacket | A SMO packet (Command + SMO payload).                           |
+-----------+-----------------------------------------------------------------+

See :class:`smserver.smutils.smpacket.SMPacketServerNSSMONL`

141: Formatted information packet
*********************************

Send formatted information regarding the server back to the player.

Payload:

+-------+---------------------------------------------------------------------+
| Size  | Description                                                         |
+=======+=====================================================================+
| NT    | Server Name                                                         |
+-------+---------------------------------------------------------------------+
| 2     | Port the server is listening on                                     |
+-------+---------------------------------------------------------------------+
| 2     | Number of players connected                                         |
+-------+---------------------------------------------------------------------+

See :class:`smserver.smutils.smpacket.SMPacketServerNSCFormatted`

142: Attack Client
******************

Payload:

+-------+---------------------------------------------------------------------+
| Size  | Description                                                         |
+=======+=====================================================================+
| 1     | Player # (0 or 1)                                                   |
+-------+---------------------------------------------------------------------+
| 4     | Time to last (in ms)                                                |
+-------+---------------------------------------------------------------------+
| NT    | Text describing modifiers                                           |
+-------+---------------------------------------------------------------------+

See :class:`smserver.smutils.smpacket.SMPacketServerNSCAttack`

143: XMLPacket
**************

This packet contains XML data. Don't know yet when it is used.

Payload:

+------+----------------------------------------------------------------------+
| Size | Description                                                          |
+======+======================================================================+
| NT   | XML Data                                                             |
+------+----------------------------------------------------------------------+

See :class:`smserver.smutils.smpacket.SMPacketServerXMLPacket`

SMOClient Packet
****************


SMOServer Packet
****************

