""" General Chat command to handle """

from smserver import models
from smserver import smutils
from smserver.chatplugin import ChatPlugin
from smserver.chathelper import with_color


class ChatHelp(ChatPlugin):
    """ Display the list of all the commands """

    command = "help"
    helper = "Show help"

    def __call__(self, resource, message):
        response = []

        commands = self.server.chat_commands

        if message:
            if message not in commands or not commands[message].can(resource.connection):
                return ["Unknown command %s" % message]

            return ["/%s: %s" % (message, commands[message].helper)]

        for command, action in sorted(commands.items()):
            if not action.can(resource.connection):
                continue

            response.append("/%s: %s" % (command, action.helper))

        return response

class ChatUserListing(ChatPlugin):
    """ List the users connected """

    command = "users"
    helper = "List users"

    def __call__(self, resource, message, *, limit=20):
        response = []

        connection = resource.connection

        users = resource.session.query(models.User).filter_by(online=True)
        max_users = self.server.config.server.get("max_users")
        if connection.room:
            users = users.filter_by(room_id=connection.room_id)
            max_users = connection.room.max_users

        response.append("%s/%s players online" % (users.count(), max_users))

        for user in users.order_by("name").limit(limit):
            response.append(
                "%s (in %s)" % (
                    user.fullname_colored(connection.room_id),
                    user.enum_status.name
                )
            )
        return response

class ChatTimestamp(ChatPlugin):
    """ Add the timestamp in the chat messages """

    command = "timestamp"
    helper = "Show timestamp"

    def __call__(self, serv, message):
        #FIXME need to be store elsewhere (don't work for the moment)

        if serv.conn.chat_timestamp:
            serv.conn.chat_timestamp = False
            serv.send_message("Chat timestamp disabled", to="me")
        else:
            serv.send_message("Chat timestamp enabled", to="me")
            serv.conn.chat_timestamp = True

        for user in serv.active_users:
            user.chat_timestamp = serv.conn.chat_timestamp

class FriendNotifications(ChatPlugin):
    command = "friendnotif"
    helper = "Enable notifications whenever a friend gets on/off line. /friendnotif"

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
            relationships = serv.session.query(models.Relationship).filter( \
                ((models.Relationship.user1_id == user.id) & (models.Relationship.user2_id == newfriend.id)) |  \
                (models.Relationship.user2_id == user.id) & (models.Relationship.user1_id == newfriend.id))
            if not relationships.first():
                serv.session.add(models.Relationship(user1_id = user.id, user2_id = newfriend.id, state = 0))
                serv.send_message("Friend request sent to %s" % with_color(message), to="me")
            else:
                relationships = relationships.all()
                if len(relationships) != 1:
                    if friendship[0].state == 2:
                        if friendship.user1_id == user.id:
                            Unignore.__call__(self, serv, message)
                            friendship = relationships[1]
                    if friendship[1].state == 2:
                        if friendship.user1_id == user.id:
                            Unignore.__call__(self, serv, message)
                            friendship = relationships[0]
                else:
                    friendship = relationships[0]
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

class RemoveFriend(ChatPlugin):
    command = "removefriend"
    helper = "Remove a friend. /removefriend user"

    def __call__(self, serv, message):
        for user in serv.active_users:
            if not user:
                return
            oldfriend = serv.session.query(models.User).filter_by(name=message).first()
            if not oldfriend:
                serv.send_message("Unknown user %s" % with_color(message), to="me")
                return
            friendship = serv.session.query(models.Relationship).filter( \
                ((models.Relationship.user1_id == user.id) & (models.Relationship.user2_id == oldfriend.id) & ((models.Relationship.state == 1) | (models.Relationship.state == 0))) | \
                ((models.Relationship.user2_id == user.id) & (models.Relationship.user1_id == oldfriend.id) & ((models.Relationship.state == 1) | (models.Relationship.state == 0))) )
            friendships = friendship.first()
            if not friendships:
                serv.send_message("%s is not your friend" % with_color(message), to="me")
            serv.session.delete(friendships)
            serv.session.commit()
            serv.send_message("%s is no longer your friend" % with_color(message), to="me")


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
            relationships = serv.session.query(models.Relationship).filter( \
                ((models.Relationship.user1_id == user.id) & (models.Relationship.user2_id == newignore.id)) |  \
                (models.Relationship.user2_id == user.id) & (models.Relationship.user1_id == newignore.id))
            relationships = relationships.all()
            ignored = False
            for relationship in relationships:
                if relationship.state == 0 or relationship.state == 1:
                    serv.session.delete(relationship)
                    serv.send_message("%s is no longer your friend" % with_color(message), to="me")
                elif relationship.state == 2 and relationship.user1_id == user.id:
                    serv.send_message("%s is already ignored" % with_color(message), to="me")
                    ignored = True
            if not ignored:
                serv.session.add(models.Relationship(user1_id = user.id, user2_id = newignore.id, state = 2))
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
            ignore = serv.session.query(models.Relationship).filter_by(user1_id = user.id).filter_by(user2_id = newignore.id).filter_by(state = 2).first()
            if ignore:
                serv.session.delete(ignore)
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
            friends = serv.session.query(models.Relationship).filter_by(state = 1).filter((models.Relationship.user1_id == user.id) | models.Relationship.user2_id == user.id).all()
            friendsStr = ""
            for friend in friends:
                if friend.user1_id == user.id:
                    frienduser = serv.session.query(models.User).filter_by(id = friend.user2_id).first()
                else:
                    frienduser = serv.session.query(models.User).filter_by(id = friend.user1_id).first()
                friendsStr += frienduser.name + ", "
            if friendsStr.endswith(", "):
                friendsStr = friendsStr[:-2]
            requests = serv.session.query(models.Relationship).filter_by(user2_id = user.id).filter_by(state = 0).all()
            requestsStr = ""
            for request in requests:
                requestsStr += serv.session.query(models.User).filter_by(id=request.user1_id).first().name + ", "
            if requestsStr.endswith(", "):
                requestsStr = requestsStr[:-2]
            requestsoutgoing = serv.session.query(models.Relationship).filter_by(user1_id = user.id).filter_by(state = 0).all()
            requestsoutgoingStr = ""
            for request in requestsoutgoing:
                requestsoutgoingStr += serv.session.query(models.User).filter_by(id=request.user2_id).first().name + ", "
            if requestsoutgoingStr.endswith(", "):
                requestsoutgoingStr = requestsoutgoingStr[:-2]
            ignores = serv.session.query(models.Relationship).filter_by(user1_id = user.id).filter_by(state = 2).all()
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
        ignore = serv.session.query(models.Relationship).filter( \
            (((models.Relationship.user1_id == user.id) & (models.Relationship.user2_id == receptor.id)) |  \
            ((models.Relationship.user2_id == user.id) & (models.Relationship.user1_id == receptor.id))) &  \
            (models.Relationship.state == 2)).first()
        if ignore:
            serv.send_message("Cant send %s a private message" %with_color(receptorname), to="me")
            return False
        if not receptor:
            serv.send_message("Could not find %s online" % with_color(receptorname), to="me")
            return False
        serv.send_message("To %s : %s" % (with_color(receptor.name), message), to="me")
        receptor = serv.server.find_connection(receptor.id)
        #if i do what's commented both players get the message
        #serv.send_message("From %s : %s" % (with_color(user.name), message), receptor)
        receptor.send(smutils.smpacket.SMPacketServerNSCCM(message="From %s : %s" % (with_color(user.name), message)))
        return True

