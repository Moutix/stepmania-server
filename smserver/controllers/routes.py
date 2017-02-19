""" Routes files """


from smserver.smutils.smpacket import smcommand
from smserver.controllers import legacy

ROUTES = {
    # Legacy controller for compatibility with Stepmania 5.X
    smcommand.SMClientCommand.NSCHello: legacy.hello.HelloController,
    smcommand.SMClientCommand.NSCCM: legacy.chat.ChatController,
    smcommand.SMClientCommand.NSCFormatted: legacy.discovery.DiscoveryController,
    smcommand.SMClientCommand.NSCGON: legacy.game_over.GameOverController,
    smcommand.SMClientCommand.NSCGSR: legacy.game_start_request.StartGameRequestController,
    smcommand.SMClientCommand.NSCGSU: legacy.game_status_update.GameStatusUpdateController,
    smcommand.SMClientCommand.NSCRSG: legacy.request_start_game.RequestStartGameController,
    smcommand.SMClientCommand.NSSMONL:legacy.smo.SMOController,
    smcommand.SMClientCommand.NSCSU: legacy.user_profil.UserProfilController,
    smcommand.SMClientCommand.NSSCSMS: legacy.user_screen.UserStatusController,

    smcommand.SMOClientCommand.LOGIN: legacy.login.LoginController,
    smcommand.SMOClientCommand.ENTERROOM: legacy.enter_room.EnterRoomController,
    smcommand.SMOClientCommand.CREATEROOM: legacy.create_room.CreateRoomController,
    smcommand.SMOClientCommand.ROOMINFO: legacy.room_info.RoomInfoController,
}
