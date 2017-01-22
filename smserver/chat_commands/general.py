#!/usr/bin/env python3
# -*- coding: utf8 -*-


from smserver import models
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
    helper = "Enable timestamps"

    def __call__(self, serv, message):
        if serv.conn.chat_timestamp:
            serv.conn.chat_timestamp = False
            serv.send_message("Chat timestamp disabled", to="me")
        else:
            serv.send_message("Chat timestamp enabled", to="me")
            serv.conn.chat_timestamp = True

        for user in serv.active_users:
            user.chat_timestamp = serv.conn.chat_timestamp


class AddFriend(ChatPlugin):
    command = "addfriend"
    helper = "Add friend"

    def __call__(self, serv, message):
        user = serv.session.query(models.User).filter_by(online = True).filter_by(last_ip = serv.conn.ip).first()
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
            for friendship in friendships.all():
                if friendship.state == 1:
                    serv.send_message("%s is already friends with you" % with_color(message), to="me")
                    return
                if friendship.state == 2:
                    if friendship.user1_id == user.id:
                        Unignore.__call__(self, serv, message)
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
    helper = "Ignore someone(Can't send friend requests or pm)"

    def __call__(self, serv, message):
        user = serv.session.query(models.User).filter_by(online = True).filter_by(last_ip = serv.conn.ip).first()
        if not user:
            return
        newignore = serv.session.query(models.User).filter_by(name=message).first()
        if not newignore:
            serv.send_message("Unknown user %s" % with_color(message), to="me")
            return
        if newignore.name == user.name:
            serv.send_message("Cant ignore yourself", to="me")
            return
        friendship = serv.session.query(models.Friendship).filter( \
            ((models.Friendship.user1_id == user.id) & (models.Friendship.user2_id == newfriend.id)) |  \
            (models.Friendship.user2_id == user.id) & (models.Friendship.user1_id == newfriend.id)).first()
        if not friendship:
            serv.session.add(models.Friendship(user1_id = user.id, user2_id = newfriend.id, state = 2))
            serv.send_message("%s ignored" % with_color(message), to="me")
        else:
            if friendship.state == 2:
                if friendship.user1_id == user.id:
                    serv.send_message("%s is already ignored" % with_color(message), to="me")
                else:
                    serv.session.add(models.Friendship(user1_id = user.id, user2_id = newfriend.id, state = 2))
                    serv.send_message("%s ignored" % with_color(message), to="me")
                return
            friendship.state = 2
            friendship.user1_id = user.id
            friendship.user2_id = newignore.id
            serv.send_message("%s ignored" % with_color(message), to="me")
        serv.session.commit()



class Unignore(ChatPlugin):
    command = "unignore"
    helper = "Stop ignoring someone"

    def __call__(self, serv, message):
        user = serv.session.query(models.User).filter_by(online = True).filter_by(last_ip = serv.conn.ip).first()
        if not user:
            return
        newignore = serv.session.query(models.User).filter_by(name=message).first()
        if not newignore:
            serv.send_message("Unknown user %s" % with_color(message), to="me")
            return
        friendship = serv.session.query(models.Friendship).filter_by(user1_id = user.id).filter_by(user2_id = newfriend.id).filter_by(state = 2).first()
        if friendship:
            friendship.delete()
            serv.session.commit()
            serv.send_message("%s unignored" % with_color(message), to="me")
            return
        serv.send_message("%s is not currently ignored. Cant unignore" % with_color(message), to="me")



class Friendlist(ChatPlugin):
    command = "friendlist"
    helper = "Show friendlist"

    def __call__(self, serv, message):
        user = serv.session.query(models.User).filter_by(online = True).filter_by(last_ip = serv.conn.ip).first()
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

        serv.send_message("Friends: %s" % friendsStr, to="me")
        serv.send_message("Pending requests: %s" % requestsStr, to="me")


class PrivateMessage(ChatPlugin):
    command = "pm"
    helper = "Send a private message"

    def __call__(self, serv, message):
        user = serv.session.query(models.User).filter_by(online = True).filter_by(last_ip = serv.conn.ip).first()
        if not user:
            return
        message = message.split(' ', 1)
        if len(message) < 2:
            serv.send_message("Need a text message to send", to="me")
            return
        receptor = serv.session.query(models.User).filter_by(online=True).filter_by(name=message[0]).first()
        if not receptor:
            serv.send_message("Could not find %s online" % with_color(message[0]), to="me")
            return
        if receptor.name == user.name:
            serv.send_message("Cant pm yourself", to="me")
            return
        ignore = serv.session.query(models.Friendship).filter( \
            (((models.Friendship.user1_id == user.id) & (models.Friendship.user2_id == receptor.id)) |  \
            ((models.Friendship.user2_id == user.id) & (models.Friendship.user1_id == receptor.id))) &  \
            (models.Friendship.state == 2)).first()
        if ignore:
            serv.send_message("Cant send %s a private message" %with_color( message[0]), to="me")
            return    
        receptor = serv.server.find_connection(receptor.id)
        if not receptor:
            serv.send_message("Could not find %s online" % with_color(message[0]), to="me")
            return
        serv.send_message("To %s : %s" % (with_color(user.name), message[1]), to="me")
        serv.send_message("From %s : %s" % (with_color(user.name), message[1]), receptor)



