# === TO'LIQ ISHLAYDIGAN TELEGRAM GAME BOT KODI ===
# O'yinlar: Mines, Aviator, Dice
# Tugmalar: balans, hisob toldirish, pul chiqarish, bonus, referal

from keep_alive import keep_alive
import telebot
from telebot import types
import random
import threading
import time
import datetime

TOKEN = "8161107014:AAH1I0srDbneOppDw4AsE2kEYtNtk7CRjOw"
bot = telebot.TeleBot(TOKEN)

user_balances = {}
addbal_state = {}
user_games = {}
user_mines_states = {}
user_aviator = {}
user_bonus_state = {}
withdraw_sessions = {}
user_states = {}
user_referred_by = {}
ADMIN_ID = 5815294733

cancel_commands = [
    "/start", "/help", "/addbal", "/cancel",
    "❌ Bekor qilish", "🔙 Orqaga",
    "💰 Balance", "💳 Hisob toldirish", "🎲 Play Dice",
    "💣 Play Mines", "🛩 Play Aviator", "💸 Pul chiqarish",
    "🎁 Kunlik bonus", "👥 Referal link"
]

user_referred_by = {}  # Foydalanuvchi qaysi referal orqali kelganini saqlash uchun

@bot.message_handler(commands=['start'])
def start(message):
    user_id = message.from_user.id
    args = message.text.split()

    # Agar foydalanuvchi yangi bo'lsa, balans va referalni tekshiramiz
    if user_id not in user_balances:
        user_balances[user_id] = 3000

        # Agar referal kodi berilgan bo'lsa va bu foydalanuvchi hali referal orqali kelmagan bo'lsa
        if len(args) > 1:
            try:
                ref_id = int(args[1])
                if ref_id != user_id:
                    # Referal ma'lumotini saqlaymiz
                    user_referred_by[user_id] = ref_id
                    # Referalga bonus beramiz
                    user_balances[ref_id] = user_balances.get(ref_id, 0) + 1000
                    bot.send_message(ref_id, f"🎉 Siz yangi foydalanuvchini taklif qilib, 1000 so‘m bonus oldingiz!")
            except:
                pass

    else:
        # Foydalanuvchi avvaldan mavjud bo'lsa, har safar startda referal kodi bo'lsa, bonus beramiz
        if len(args) > 1:
            try:
                ref_id = int(args[1])
                if ref_id != user_id:
                    # Har safar referal kodi bilan start berilganda bonus berish
                    user_balances[ref_id] = user_balances.get(ref_id, 0) + 1000
                    bot.send_message(ref_id, f"🎉 Siz yangi foydalanuvchini taklif qilib, 1000 so‘m bonus oldingiz!")
            except:
                pass

    back_to_main_menu(message)


# === Asosiy menyuga qaytish funksiyasi ===
def back_to_main_menu(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add('💣 Play Mines', '🛩 Play Aviator')
    markup.add('🎲 Play Dice', '💰 Balance')
    markup.add('💸 Pul chiqarish', '💳 Hisob toldirish')
    markup.add('🎁 Kunlik bonus', '👥 Referal link')
    bot.send_message(message.chat.id, "🔙 Asosiy menyu:", reply_markup=markup)


@bot.message_handler(func=lambda m: m.text == "💰 Balance")
def show_balance(message):
    user_id = message.from_user.id
    bal = user_balances.get(user_id, 0)
    bot.send_message(message.chat.id, f"💰 Sizning balansingiz: {bal} so‘m")

    cancel_commands = [
    "/start", "/help", "/addbal",
    "💰 Balance", "💳 Hisob toldirish", "🎲 Play Dice", "💣 Play Mines",
    "🛩 Play Aviator", "💸 Pul chiqarish", "🎁 Kunlik bonus", "👥 Referal link",
    "🔙 Orqaga"
]

@bot.message_handler(commands=['addbal'])
def addbal_start(message):
    if message.from_user.id != ADMIN_ID:
        return
    msg = bot.send_message(message.chat.id, "🆔 Foydalanuvchi ID raqamini kiriting:")
    bot.register_next_step_handler(msg, addbal_get_id)

def addbal_get_id(message):
    if message.text.startswith("/") or message.text in cancel_commands:
        bot.send_message(message.chat.id, "❌ Jarayon bekor qilindi. /addbal ni qayta bosing.")
        addbal_state.pop(message.from_user.id, None)
        return

    try:
        target_id = int(message.text)
        addbal_state[message.from_user.id] = {'target_id': target_id}
        msg = bot.send_message(message.chat.id, "💵 Qo‘shiladigan miqdorni kiriting:")
        bot.register_next_step_handler(msg, addbal_get_amount)
    except Exception:
        msg = bot.send_message(message.chat.id, "❌ Noto‘g‘ri ID. Iltimos, raqam kiriting:")
        bot.register_next_step_handler(msg, addbal_get_id)

def addbal_get_amount(message):
    if message.text.startswith("/") or message.text in cancel_commands:
        bot.send_message(message.chat.id, "❌ Jarayon bekor qilindi. /addbal ni qayta bosing.")
        addbal_state.pop(message.from_user.id, None)
        return

    try:
        amount = int(message.text)
        if amount <= 0:
            raise ValueError()
        admin_id = message.from_user.id
        target_id = addbal_state[admin_id]['target_id']

        user_balances[target_id] = user_balances.get(target_id, 0) + amount

        bot.send_message(admin_id, f"✅ {amount:,} so‘m foydalanuvchi {target_id} ga qo‘shildi.")

        try:
            bot.send_message(target_id, f"✅ Hisobingizga {amount:,} so‘m tushirildi!", parse_mode="HTML")
        except Exception:
            # Foydalanuvchiga xabar yuborishda xato bo‘lsa, xatolikni e'tiborsiz qoldiramiz
            pass

        del addbal_state[admin_id]

    except Exception:
        msg = bot.send_message(message.chat.id, "❌ Noto‘g‘ri miqdor. Qaytadan raqam kiriting:")
        bot.register_next_step_handler(msg, addbal_get_amount)



@bot.message_handler(func=lambda m: m.text == "👥 Referal link")
def referal_link(message):
    uid = message.from_user.id
    username = bot.get_me().username
    link = f"https://t.me/{username}?start={uid}"
    bot.send_message(message.chat.id, f"👥 Referal linkingiz:\n{link}")

@bot.message_handler(func=lambda message: message.text == "💳 Hisob toldirish")
def handle_deposit(message):
    user_id = message.from_user.id

    text = (
        f"🆔 <b>Sizning ID:</b> <code>{user_id}</code>\n\n"
        f"📨 Iltimos, ushbu ID raqamingizni <b>@for_X_bott</b> ga yuboring.\n\n"
        f"💳 Sizga to‘lov uchun karta raqami yuboriladi. \n"
        f"📥 Karta raqamiga to‘lov qilganingizdan so‘ng, to‘lov chekini adminga yuboring.\n\n"
        f"✅ Admin to‘lovni tekshirib, <b>ID raqamingiz asosida</b> balansingizni to‘ldirib beradi."
    )

    bot.send_message(message.chat.id, text, parse_mode="HTML")
    # Botni sozlash, importlar, token va boshqalar

def back_to_main_menu(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add('💣 Play Mines', '🛩 Play Aviator')
    markup.add('🎲 Play Dice', '💰 Balance')
    markup.add('💸 Pul chiqarish', '💳 Hisob toldirish')
    markup.add('🎁 Kunlik bonus', '👥 Referal link')
    bot.send_message(message.chat.id, "🔙 Asosiy menyu:", reply_markup=markup)

# Keyin boshqa handlerlar va funksiyalar
@bot.message_handler(commands=['start'])
def start(message):
    back_to_main_menu(message)

# Yoki boshqa joyda
@bot.message_handler(func=lambda m: m.text == "🔙 Orqaga")
def go_back(message):
    back_to_main_menu(message)


@bot.message_handler(func=lambda m: m.text == "💸 Pul chiqarish")
def withdraw_step1(message):
    msg = bot.send_message(message.chat.id, "💵 Miqdorni kiriting (min 20000 so‘m):")
    bot.register_next_step_handler(msg, withdraw_step2)

def withdraw_step2(message):
    try:
        amount = int(message.text)
        user_id = message.from_user.id
        if amount < 20000:
            bot.send_message(message.chat.id, "❌ Minimal chiqarish miqdori 20000 so‘m.")
            return
        if user_balances.get(user_id, 0) < amount:
            bot.send_message(message.chat.id, "❌ Mablag‘ yetarli emas.")
            return
        withdraw_sessions[user_id] = amount
        msg = bot.send_message(message.chat.id, "💳 Karta yoki to‘lov usulini yozing:")
        bot.register_next_step_handler(msg, withdraw_step3)
    except:
        bot.send_message(message.chat.id, "❌ Noto‘g‘ri miqdor.")

# === SHU YERGA QO‘Y — withdraw_step3 ===
def withdraw_step3(message):
    user_id = message.from_user.id
    amount = withdraw_sessions.get(user_id)
    info = message.text.strip()

    # === Karta yoki to‘lov tizimi tekshiruvlari ===
    valid = False
    digits = ''.join(filter(str.isdigit, info))
    if len(digits) in [16, 19] and (digits.startswith('8600') or digits.startswith('9860') or digits.startswith('9989')):
        valid = True
    elif any(x in info.lower() for x in ['click', 'payme', 'uzcard', 'humo', 'apelsin']):
        valid = True

    if not valid:
        bot.send_message(message.chat.id, "❌ To‘lov usuli noto‘g‘ri kiritildi. Karta raqami (8600...) yoki servis nomini kiriting.")
        return

    user_balances[user_id] -= amount
    text = f"🔔 Yangi pul chiqarish so‘rovi!\n👤 @{message.from_user.username or 'no_username'}\n🆔 ID: {user_id}\n💵 Miqdor: {amount} so‘m\n💳 To‘lov: {info}"
    bot.send_message(ADMIN_ID, text)
    bot.send_message(message.chat.id, "✅ So‘rov yuborildi, kuting.")
    del withdraw_sessions[user_id]


@bot.message_handler(func=lambda m: m.text == "🎁 Kunlik bonus")
def daily_bonus(message):
    user_id = message.from_user.id
    today = datetime.date.today()
    if user_bonus_state.get(user_id) == today:
        bot.send_message(message.chat.id, "🎁 Siz bugun bonus oldingiz.")
        return
    bonus = random.randint(1000, 5000)
    user_balances[user_id] = user_balances.get(user_id, 0) + bonus
    user_bonus_state[user_id] = today
    bot.send_message(message.chat.id, f"🎉 Sizga {bonus} so‘m bonus berildi!")

@bot.message_handler(func=lambda m: m.text == "🎲 Play Dice")
def dice_start(message):
    msg = bot.send_message(message.chat.id, "🎯 Stavka miqdorini kiriting:")
    bot.register_next_step_handler(msg, dice_process)

def dice_process(message):
    if message.text == "🔙 Orqaga":
        return back_to_main_menu(message)
    try:
        user_id = message.from_user.id
        stake = int(message.text)
        if user_balances.get(user_id, 0) < stake:
            bot.send_message(message.chat.id, "❌ Mablag‘ yetarli emas.")
            return
        user_balances[user_id] -= stake
        bot.send_message(message.chat.id, "🎲 Qaytarilmoqda...")
        time.sleep(2)
        dice = random.randint(1, 6)
        if dice <= 2:
            win = 0
        elif dice <= 4:
            win = stake
        else:
            win = stake * 2
        user_balances[user_id] += win
        bot.send_dice(message.chat.id)
        time.sleep(3)
        bot.send_message(
            message.chat.id,
            f"🎲 Natija: {dice}\n"
            f"{'✅ Yutdingiz!' if win > stake else '❌ Yutqazdingiz.'}\n"
            f"💵 Yutuq: {win} so‘m"
        )
    except:
        bot.send_message(message.chat.id, "❌ Noto‘g‘ri stavka.")


# === MINES o'yini funksiyasi ===
@bot.message_handler(func=lambda m: m.text == "💣 Play Mines")
def start_mines(message):
    user_id = message.from_user.id
    if user_id in user_mines_states and user_mines_states[user_id]['active']:
        bot.send_message(message.chat.id, "⏳ Avvalgi o'yiningiz tugamagani uchun yangi boshlay olmaysiz.")
        return

    msg = bot.send_message(message.chat.id, "🎯 Stavka miqdorini kiriting (min 1000 so'm):")
    bot.register_next_step_handler(msg, mines_start_with_stake)

def mines_start_with_stake(message):
    if message.text == "🔙 Orqaga":
        return back_to_main_menu(message)

    user_id = message.from_user.id
    try:
        stake = int(message.text)
    except:
        bot.send_message(message.chat.id, "❌ Iltimos, raqam kiriting.")
        return

    if stake < 1000:
        bot.send_message(message.chat.id, "❌ Minimal stavka 1000 so'm.")
        return

    if user_balances.get(user_id, 0) < stake:
        bot.send_message(message.chat.id, "❌ Mablag‘ yetarli emas.")
        return

    user_balances[user_id] -= stake

    mines = random.sample(range(25), 3)
    user_mines_states[user_id] = {
        'mines': mines,
        'opened': [],
        'active': True,
        'stake': stake,
        'multiplier': 1.0
    }

    send_grid(message.chat.id, user_id)

def send_grid(chat_id, user_id):
    state = user_mines_states[user_id]
    mines = state['mines']
    opened = state['opened']

    markup = types.InlineKeyboardMarkup(row_width=5)
    buttons = []

    for i in range(25):
        if i in opened:
            if i in mines:
                emoji = '💣'
            else:
                emoji = '✅'
            buttons.append(types.InlineKeyboardButton(emoji, callback_data="opened"))
        else:
            buttons.append(types.InlineKeyboardButton('⬜️', callback_data=f"cell_{i}"))

    for i in range(0, 25, 5):
        markup.row(*buttons[i:i+5])

    markup.add(types.InlineKeyboardButton("💰 Cash Out", callback_data="cashout"))

    bot.send_message(chat_id, "💣 Mines o‘yini - Katakni tanlang:", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data.startswith("cell_"))
def handle_cell_click(call):
    user_id = call.from_user.id
    state = user_mines_states.get(user_id)

    if not state or not state['active']:
        bot.answer_callback_query(call.id, "⛔ O'yin yo'q yoki tugagan.")
        return

    index = int(call.data.split("_")[1])

    if index in state['opened']:
        bot.answer_callback_query(call.id, "⚠️ Bu katak ochilgan.")
        return

    state['opened'].append(index)

    if index in state['mines']:
        state['active'] = False
        show_result(call.message.chat.id, user_id, lose=True)
    else:
        state['multiplier'] = 1.0 + 0.5 * len(state['opened'])
        bot.answer_callback_query(call.id, "✅ Ochildi!")
        # Yangilangan gridni yuboramiz
        send_grid(call.message.chat.id, user_id)

@bot.callback_query_handler(func=lambda call: call.data == "cashout")
def handle_cashout(call):
    user_id = call.from_user.id
    state = user_mines_states.get(user_id)

    if not state or not state['active']:
        bot.answer_callback_query(call.id, "⛔ O'yin yo'q yoki tugagan.")
        return

    state['active'] = False

    win = int(state['stake'] * state['multiplier'])
    user_balances[user_id] = user_balances.get(user_id, 0) + win

    show_result(call.message.chat.id, user_id, win=win)

def show_result(chat_id, user_id, lose=False, win=0):
    state = user_mines_states[user_id]
    grid = []

    for i in range(25):
        if i in state['mines']:
            emoji = '💣'
        elif i in state['opened']:
            emoji = '✅'
        else:
            emoji = '⬜️'
        grid.append(emoji)

    rows = [grid[i:i+5] for i in range(0, 25, 5)]
    grid_text = '\n'.join([' '.join(row) for row in rows])

    if lose:
        bot.send_message(chat_id, f"💥 Bomba bosdingiz!\n{grid_text}\n\n❌ Siz {state['stake']} so‘m yo‘qotdingiz.")
    else:
        bot.send_message(chat_id, f"💰 Cash Out!\n{grid_text}\n\n✅ Siz {win} so‘m yutdingiz!")

    del user_mines_states[user_id]
   
    

def send_grid(chat_id, user_id):
    state = user_mines_states[user_id]
    mines = state['mines']
    opened = state['opened']

    markup = types.InlineKeyboardMarkup(row_width=5)
    buttons = []
    for i in range(25):
        if i in opened:
            if i in mines:
                emoji = '💣'
            else:
                emoji = '✅'
            buttons.append(types.InlineKeyboardButton(emoji, callback_data="opened"))
        else:
            buttons.append(types.InlineKeyboardButton('⬜️', callback_data=f"cell_{i}"))
    for i in range(0, 25, 5):
        markup.row(*buttons[i:i+5])
    markup.add(types.InlineKeyboardButton("💰 Cash Out", callback_data="cashout"))

    bot.send_message(chat_id, "💣 Mines o‘yini - Katakni tanlang:", reply_markup=markup)



# === AVIATOR o'yini funksiyasi ===
@bot.message_handler(func=lambda m: m.text == "🛩 Play Aviator")
def play_aviator(message):
    user_id = message.from_user.id
    if user_id in user_aviator:
        bot.send_message(message.chat.id, "⏳ Avvalgi Aviator o‘yini tugamagani uchun kuting.")
        return
    msg = bot.send_message(message.chat.id, "🎯 Stavka miqdorini kiriting (min 1000 so‘m):")
    bot.register_next_step_handler(msg, process_aviator_stake)

def process_aviator_stake(message):
    if message.text == "🔙 Orqaga":
        return back_to_main_menu(message)
    try:
        user_id = message.from_user.id
        stake = int(message.text)
        if stake < 1000:
            bot.send_message(message.chat.id, "❌ Minimal stavka 1000 so‘m.")
            return
        if user_balances.get(user_id, 0) < stake:
            bot.send_message(message.chat.id, "❌ Yetarli balans yo‘q.")
            return
        user_balances[user_id] -= stake
        user_aviator[user_id] = {
            'stake': stake,
            'multiplier': 1.0,
            'chat_id': message.chat.id,
            'message_id': None,
            'stopped': False
        }
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton("🛑 STOP", callback_data="aviator_stop"))
        msg = bot.send_message(message.chat.id, f"🛫 Boshlanmoqda... x1.00", reply_markup=markup)
        user_aviator[user_id]['message_id'] = msg.message_id
        threading.Thread(target=run_aviator_game, args=(user_id,)).start()
    except:
        bot.send_message(message.chat.id, "❌ Xatolik. Raqam kiriting.")


def run_aviator_game(user_id):
    data = user_aviator.get(user_id)
    if not data:
        return
    chat_id = data['chat_id']
    message_id = data['message_id']
    stake = data['stake']
    multiplier = data['multiplier']
    for _ in range(30):
        if user_aviator.get(user_id, {}).get('stopped'):
            win = int(stake * multiplier)
            user_balances[user_id] += win
            bot.edit_message_text(f"🛑 To‘xtatildi: x{multiplier}\n✅ Yutuq: {win} so‘m", chat_id, message_id)
            del user_aviator[user_id]
            return
        time.sleep(1)
        multiplier = round(multiplier + random.uniform(0.15, 0.4), 2)
        chance = random.random()
        if (multiplier <= 1.6 and chance < 0.3) or (1.6 < multiplier <= 2.4 and chance < 0.15) or (multiplier > 2.4 and chance < 0.1):
            bot.edit_message_text(f"💥 Portladi: x{multiplier}\n❌ Siz yutqazdingiz.", chat_id, message_id)
            del user_aviator[user_id]
            return
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton("🛑 STOP", callback_data="aviator_stop"))
        try:
            bot.edit_message_text(f"🛩 Ko‘tarilmoqda... x{multiplier}", chat_id, message_id, reply_markup=markup)
        except:
            pass
        user_aviator[user_id]['multiplier'] = multiplier
@bot.callback_query_handler(func=lambda call: call.data == "aviator_stop")
def aviator_stop(call):
    user_id = call.from_user.id
    if user_id in user_aviator:
        user_aviator[user_id]['stopped'] = True
        bot.answer_callback_query(call.id, "🛑 O'yin to'xtatildi, pulingiz qaytarildi.")


print("Bot ishga tushdi...")
keep_alive()
bot.polling(none_stop=True)
