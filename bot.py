# python modules
import logging
import random

# telegram api
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, ParseMode, Update, ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import (
    CallbackQueryHandler, ChosenInlineResultHandler,
    CommandHandler, InlineQueryHandler, ConversationHandler, CallbackContext, Filters, MessageHandler
)

# bot modules
import helpers
import logger as loggero
import stats
from actions import do_play_card
from config import MIN_PLAYERS, TIME_TO_START
from errors import (AlreadyGameInChat, AlreadyJoinedError,
                    GameAlreadyStartedError, LobbyClosedError,
                    MaxPlayersReached, NoGameInChatError, NotEnoughNkap,
                    NotEnoughPlayersError)
from global_variables import dispatcher, gm, updater
from results import (add_card, add_no_game, add_not_started, add_special_card,
                     check_quick_win, get_game_status)
from start_bot import start_bot
from utils import (TIMEOUT, answer_async, delete_start_msgs, pin_game_message,
                   mention, send_animation_async, send_async, user_is_creator,
                   user_is_creator_or_admin, n_format)
from gifs import start_Anim, win_forfeit_Anim
from interactions import tu_joue_combien_txt, i_do_not_understand, just_launched

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.DEBUG)
logger = logging.getLogger(__name__)


def call_me_back(update, context):
    bot = context.bot
    """Handler for /call_me_back command, pm people for next game"""
    chat_id = update.message.chat_id
    if update.message.chat.type == 'private':
        send_async(bot, chat_id, text=f"Envoyez cette commande dans un groupe de jeu et vous serez notifié lorsqu'une nouvelle partie sera lancé.")
    else:
        try:
            send_async(bot, update.message.from_user.id,
                       text=f"Sois posé, je vais te notifier quand nous allons lancer.")
            gm.remind_dict[chat_id].add(update.message.from_user.id)
        except KeyError:
            gm.remind_dict[chat_id] = {update.message.from_user.id}


def initiate_nkap(update: Update, context: CallbackContext):
    chat_id = update.message.chat_id
    if gm.chatid_games:
        if len(gm.chatid_games[chat_id]) >= 1:
            send_async(context.bot, chat_id,
                       text=f'Calme toi! Nous jouons l\'argent ici.')
            return ConversationHandler.END
    if not context.args:

        send_async(context.bot, chat_id, text=tu_joue_combien_txt(),
                   reply_to_message_id=update.message.message_id)
        return 1
    else:
        new_nkap_game(update, context,
                      montant=context.args[0].replace(" ", ""))


def stop_nkap_game(update: Update, context: CallbackContext):
    send_async(context.bot, update.message.chat_id,
               text=f'Ok c\'est free, Mboutman.',  reply_markup=ReplyKeyboardRemove())
    return ConversationHandler.END


def new_nkap_game(update, context, montant=None):
    """/new_nkap_game command handler"""

    chat_id = update.message.chat_id
    title = update.message.chat.title
    bot = context.bot
    current_bet = 0

    try:
        if montant is not None:
            current_bet = int(montant.replace(" ", ""))
        else:
            current_bet = int(update.message.text.replace(" ", ""))
    except ValueError:
        reply_keyboard = [['50000', '25000', '10000', '5000'], [
            '2500', '1000', '500', '/ndem']]
        send_async(context.bot, chat_id,
                   text=i_do_not_understand(), reply_to_message_id=update.message.message_id, reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True, resize_keyboard=True, selective=True))
        return 1

    if update.message.chat.type == 'private':
        helpers.help_handler(update, context)
    else:
        if chat_id in gm.remind_dict:
            for user in gm.remind_dict[chat_id]:
                send_async(
                    bot, user, text=f"Va jouer dans le groupe [{title}]({update.message.link}). La mise c'est {n_format(current_bet)}")
            del gm.remind_dict[chat_id]

        try:
            game = gm.new_game(update.message.chat)
            game.starter = update.message.from_user
            game.owner.append(update.message.from_user.id)
            game.nkap = True
            game.bet = current_bet
            game.game_info = []

            join_btn = [[InlineKeyboardButton(
                "🖐🏽 - Rejoindre", callback_data="join_game"), InlineKeyboardButton(
                    "Notifier - 🔔", callback_data="notify")], [InlineKeyboardButton(
                        "Lancer - 🚀", callback_data="start_game")]]

            # Reply to inform the start of game
            send_animation_async(
                context.bot, chat_id, animation=start_Anim(), caption=just_launched(mention(game.starter), n_format(current_bet)), reply_markup=InlineKeyboardMarkup(join_btn), to_delete=True)

            stats.user_started(update.message.from_user.id)

            # start the game after TIME_TO_START secs
            context.job_queue.run_once(
                start_the_game_soon, TIME_TO_START/2, context=update)

        except AlreadyGameInChat:
            send_async(context.bot, chat_id,
                       text=f'Calme toi! Nous jouons l\'argent ici.', to_delete=True)

    return ConversationHandler.END


def start_the_game_soon(context):
    chat = context.job.context.effective_message.chat
    try:
        game = gm.chatid_games[chat.id][-1]
    except (KeyError, IndexError):
        return
    if not game.started:
        send_async(context.bot, chat.id,
                   text=f'Je partage les cartes dans **{int(TIME_TO_START/2)} secondes**...', to_delete=True)
        context.job_queue.run_once(
            start_the_game, TIME_TO_START/2, context=context.job.context)


def start_the_game(context):
    chat = context.job.context.effective_message.chat
    user = context.job.context.effective_user

    try:
        game = gm.chatid_games[chat.id][-1]
    except (KeyError, IndexError):
        return
    if len(game.players) >= MIN_PLAYERS and not game.started:
        start_lamap(context.job.context, context)
        return
    elif not game.started:
        send_async(context.bot, chat.id,
                   text=f'Les gars ne sont pas chauds, je tue le way. Utilise /call\_me\_back et je vais te notifier quand on va lancer ici.')
        delete_start_msgs(context.bot, chat.id)
        # kill previous game
        gm.chatid_games[chat.id] = []
        logger.debug("END GAME - NOTENOUGHPLAYERS in chat " + str(chat.id))
        return


def join_game(update, context):
    """Handler for the /join command"""
    bot = context.bot
    if update.message is not None:
        chat = update.message.chat
        user = update.message.from_user
    else:
        chat = update.effective_message.chat
        user = update.effective_user

    if chat.type == 'private':
        helpers.help_handler(update, context)
        return

    stats.init_stats(user.id, user.first_name)

    try:
        gm.join_game(user, chat)

    except NotEnoughNkap:
        send_async(
            bot, chat.id, text=f"Molah, {mention(user)}, tu n'as pas l'argent.\nCe n'est pas le ndoshi ici.", to_delete=True)

    except LobbyClosedError:
        send_async(bot, chat.id, text="La partie est fermée", to_delete=True)

    except MaxPlayersReached:
        send_async(bot, chat.id, text="Le terre est plein, tu ne peux pas joindre. Utilise /call\_me\_back pour être notifié lorsque une nouvelle partie sera lancée dans ce groupe.", to_delete=True)

    except GameAlreadyStartedError:
        send_async(
            bot, chat.id, text="Impossible de rejoindre une partie en cours, utilise /call\_me\_back pour être notifié lorsque une nouvelle partie sera lancée dans ce groupe.", to_delete=True)

    except NoGameInChatError:
        send_async(
            bot, chat.id, text="Il n'y a aucune partie en cours, crée une nouvelle avec /nkap.", to_delete=True)

    except AlreadyJoinedError:
        send_async(
            bot, chat.id, text=f"{mention(user)}, calme toi, j'ai déjà coupé tes cartes.", to_delete=True)

    else:
        send_async(
            bot, chat.id, text=f'{mention(user)} a réjoint la partie !', to_delete=True)


def start_lamap(update, context):
    """Handler for the /start_lamap command"""
    bot = context.bot

    if update.message is not None:
        chat = update.message.chat
        user = update.message.from_user
    else:
        chat = update.effective_message.chat
        user = update.effective_user

    if chat.type != 'private':

        try:
            game = gm.chatid_games[chat.id][-1]

        except (KeyError, IndexError):
            send_async(
                bot, chat.id, text="Il n'y a aucune partie en cours, crée une nouvelle avec /nkap.")
            return

        if user_is_creator_or_admin(user, game, bot, chat):
            if game.started:
                send_async(
                    bot, chat.id, text=f'{mention(user)}, j\'ai déjà partagé.')

            elif len(game.players) < MIN_PLAYERS:
                send_async(
                    bot, chat.id, text=f'Une partie doit avoir au moins {MIN_PLAYERS} joueurs pour commencer.', to_delete=True)

            else:
                game.start()
                delete_start_msgs(bot, chat.id)

                for player in game.players:
                    stats.user_plays(player.user.id)
                    player.draw_hand()

                choice = [[InlineKeyboardButton(
                    text=f"Tu dégages avec quoi?", switch_inline_query_current_chat='')]]

                game.first_player = random.choice(game.players)
                game.current_player = game.first_player

                # Send the first card and player
                bot.send_message(chat.id, text=f"La partie vient d'être lancée, {mention(game.first_player.user)}, Tu joues la première carte", reply_markup=InlineKeyboardMarkup(
                    choice), timeout=TIMEOUT, parse_mode=ParseMode.MARKDOWN, disable_web_page_preview=True)

        else:
            send_async(
                bot, chat.id, text=f'Toi qui? Seuls le créateur de la partie et les admins peuvent utiliser cette commande.')

    else:
        helpers.help_handler(update, context)


def reply_to_query(update, context):
    """
    Handler for inline queries.
    Builds the result list for inline queries and answers to the client.
    """
    results = list()
    bot = context.bot

    try:
        user = update.inline_query.from_user
        user_id = user.id
        player = gm.userid_current[user_id]
        game = player.game
        players = game.players

    except KeyError:
        add_no_game(results)
    else:
        # the game has not yet started
        if not game.started:
            if user_is_creator(user, game):
                logger.debug(f"{user.id} wants to start a game")
            else:
                add_not_started(results)

        elif user_id == game.current_player.user.id:
            # to help show the cards in the same order each time
            playable = player.playable_cards()
            qw_check = check_quick_win(player.cards)
            if qw_check is not None and len(player.cards) == 5:
                add_special_card(game, qw_check, results, can_play=True)
            for card in sorted(player.cards):
                add_card(game, card, results, can_play=(card in playable))

        elif user_id != game.current_player.user.id or not game.started:
            for card in sorted(player.cards):
                add_card(game, card, results, can_play=False)

    answer_async(bot, update.inline_query.id, results, cache_time=0,
                 switch_pm_parameter='select')


def process_result(update, context):
    """
    Handler for chosen inline results.
    """

    bot = context.bot

    try:
        user = update.chosen_inline_result.from_user
        player = gm.userid_current[user.id]
        game = player.game
        result_id = update.chosen_inline_result.result_id

    except (KeyError, AttributeError, ValueError):
        # handle errors that occurs when players play wrong cards
        return

    do_play_card(bot, player, result_id)


def close_game(update, context):
    ''' Handler for the close command '''
    chat = update.message.chat
    bot = context.bot
    user = update.message.from_user
    games = gm.chatid_games.get(chat.id)

    if not games:
        send_async(
            bot, chat.id, f"Il n'y a aucune partie en cours dans ce groupe. Utilise /nkap  pour lancer")

    game = games[-1]

    if user.id in game.owner:
        game.open = False
        send_async(
            bot, chat.id, f"On a fermé le terre. Tu ne peux plus joindre.")
        return

    else:
        send_async(
            bot, chat.id, f"Tu es qui pour lock le terre? Seul le créateur de la partie {mention(game.starter)} ou l'admin peuvent lock le terre", reply_to_message_id=update.message.message_id)
        return


def quit_game(update, context):
    """Handler for the /leave command"""
    chat = update.message.chat
    user = update.message.from_user
    bot = context.bot
    player = None

    try:
        player = gm.player_for_user_in_chat(user, chat)
    except NoGameInChatError:
        send_async(bot, chat.id, text=f"Il n'y a aucune partie en cours dans groupe, crée une nouvelle avec /nkap.",
                   reply_to_message_id=update.message.message_id)

    game = player.game
    user = update.message.from_user

    try:
        if game.control_player != None:
            if game.control_player.user.id != user.id:
                gm.leave_game(user, chat)
            else:
                send_async(bot, chat.id, text=f"Molah, Tu pars où alors que tu as le contrôle ?",
                           reply_to_message_id=update.message.message_id)
                return

        elif game.current_player.user.id == user.id:
            send_async(bot, chat.id, text=f"{mention(user)} a fui en voyant ses cartes.",
                       reply_to_message_id=update.message.message_id)
            gm.leave_game(user, chat)
            stats.user_quit(user.id)
            stats.user_lost(user.id, "n", game.nkap, game.bet)

        else:
            send_async(bot, chat.id, text=f"{mention(user)} a fui sans voir ses cartes.",
                       reply_to_message_id=update.message.message_id)
            gm.leave_game(user, chat)
            stats.user_quit(user.id)
            stats.user_lost(user.id, "n", game.nkap, game.bet)

    except NoGameInChatError:
        send_async(bot, chat.id, text=f"Il n'y a aucune partie en cours dans groupe, crée une nouvelle avec /nkap.",
                   reply_to_message_id=update.message.message_id)

    except NotEnoughPlayersError:
        gm.end_game(chat, user)
        if game.control_player is None:
            send_async(
                bot, chat.id, text=f"Comment vous partez tous?! Fin de partie !")
        else:
            send_animation_async(
                bot, chat.id, animation="https://media.giphy.com/media/NG6dWJC9wFX2/giphy.gif", caption=f"Je considère que {mention(game.control_player.user)} a gagné")
            logger.debug(
                f"WIN GAME FOFEIT ({game.control_player.user.id}) in {chat.id}")
            stats.user_won(game.control_player.user.id,
                           "n", game.nkap, game.bet)

    else:
        if game.started:
            send_async(bot, chat.id,
                       text=f"{mention(user)} comme tu pars là, ne vient plus. Prochain joueur: {mention(game.current_player.user)}", reply_to_message_id=update.message.message_id)
            try:
                gm.leave_game(user, chat)
                stats.user_quit(user.id)
                stats.user_lost(user.id, "n", game.nkap, game.bet)

            except NotEnoughPlayersError:
                if game.control_player is None:
                    send_async(
                        bot, chat.id, text=f"Comment vous partez tous?! Fin de partie !")
                else:
                    send_animation_async(
                        bot, chat.id, animation="https://media.giphy.com/media/NG6dWJC9wFX2/giphy.gif", caption=f"Les gars ont tous fui?! Je considère que {mention(game.control_player.user)} a gagné")
                gm.end_game(chat, user)
                stats.user_won(game.control_player.user.id,
                               "n", game.nkap, game.bet)
        else:
            send_async(bot, chat.id, text=f"{mention(user)} a fui.",
                       reply_to_message_id=update.message.message_id)
            try:
                gm.leave_game(user, chat)
                stats.user_quit(user.id)
                stats.user_lost(user.id, "n", game.nkap, game.bet)

            except NotEnoughPlayersError:
                if game.control_player is None:
                    send_async(
                        bot, chat.id, text=f"Comment vous partez tous?! Fin de partie !")
                else:
                    send_animation_async(
                        bot, chat.id, animation=win_forfeit_Anim(), caption=f"Les gars ont tous fui?! Je considère que {mention(game.control_player.user)} a gagné")
                stats.user_won(game.control_player.user.id,
                               "n", game.nkap, game.bet)
                gm.end_game(chat, user)


def kill_game(update, context):
    """Handler for the /kill game"""
    chat = update.message.chat
    user = update.message.from_user
    games = gm.chatid_games.get(chat.id)
    bot = context.bot

    if update.message.chat.type == 'private':
        helpers.help_handler(bot, update)
        return

    if not games:
        send_async(
            bot, chat.id, text="Aucune partie lancé ici, crée une nouvelle avec /nkap.")
        return

    game = games[-1]

    if user_is_creator_or_admin(user, game, bot, chat):

        try:
            gm.end_game(chat, user)
            send_async(bot, chat.id, text="J'ai tué le way !")
            delete_start_msgs(bot, chat.id)
            logger.debug("KILLED GAME in chat " +
                         str(chat.id) + "by user" + str(user.id))

        except NoGameInChatError:
            send_async(bot, chat.id,
                       text="Ok. j'éteins le feu.", reply_to_message_id=update.message.message_id)
            delete_start_msgs(bot, chat.id)
            gm.chatid_games[chat.id] = []
            context.job_queue.stop()

    else:
        send_async(
            bot, chat.id, text=f"Tu es qui pour tuer le way? Seul l'organisateur ({mention(game.starter)}) et un admin peuvent tuer le way.", reply_to_message_id=update.message.message_id)


def kick_player(update, context):
    """Handler for the /chasser command"""
    bot = context.bot

    if update.message.chat.type == 'private':
        return

    chat = update.message.chat
    user = update.message.from_user

    try:
        game = gm.chatid_games[chat.id][-1]

    except (KeyError, IndexError):
        send_async(bot, chat.id,
                   text=f"On ne joue pas encore boss.",
                   reply_to_message_id=update.message.message_id, to_delete=True)
        return

    if not game.started:
        send_async(bot, chat.id,
                   text="La partie n'a pas encore débuté.",
                   reply_to_message_id=update.message.message_id)
        return

    if user_is_creator_or_admin(user, game, bot, chat):

        if update.message.reply_to_message:
            kicked = update.message.reply_to_message.from_user
            if game.control_player.user.id == kicked.id:
                send_async(bot, chat.id, text=f"Calme toi, il a le contrôle.",
                           reply_to_message_id=update.message.message_id)
                return

            try:
                gm.leave_game(kicked, chat)

            except NoGameInChatError:
                send_async(bot, chat.id, text=f"Tu veux chasser {kicked.name} alors qu'il ne joue pas?",
                           reply_to_message_id=update.message.message_id)
                return

            except NotEnoughPlayersError:
                gm.end_game(chat, user)
                send_async(bot, chat.id,
                           text=f"Ce n'est pas la salle d'attente ici! {mention(user)} a chassé {mention(kicked)} !")
                stats.user_kicked(kicked.id)
                send_async(
                    bot, chat.id, text=f"Plus assez de joueurs, Fin de partie !")
                return

            send_async(
                bot, chat.id, text=f"C'est pas la salle d'attente ici, {mention(user)} a chassé {mention(kicked)} !")

        else:
            send_async(bot, chat.id,
                       text=f"Réessaies en repondant à un de ses messages.",
                       reply_to_message_id=update.message.message_id)
            return

        send_async(bot, chat.id,
                   text=f"C'est free... Prochain joueur: {mention(game.current_player.user)}.",
                   reply_to_message_id=update.message.message_id)
        stats.user_kicked(kicked.id)

    else:
        send_async(bot, chat.id,
                   text=f"Tu chasse en tant que qui ?",
                   reply_to_message_id=update.message.message_id)


def game_status(update, context):
    chat = update.message.chat
    user = update.message.from_user
    games = gm.chatid_games.get(chat.id)
    bot = context.bot

    if update.message.chat.type == 'private':
        helpers.help_handler(bot, update)
        return

    if not games:
        send_async(
            bot, chat.id, text="Aucune partie n'est lancé ici, crée une nouvelle avec /new\_game.")
        return

    game = games[-1]

    send_async(bot, chat.id, text=get_game_status(game))


def reset_stats(update, context):
    chat = update.message.chat
    user = update.message.from_user
    bot = context.bot

    if update.message.chat.type == 'private':
        stats.reset_all_stats(user.id)
        send_async(
            bot, chat.id, text="C'est bon, j'ai tout oublié ton passé, sauf l'argent que tu avais 😎")
        return

    else:
        send_async(
            bot, chat.id, text="Vient en DM me dire ce que tu essaies de cacher.", reply_to_message_id=update.message.message_id)
        return


def cbhandler(update, context):
    bot = context.bot
    chat = update.effective_message.chat
    query = update.callback_query
    user = update.effective_user

    game = gm.chatid_games[chat.id][-1]

    if (query.data == 'join_game'):
        join_game(update, context)
    elif query.data == 'start_game':
        if user_is_creator_or_admin(user, game, bot, chat):
            start_lamap(update, context)
    elif query.data == 'notify':
        if user_is_creator_or_admin(user, game, bot, chat):
            pin_game_message(context.bot, chat.id)
    elif query.data == 'kill_game':
        if user_is_creator_or_admin(user, game, bot, chat):
            kill_game(update, context)

    query.answer()


def mes(update, context):
    if update.message.chat.type == 'private':
        context.bot.send_message(
            chat_id=update.effective_chat.id, text="Ok free")


def main():

    # Get the dispatcher to register handlers
    dispatcher.add_handler(InlineQueryHandler(reply_to_query))
    dispatcher.add_handler(ChosenInlineResultHandler(process_result))
    dispatcher.add_handler(CommandHandler('close', close_game))
    dispatcher.add_handler(
        ConversationHandler(
            entry_points=[CommandHandler('nkap', initiate_nkap)],
            states={
                1: [MessageHandler(Filters.text & ~Filters.command, new_nkap_game)]
            },
            fallbacks=[CommandHandler('ndem', stop_nkap_game)]
        )
    )
    # dispatcher.add_handler(CommandHandler('se_banquer', quit_game))
    dispatcher.add_handler(CommandHandler('tuer_le_way', kill_game))
    dispatcher.add_handler(CommandHandler('call_me_back', call_me_back))
    dispatcher.add_handler(CommandHandler('start_game', start_lamap))
    dispatcher.add_handler(CommandHandler('game_status', game_status))
    # muted commands
    dispatcher.add_handler(CommandHandler('join', join_game))
    dispatcher.add_handler(CommandHandler('se_banquer', quit_game))
    # dispatcher.add_handler(CommandHandler('chasser', kick_player))
    dispatcher.add_handler(CommandHandler('reset_stats', reset_stats))

    # callback queries handler
    dispatcher.add_handler(CallbackQueryHandler(cbhandler))

    # all handler (use ONLY for debugging!)
    # dispatcher.add_handler(MessageHandler(Filters.all, mes))

    dispatcher.add_error_handler(loggero.error)

    helpers.register()

    # Start the Bot
    start_bot(updater)

    # Run the bot until the user presses Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT
    updater.idle()


if __name__ == '__main__':
    main()
