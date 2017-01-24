#!/usr/bin/env python3
# -*- coding: utf8 -*-


from smserver import models
from smserver import smutils
from smserver.chathelper import with_color
from smserver.chatplugin import ChatPlugin


class ChatHelp(ChatPlugin):
    command = "help"
    helper = "Show help"

    def __call__(self, serv, message):
        for command, action in sorted(serv.server.chat_commands.items()):
            if not action.can(serv):
                continue

            serv.send_message("/%s: %s" % (command, action.helper), to="me")


class ChatUserListing(ChatPlugin):
    command = "users"
    helper = "List users"

    def __call__(self, serv, message):
        users = serv.session.query(models.User).filter_by(online=True)
        max_users = serv.server.config.server.get("max_users")
        if serv.room:
            users = users.filter_by(room_id=serv.room.id)
            max_users = serv.room.max_users

        users = users.all()
        serv.send_message("%s/%s players online" % (len(users), max_users), to="me")

        for user in users:
            serv.send_message(
                "%s (in %s)" % (
                    user.fullname_colored(serv.conn.room),
                    user.enum_status.name),
                to="me")


class ChatTimestamp(ChatPlugin):
    command = "timestamp"
    helper = "Enable chat timestamps"

    def __call__(self, serv, message):
        if serv.conn.chat_timestamp:
            serv.conn.chat_timestamp = False
            serv.send_message("Chat timestamp disabled", to="me")
        else:
            serv.send_message("Chat timestamp enabled", to="me")
            serv.conn.chat_timestamp = True

        for user in serv.active_users:
            user.chat_timestamp = serv.conn.chat_timestamp


class ShowOffset(ChatPlugin):
    command = "showoffset"
    helper = "Enable average offset display after a song"

    def __call__(self, serv, message):

        for user in serv.active_users:
            if user.show_offset:
                user.show_offset = False
                serv.send_message("Offset diplay disabled", to="me")
            else:
                user.show_offset = True
                serv.send_message("Offset diplay enabled", to="me")


class Profile(ChatPlugin):
    command = "profile"
    helper = "Display profile information"

    def __call__(self, serv, message):

        for user in serv.active_users:
            serv.send_message("Name: %s" % with_color(user.name), to="me")
            serv.send_message("XP: %s" % user.xp, to="me")
            serv.send_message("Rank: %s" % user.rank, to="me")
            for skillset in models.ranked_song.Skillsets:
                rating = eval("user.rating_" + skillset.name)
                serv.send_message(skillset.name.capitalize()+": %f" %  rating, to="me")


class FriendNotification(ChatPlugin):
    command = "friendnotif"
    helper = "Enable notifications whenever a friend gets on/off line"

    def __call__(self, serv, message):

        for user in serv.active_users:
            if user.friend_notifications:
                user.friend_notifications = False
                serv.send_message("Friend notifications disabled", to="me")
            else:
                user.friend_notifications = True
                serv.send_message("Friend notifications enabled", to="me")


class AddFriend(ChatPlugin):
    command = "addfriend"
    helper = "Add a friend. /addfriend user"

    def __call__(self, serv, message):
        for user in serv.active_users:
            if not user:
                return
            newfriend = serv.session.query(models.User).filter_by(name=message).first()
            if not newfriend:
                serv.send_message("Unknown user %s" % with_color(message), to="me")
                return
            if newfriend.name == user.name:
                serv.send_message("Cant befriend yourself", to="me")
                return
            friendships = serv.session.query(models.Friendship).filter( \
                ((models.Friendship.user1_id == user.id) & (models.Friendship.user2_id == newfriend.id)) |  \
                (models.Friendship.user2_id == user.id) & (models.Friendship.user1_id == newfriend.id))
            if not friendships.first():
                serv.session.add(models.Friendship(user1_id = user.id, user2_id = newfriend.id, state = 0))
                serv.send_message("Friend request sent to %s" % with_color(message), to="me")
            else:
                friendships = friendships.all()
                if len(friendships) != 1:
                    if friendship[0].state == 2:
                        if friendship.user1_id == user.id:
                            Unignore.__call__(self, serv, message)
                            friendship = friendships[1]
                    if friendship[1].state == 2:
                        if friendship.user1_id == user.id:
                            Unignore.__call__(self, serv, message)
                            friendship = friendships[0]
                else:
                    friendship = friendships[0]
                if friendship.state == 1:
                    serv.send_message("%s is already friends with you" % with_color(message), to="me")
                    return
                if friendship.state == 2:
                    serv.send_message("Cant send %s a friend request" % with_color(message), to="me")
                    return
                if friendship.user1_id == user.id:
                    serv.send_message("Already sent a friend request to %s" % with_color(message), to="me")
                    return
                friendship.state = 1
                serv.send_message("Accepted friend request from %s" % with_color(message), to="me")
            serv.session.commit()


class Ignore(ChatPlugin):
    command = "ignore"
    helper = "Ignore someone(Can't send friend requests or pm). /ignore user"

    def __call__(self, serv, message):
        for user in serv.active_users:
            if not user:
                return
            newignore = serv.session.query(models.User).filter_by(name=message).first()
            if not newignore:
                serv.send_message("Unknown user %s" % with_color(message), to="me")
                return
            if newignore.name == user.name:
                serv.send_message("Cant ignore yourself", to="me")
                return
            friendships = serv.session.query(models.Friendship).filter( \
                ((models.Friendship.user1_id == user.id) & (models.Friendship.user2_id == newignore.id)) |  \
                (models.Friendship.user2_id == user.id) & (models.Friendship.user1_id == newignore.id))
            friendship = friendships.first()
            if not friendship:
                serv.session.add(models.Friendship(user1_id = user.id, user2_id = newignore.id, state = 2))
                serv.send_message("%s ignored" % with_color(message), to="me")
            else:
                if friendship.state == 2:
                    if friendship.user1_id == user.id:
                        serv.send_message("%s is already ignored" % with_color(message), to="me")
                    else:
                        friendshiptwo = friendships.all()
                        if len(friendshiptwo) > 1:
                            friendshiptwo = friendshiptwo[1]
                            if friendshiptwo.user1_id == user.id:
                                serv.send_message("%s is already ignored" % with_color(message), to="me")
                                return
                        serv.session.add(models.Friendship(user1_id = user.id, user2_id = newignore.id, state = 2))
                        serv.send_message("%s ignored" % with_color(message), to="me")
                    return
                friendship.state = 2
                friendship.user1_id = user.id
                friendship.user2_id = newignore.id
                serv.send_message("%s ignored" % with_color(message), to="me")
            serv.session.commit()



class Unignore(ChatPlugin):
    command = "unignore"
    helper = "Stop ignoring someone. /unignore user"

    def __call__(self, serv, message):
        for user in serv.active_users:
            if not user:
                return
            newignore = serv.session.query(models.User).filter_by(name=message).first()
            if not newignore:
                serv.send_message("Unknown user %s" % with_color(message), to="me")
                return
            friendship = serv.session.query(models.Friendship).filter_by(user1_id = user.id).filter_by(user2_id = newignore.id).filter_by(state = 2).first()
            if friendship:
                serv.session.delete(friendship)
                serv.session.commit()
                serv.send_message("%s unignored" % with_color(message), to="me")
                return
            serv.send_message("%s is not currently ignored. Cant unignore" % with_color(message), to="me")



class Friendlist(ChatPlugin):
    command = "friendlist"
    helper = "Show friendlist"

    def __call__(self, serv, message):
        for user in serv.active_users:
            if not user:
                return
            friends = serv.session.query(models.Friendship).filter_by(state = 1).filter((models.Friendship.user1_id == user.id) | models.Friendship.user2_id == user.id).all()
            friendsStr = ""
            for friend in friends:
                if friend.user1_id == user.id:
                    frienduser = serv.session.query(models.User).filter_by(id = friend.user2_id).first()
                else:
                    frienduser = serv.session.query(models.User).filter_by(id = friend.user1_id).first()
                friendsStr += frienduser.name + ", "
            if friendsStr.endswith(", "):
                friendsStr = friendsStr[:-2]
            requests = serv.session.query(models.Friendship).filter_by(user2_id = user.id).filter_by(state = 0).all()
            requestsStr = ""
            for request in requests:
                requestsStr += serv.session.query(models.User).filter_by(id=request.user1_id).first().name + ", "
            if requestsStr.endswith(", "):
                requestsStr = requestsStr[:-2]
            requestsoutgoing = serv.session.query(models.Friendship).filter_by(user1_id = user.id).filter_by(state = 0).all()
            requestsoutgoingStr = ""
            for request in requestsoutgoing:
                requestsoutgoingStr += serv.session.query(models.User).filter_by(id=request.user2_id).first().name + ", "
            if requestsoutgoingStr.endswith(", "):
                requestsoutgoingStr = requestsoutgoingStr[:-2]
            ignores = serv.session.query(models.Friendship).filter_by(user1_id = user.id).filter_by(state = 2).all()
            ignoresStr = ""
            for ignore in ignores:
                ignoresStr += serv.session.query(models.User).filter_by(id=ignore.user2_id).first().name + ", "
            if ignoresStr.endswith(", "):
                ignoresStr = ignoresStr[:-2]

            serv.send_message("Friends: %s" % friendsStr, to="me")
            serv.send_message("Incoming requests: %s" % requestsStr, to="me")
            serv.send_message("Outgoing requests: %s" % requestsoutgoingStr, to="me")
            serv.send_message("Ignoring: %s" % ignoresStr, to="me")


class PrivateMessage(ChatPlugin):
    command = "pm"
    helper = "Send a private message. /pm user message"

    def __call__(self, serv, message):
        user = models.User.from_ids(serv.conn.users, serv.session)
        user = user[0]
        #user = serv.session.query(models.User).filter_by(online = True).filter_by(last_ip = serv.conn.ip).first()
        if not user:
            return
        message = message.split(' ', 1)
        if len(message) < 2:
            serv.send_message("Need a text message to send", to="me")
            return
        if self.sendpm(serv, user, message[0], message[1]) == False:
            if '_' in message[0]:
                self.sendpm(serv, user, message[0].replace('_',' '), message[1])

    def sendpm(self, serv, user, receptorname, message):
        receptor = serv.session.query(models.User).filter_by(online=True).filter_by(name=receptorname).first()
        if not receptor:
            serv.send_message("Could not find %s online" % with_color(receptorname), to="me")
            return False
        if receptor.name == user.name:
            serv.send_message("Cant pm yourself", to="me")
            return False
        ignore = serv.session.query(models.Friendship).filter( \
            (((models.Friendship.user1_id == user.id) & (models.Friendship.user2_id == receptor.id)) |  \
            ((models.Friendship.user2_id == user.id) & (models.Friendship.user1_id == receptor.id))) &  \
            (models.Friendship.state == 2)).first()
        if ignore:
            serv.send_message("Cant send %s a private message" %with_color(receptorname), to="me")
            return False
        if not receptor:
            serv.send_message("Could not find %s online" % with_color(receptorname), to="me")
            return False
        serv.send_message("To %s : %s" % (with_color(receptor.name), message), to="me")
        receptor = serv.server.find_connection(receptor.id)
        #if i do what's commented both players get the message for some reason
        #serv.send_message("From %s : %s" % (with_color(user.name), message), receptor)
        receptor.send(smutils.smpacket.SMPacketServerNSCCM(message="From %s : %s" % (with_color(user.name), message)))
        return True



