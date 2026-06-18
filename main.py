import telebot
import os
import random
import threading
from telebot import types
from datetime import datetime, timezone

from database import (
    init_db, register_player, get_player, update_jenny, get_jenny,
    add_hand_card, remove_hand_card, get_hand_cards, has_hand_card,
    add_binder_card, get_binder_cards, in_binder, remove_binder_card, get_binder_count,
    add_spell, remove_spell, get_spells, has_spell,
    get_quest_progress, increment_quest, complete_quest,
    create_pvp_challenge, get_pending_challenge, close_pvp_challenge, update_pvp_record,
    get_active_boss, create_boss_fight, damage_boss, get_boss_participants,
    get_leaderboard, is_protected, set_protection,
    set_last_discarded, get_last_discarded, can_draw, update_last_draw
)
from cards_data import NUMBERED_CARDS, RARITY_EMOJI, RARITY_WEIGHTS, SPELL_CARDS, BOSSES, DAILY_QUESTS

BOT_TOKEN = os.environ.get('BOT_TOKEN')
bot = telebot.TeleBot(BOT_TOKEN)

import traceback as _tb
import functools

_original_message_handler = bot.message_handler
def _safe_message_handler(*args, **kwargs):
    deco = _original_message_handler(*args, **kwargs)
    def wrapper(func):
        @functools.wraps(func)
        def safe_func(message, *a, **kw):
            try:
                return func(message, *a, **kw)
            except Exception as e:
                print(f"❌ ERROR in {func.__name__}: {e}")
                _tb.print_exc()
                try:
                    bot.reply_to(message, f"⚠️ Something went wrong: {e}\nTry again or contact admin.")
                except: pass
        return deco(safe_func)
    return wrapper
bot.message_handler = _safe_message_handler

_original_callback_handler = bot.callback_query_handler
def _safe_callback_handler(*args, **kwargs):
    deco = _original_callback_handler(*args, **kwargs)
    def wrapper(func):
        @functools.wraps(func)
        def safe_func(call, *a, **kw):
            try:
                return func(call, *a, **kw)
            except Exception as e:
                print(f"❌ ERROR in callback {func.__name__}: {e}")
                _tb.print_exc()
                try:
                    bot.answer_callback_query(call.id, f"⚠️ Error: {e}"[:200])
                except: pass
        return deco(safe_func)
    return wrapper
bot.callback_query_handler = _safe_callback_handler

# ─── Utilities ────────────────────────────────────────────────────────────────

def uname(user):
    return f"@{user.username}" if user.username else user.first_name

def card_line(card_id):
    c = NUMBERED_CARDS[card_id]
    r = RARITY_EMOJI[c['rarity']]
    return f"{r} #{card_id:03d} {c['emoji']} {c['name']} [{c['rarity']}]"

CARD_IMG_DIR = os.path.join(os.path.dirname(__file__), "assets", "cards")

def card_photo_path(card_id):
    p = os.path.join(CARD_IMG_DIR, f"{card_id:03d}.png")
    return p if os.path.exists(p) else None

def send_card_photo(chat_id, card_id, caption=None, reply_markup=None):
    path = card_photo_path(card_id)
    if path:
        with open(path, 'rb') as f:
            return bot.send_photo(chat_id, f, caption=caption, reply_markup=reply_markup)
    else:
        return bot.send_message(chat_id, caption or card_line(card_id), reply_markup=reply_markup)

def draw_random_card():
    pool = []
    for card_id, card in NUMBERED_CARDS.items():
        pool.extend([card_id] * RARITY_WEIGHTS[card['rarity']])
    return random.choice(pool)

def ensure_registered(func):
    def wrapper(message):
        uid = message.from_user.id
        uname_ = uname(message.from_user)
        register_player(uid, uname_)
        return func(message)
    return wrapper

def check_registered(message):
    p = get_player(message.from_user.id)
    if not p:
        bot.reply_to(message, "❌ You're not registered! Send /start first.")
        return False
    return True

# ─── /start ───────────────────────────────────────────────────────────────────

@bot.message_handler(commands=['start'])
def cmd_start(message):
    uid = message.from_user.id
    name = uname(message.from_user)
    register_player(uid, name)
    p = get_player(uid)
    jenny = p['jenny']

    text = (
        "🎮 Welcome to GREED ISLAND! 🎮\n\n"
        "━━━━━━━━━━━━━━━━━━━━\n"
        "You have been transported into the legendary Nen-based game!\n\n"
        "🎯 Your Mission: Collect all 100 numbered cards and fill your binder to complete the game!\n\n"
        f"💰 Starting Jenny: {jenny:,}\n\n"
        "━━━━━━━━━━━━━━━━━━━━\n"
        "📖 Quick Start:\n"
        "• /drawcard — Draw a random card (5min cooldown)\n"
        "• /binder — View your card binder\n"
        "• /cards — View your hand cards\n"
        "• /spells — View & use spell cards\n"
        "• /shop — Buy spell cards\n"
        "• /challenge @user — PvP battle\n"
        "• /boss — Fight bosses for rare cards\n"
        "• /quest — Daily quests\n"
        "• /help — Full command list\n\n"
        "⚠️ Remember: Cards in your hand can be stolen! Put them in your /binder to keep them safe."
    )
    bot.send_message(message.chat.id, text)

# ─── /help ────────────────────────────────────────────────────────────────────

@bot.message_handler(commands=['help'])
def cmd_help(message):
    text = (
        "📖 GREED ISLAND — Command List\n\n"
        "━━ 🃏 CARDS ━━\n"
        "/drawcard — Draw a random card (5min cooldown)\n"
        "/cards — View your hand cards\n"
        "/cardinfo ID — Full stats and ability of a card\n"
        "/sell ID — Sell a hand card for Jenny\n\n"
        "━━ 📚 BINDER ━━\n"
        "/binder — View your binder progress\n"
        "/addtobinder ID — Lock card into binder safely\n"
        "/removefromBinder ID — Take card back to hand\n\n"
        "━━ SPELLS ━━\n"
        "/spells — View your spell cards\n"
        "/usespell spell — Use a spell card\n"
        "/shop — Buy spell cards with Jenny\n"
        "/buy spell — Buy a specific spell\n\n"
        "━━ BATTLE ━━\n"
        "/challenge — Reply to user + challenge\n"
        "/accept — Reply to challenger + accept\n"
        "/boss — View or summon a boss\n"
        "/summon boss_name — Summon a boss\n"
        "/attack — Attack the active boss\n\n"
        "━━ 📊 STATS ━━\n"
        "/profile — Your full stats\n"
        "/quest — Daily quests\n"
        "/leaderboard — Top players\n"
        "/jenny — Check your Jenny\n\n"
        "━━ ECONOMY ━━\n"
        "/trade your_card want_card — Offer a trade\n"
        "/accept_trade ID — Accept a trade offer\n\n"
        "Bosses: chimera_ant | phantom_troupe | hisoka | meruem"
    )
    bot.send_message(message.chat.id, text)

# ─── /profile ─────────────────────────────────────────────────────────────────

@bot.message_handler(commands=['profile'])
def cmd_profile(message):
    if not check_registered(message): return
    uid = message.from_user.id
    p = get_player(uid)
    binder_count = get_binder_count(uid)
    hand_cards = get_hand_cards(uid)
    hand_count = sum(q for _, q in hand_cards)
    spells = get_spells(uid)
    spell_count = sum(q for _, q in spells)
    pct = (binder_count / 100) * 100

    protected = is_protected(uid)
    shield = "🔒 Protected" if protected else "🔓 Unprotected"

    text = (
        f"👤 {p['username']}\n\n"
        f"💰 Jenny: {p['jenny']:,}\n"
        f"📚 Binder: {binder_count}/100 ({pct:.0f}% complete)\n"
        f"🃏 Hand Cards: {hand_count}\n"
        f"✨ Spell Cards: {spell_count}\n"
        f"⚔️ PvP W/L: {p['wins']}/{p['losses']}\n"
        f"📦 Total Collected: {p['total_cards_collected']}\n"
        f"🛡️ Status: {shield}\n\n"
        f"{'🏆 GAME COMPLETE! You win!' if binder_count == 100 else f'📊 Progress: {binder_count}/100 cards in binder'}"
    )
    bot.send_message(message.chat.id, text)

# ─── /jenny ───────────────────────────────────────────────────────────────────

@bot.message_handler(commands=['jenny'])
def cmd_jenny(message):
    if not check_registered(message): return
    j = get_jenny(message.from_user.id)
    bot.reply_to(message, f"💰 You have {j:,} Jenny")

# ─── /drawcard ────────────────────────────────────────────────────────────────

@bot.message_handler(commands=['drawcard'])
@ensure_registered
def cmd_drawcard(message):
    uid = message.from_user.id
    can, secs = can_draw(uid)
    if not can:
        mins = secs // 60
        s = secs % 60
        bot.reply_to(message, f"⏳ Draw cooldown: {mins}m {s}s remaining.")
        return

    card_id = draw_random_card()
    card = NUMBERED_CARDS[card_id]
    r_emoji = RARITY_EMOJI[card['rarity']]

    add_hand_card(uid, card_id)
    update_last_draw(uid)
    increment_quest(uid, "collect", 1)

    text = (
        f"🎴 Card Drawn!\n\n"
        f"💡 Use /addtobinder {card_id} to lock it in your binder!"
    )

    # Check quest completions
    _check_quest_completion(uid, "collect", message.chat.id)
    send_card_photo(message.chat.id, card_id, caption=text)
    bot.send_message(message.chat.id, text)

# ─── /cards ───────────────────────────────────────────────────────────────────

@bot.message_handler(commands=['cards'])
def cmd_cards(message):
    if not check_registered(message): return
    uid = message.from_user.id
    hand = get_hand_cards(uid)
    if not hand:
        bot.reply_to(message, "🃏 Your hand is empty! Use /drawcard to get cards.")
        return

    lines = ["🃏 Your Hand Cards (can be stolen!)\n"]
    for card_id, qty in hand:
        c = NUMBERED_CARDS[card_id]
        r = RARITY_EMOJI[c['rarity']]
        line = f"{r} #{card_id:03d} {c['emoji']} {c['name']} x{qty}"
        lines.append(line)

    lines.append(f"\n📊 Total: {sum(q for _,q in hand)} cards")
    lines.append("💡 Use /addtobinder <card_id> to lock cards safely")
    bot.send_message(message.chat.id, "\n".join(lines))

# ─── /cardinfo ────────────────────────────────────────────────────────────────

@bot.message_handler(commands=['cardinfo'])
def cmd_cardinfo(message):
    parts = message.text.split()
    if len(parts) < 2 or not parts[1].isdigit():
        bot.reply_to(message, "Usage: /cardinfo <card_id> (1–100)")
        return
    cid = int(parts[1])
    if cid not in NUMBERED_CARDS:
        bot.reply_to(message, "❌ Card ID must be between 1 and 100.")
        return
    c = NUMBERED_CARDS[cid]
    r = RARITY_EMOJI[c['rarity']]
    send_card_photo(message.chat.id, cid, caption=f"{r} Card #{cid:03d} — {c['name']}")

# ─── /binder ─────────────────────────────────────────────────────────────────

@bot.message_handler(commands=['binder'])
def cmd_binder(message):
    if not check_registered(message): return
    uid = message.from_user.id
    binder = get_binder_cards(uid)
    count = len(binder)
    pct = (count / 100) * 100

    if not binder:
        bot.reply_to(message, f"📚 Your binder is empty!\nUse /addtobinder <card_id> to start filling it.\n\n0/100 cards (0%)")
        return

    # Show in pages of 25
    lines = [f"📚 Your Binder — {count}/100 ({pct:.0f}%)\n"]
    for card_id in binder:
        c = NUMBERED_CARDS[card_id]
        r = RARITY_EMOJI[c['rarity']]
        lines.append(f"{r} #{card_id:03d} {c['emoji']} {c['name']}")

    if count == 100:
        lines.append("\n🏆 BINDER COMPLETE! YOU WIN THE GAME! 🏆")
    else:
        missing = 100 - count
        lines.append(f"\n❌ Missing: {missing} cards to complete")

    text = "\n".join(lines)
    # Split if too long
    if len(text) > 4000:
        for i in range(0, len(lines), 30):
            bot.send_message(message.chat.id, "\n".join(lines[i:i+30]))
    else:
        bot.send_message(message.chat.id, text)

# ─── /addtobinder ─────────────────────────────────────────────────────────────

@bot.message_handler(commands=['addtobinder'])
def cmd_addtobinder(message):
    if not check_registered(message): return
    parts = message.text.split()
    if len(parts) < 2 or not parts[1].isdigit():
        bot.reply_to(message, "Usage: /addtobinder <card_id>")
        return
    cid = int(parts[1])
    if cid not in NUMBERED_CARDS:
        bot.reply_to(message, "❌ Invalid card ID (1–100).")
        return
    uid = message.from_user.id
    if in_binder(uid, cid):
        bot.reply_to(message, f"📚 Card #{cid:03d} is already in your binder!")
        return
    if not has_hand_card(uid, cid):
        bot.reply_to(message, f"❌ You don't have Card #{cid:03d} in your hand.")
        return
    remove_hand_card(uid, cid)
    add_binder_card(uid, cid)
    increment_quest(uid, "binder", 1)
    count = get_binder_count(uid)
    c = NUMBERED_CARDS[cid]
    _check_quest_completion(uid, "binder", message.chat.id)
    send_card_photo(message.chat.id, cid, caption=f"📚 {c['name']} added to binder!\n📊 Binder: {count}/100")

# ─── /removefromBinder ────────────────────────────────────────────────────────

@bot.message_handler(commands=['removefromBinder'])
def cmd_remove_binder(message):
    if not check_registered(message): return
    parts = message.text.split()
    if len(parts) < 2 or not parts[1].isdigit():
        bot.reply_to(message, "Usage: /removefromBinder <card_id>")
        return
    cid = int(parts[1])
    uid = message.from_user.id
    if not in_binder(uid, cid):
        bot.reply_to(message, f"❌ Card #{cid:03d} is not in your binder.")
        return
    remove_binder_card(uid, cid)
    add_hand_card(uid, cid)
    c = NUMBERED_CARDS[cid]
    bot.reply_to(message, f"↩️ {c['name']} moved back to your hand.\n⚠️ It can now be stolen!")

# ─── /spells ─────────────────────────────────────────────────────────────────

@bot.message_handler(commands=['spells'])
def cmd_spells(message):
    if not check_registered(message): return
    uid = message.from_user.id
    spells = get_spells(uid)
    if not spells:
        bot.reply_to(message, "✨ You have no spell cards!\nBuy them at /shop or earn from /quest")
        return

    lines = ["✨ Your Spell Cards\n"]
    for spell_id, qty in spells:
        s = SPELL_CARDS[spell_id]
        lines.append(f"{s['emoji']} {s['name']} x{qty}\n   {s['desc']}\n   Use: /usespell {spell_id}\n")
    bot.send_message(message.chat.id, "\n".join(lines))

# ─── /usespell ────────────────────────────────────────────────────────────────

@bot.message_handler(commands=['usespell'])
def cmd_usespell(message):
    if not check_registered(message): return
    parts = message.text.split()
    if len(parts) < 2:
        bot.reply_to(message, "Usage:\n/usespell gain\n/usespell levy @user card_id\n/usespell clone card_id\n/usespell discard @user\n/usespell protect\n/usespell reveal @user\n/usespell transform\n/usespell lottery\n/usespell recover")
        return

    uid = message.from_user.id
    spell_id = parts[1].lower()

    if spell_id not in SPELL_CARDS:
        bot.reply_to(message, f"❌ Unknown spell: {spell_id}")
        return

    if not has_spell(uid, spell_id):
        bot.reply_to(message, f"❌ You don't have a {SPELL_CARDS[spell_id]['name']} spell card.\nBuy at /shop")
        return

    # ── GAIN ──
    if spell_id == "gain":
        card_id = draw_random_card()
        add_hand_card(uid, card_id)
        remove_spell(uid, spell_id)
        increment_quest(uid, "use_spell", 1)
        increment_quest(uid, "collect", 1)
        c = NUMBERED_CARDS[card_id]
        r = RARITY_EMOJI[c['rarity']]
        _check_quest_completion(uid, "use_spell", message.chat.id)
        bot.reply_to(message, f"🎁 Gain cast!\n\nYou received: {r} {c['emoji']} {c['name']} [#{card_id}]")

    # ── PROTECT ──
    elif spell_id == "protect":
        set_protection(uid, 24)
        remove_spell(uid, spell_id)
        increment_quest(uid, "use_spell", 1)
        _check_quest_completion(uid, "use_spell", message.chat.id)
        bot.reply_to(message, "🔒 Protect activated!\nYour hand cards are safe from theft for 24 hours!")

    # ── TRANSFORM ──
    elif spell_id == "transform":
        hand = get_hand_cards(uid)
        commons = [(cid, qty) for cid, qty in hand if NUMBERED_CARDS[cid]['rarity'] == "Common"]
        total_commons = sum(q for _, q in commons)
        if total_commons < 3:
            bot.reply_to(message, f"❌ Need 3 Common cards in hand. You have {total_commons}.")
            return
        # Remove 3 commons
        removed = 0
        for cid, qty in commons:
            while qty > 0 and removed < 3:
                remove_hand_card(uid, cid)
                qty -= 1
                removed += 1
        # Give 1 rare
        rare_ids = [cid for cid, c in NUMBERED_CARDS.items() if c['rarity'] == "Rare"]
        new_card = random.choice(rare_ids)
        add_hand_card(uid, new_card)
        remove_spell(uid, spell_id)
        increment_quest(uid, "use_spell", 1)
        c = NUMBERED_CARDS[new_card]
        _check_quest_completion(uid, "use_spell", message.chat.id)
        bot.reply_to(message, f"✨ Transform cast!\n3 Commons → 🔵 {c['emoji']} {c['name']} [Rare #{new_card}]")

    # ── RECOVER ──
    elif spell_id == "recover":
        last = get_last_discarded(uid)
        if not last:
            bot.reply_to(message, "❌ No discarded card to recover!")
            return
        add_hand_card(uid, last)
        remove_spell(uid, spell_id)
        increment_quest(uid, "use_spell", 1)
        c = NUMBERED_CARDS[last]
        _check_quest_completion(uid, "use_spell", message.chat.id)
        bot.reply_to(message, f"💊 Recover cast!\nRetrieved: {c['emoji']} {c['name']} [#{last}]")

    # ── LOTTERY ──
    elif spell_id == "lottery":
        remove_spell(uid, spell_id)
        increment_quest(uid, "use_spell", 1)
        roll = random.random()
        if roll < 0.10:
            # Jackpot
            epic_ids = [cid for cid, c in NUMBERED_CARDS.items() if c['rarity'] in ["Epic", "Legendary"]]
            card_id = random.choice(epic_ids)
            add_hand_card(uid, card_id)
            c = NUMBERED_CARDS[card_id]
            r = RARITY_EMOJI[c['rarity']]
            msg = f"🎰 LOTTERY JACKPOT! 🎉\n{r} {c['emoji']} {c['name']} landed on you!"
        elif roll < 0.40:
            jenny = random.randint(500, 2000)
            update_jenny(uid, jenny)
            msg = f"🎰 Lottery — Lucky!\nYou won {jenny:,} Jenny! 💰"
        elif roll < 0.65:
            card_id = draw_random_card()
            add_hand_card(uid, card_id)
            c = NUMBERED_CARDS[card_id]
            msg = f"🎰 Lottery — A card!\n{c['emoji']} {c['name']} appeared!"
        elif roll < 0.80:
            msg = "🎰 Lottery — Nothing happened... (fizzle)"
        else:
            # Bad
            hand = get_hand_cards(uid)
            if hand:
                cid, _ = random.choice(hand)
                remove_hand_card(uid, cid)
                set_last_discarded(uid, cid)
                c = NUMBERED_CARDS[cid]
                msg = f"🎰 Lottery — Backfired! 💀\nYou lost {c['emoji']} {c['name']}!"
            else:
                jenny_lost = random.randint(100, 500)
                update_jenny(uid, -jenny_lost)
                msg = f"🎰 Lottery — Backfired! 💀\nYou lost {jenny_lost:,} Jenny!"
        _check_quest_completion(uid, "use_spell", message.chat.id)
        bot.reply_to(message, msg)

    # ── TARGET SPELLS (need @user) ──
    elif spell_id in ["levy", "discard", "reveal", "clone"]:
        # Parse target
        target_user = None
        extra = None

        if message.reply_to_message:
            target_user = message.reply_to_message.from_user
            if len(parts) > 2:
                extra = parts[2]
        elif len(parts) >= 3:
            # Try to find user mention
            mention = parts[2].lstrip('@')
            if len(parts) > 3:
                extra = parts[3]
            bot.reply_to(message, f"💡 Reply to the target player's message to use {spell_id} on them!")
            return

        if not target_user:
            bot.reply_to(message, f"💡 Reply to the target player's message to use {spell_id}!\nExample: Reply to their message, then send /usespell {spell_id}")
            return

        target_id = target_user.id
        if target_id == uid:
            bot.reply_to(message, "❌ You can't target yourself!")
            return

        if not get_player(target_id):
            bot.reply_to(message, "❌ Target player hasn't started the game (/start).")
            return

        t_name = uname(target_user)

        if spell_id == "reveal":
            binder = get_binder_cards(target_id)
            remove_spell(uid, spell_id)
            increment_quest(uid, "use_spell", 1)
            _check_quest_completion(uid, "use_spell", message.chat.id)
            if not binder:
                bot.reply_to(message, f"👁️ Reveal cast on {t_name}!\nTheir binder is empty.")
            else:
                lines = [f"👁️ Reveal — {t_name}'s Binder ({len(binder)}/100)\n"]
                for cid in binder:
                    c = NUMBERED_CARDS[cid]
                    lines.append(f"{RARITY_EMOJI[c['rarity']]} #{cid:03d} {c['name']}")
                bot.send_message(message.chat.id, "\n".join(lines))

        elif spell_id == "discard":
            if is_protected(target_id):
                bot.reply_to(message, f"🔒 {t_name} is protected! Discard failed.")
                return
            t_hand = get_hand_cards(target_id)
            if not t_hand:
                bot.reply_to(message, f"❌ {t_name} has no hand cards to discard!")
                return
            cid, _ = random.choice(t_hand)
            remove_hand_card(target_id, cid)
            set_last_discarded(target_id, cid)
            remove_spell(uid, spell_id)
            increment_quest(uid, "use_spell", 1)
            c = NUMBERED_CARDS[cid]
            _check_quest_completion(uid, "use_spell", message.chat.id)
            bot.reply_to(message, f"🗑️ Discard cast on {t_name}!\nForced them to discard: {c['emoji']} {c['name']}")
            try:
                bot.send_message(target_id, f"🗑️ Discard spell used on you by {uname(message.from_user)}!\nYou lost: {c['emoji']} {c['name']}\nUse /usespell recover to get it back!")
            except: pass

        elif spell_id == "levy":
            if not extra or not extra.isdigit():
                bot.reply_to(message, "Usage: Reply to target, then\n/usespell levy <card_id>")
                return
            cid = int(extra)
            if cid not in NUMBERED_CARDS:
                bot.reply_to(message, "❌ Invalid card ID.")
                return
            if in_binder(target_id, cid):
                bot.reply_to(message, f"🔒 Card #{cid:03d} is in {t_name}'s binder — it's protected!")
                return
            if is_protected(target_id):
                bot.reply_to(message, f"🔒 {t_name} is protected! Levy failed.")
                return
            if not has_hand_card(target_id, cid):
                bot.reply_to(message, f"❌ {t_name} doesn't have Card #{cid:03d} in their hand.")
                return
            remove_hand_card(target_id, cid)
            add_hand_card(uid, cid)
            remove_spell(uid, spell_id)
            increment_quest(uid, "use_spell", 1)
            c = NUMBERED_CARDS[cid]
            _check_quest_completion(uid, "use_spell", message.chat.id)
            bot.reply_to(message, f"🎯 Levy success!\nStole {c['emoji']} {c['name']} from {t_name}!")
            try:
                bot.send_message(target_id, f"🎯 Levy spell! {uname(message.from_user)} stole your {c['name']}!\nUse /protect to prevent future theft.")
            except: pass

        elif spell_id == "clone":
            if not extra or not extra.isdigit():
                bot.reply_to(message, "Usage: /usespell clone <card_id_you_own>")
                return
            cid = int(extra)
            if not has_hand_card(uid, cid) and not in_binder(uid, cid):
                bot.reply_to(message, f"❌ You don't own Card #{cid:03d}.")
                return
            add_hand_card(uid, cid)
            remove_spell(uid, spell_id)
            increment_quest(uid, "use_spell", 1)
            c = NUMBERED_CARDS[cid]
            _check_quest_completion(uid, "use_spell", message.chat.id)
            bot.reply_to(message, f"👥 Clone cast!\nDuplicated: {c['emoji']} {c['name']}\nA copy added to your hand!")

    else:
        bot.reply_to(message, "❌ Unknown spell usage.")


# ─── /sell ────────────────────────────────────────────────────────────────────

SELL_PRICES = {"Common": 100, "Rare": 400, "Epic": 1200, "Legendary": 5000}

@bot.message_handler(commands=['sell'])
def cmd_sell(message):
    if not check_registered(message): return
    parts = message.text.split()
    if len(parts) < 2 or not parts[1].isdigit():
        bot.reply_to(message, (
            "Usage: /sell <card_id>\n\n"
            "Sell prices:\n"
            "⚪ Common — 100 Jenny\n"
            "🔵 Rare — 400 Jenny\n"
            "🟣 Epic — 1,200 Jenny\n"
            "🟡 Legendary — 5,000 Jenny"
        ))
        return
    cid = int(parts[1])
    if cid not in NUMBERED_CARDS:
        bot.reply_to(message, "❌ Invalid card ID (1–100).")
        return
    uid = message.from_user.id
    if not has_hand_card(uid, cid):
        bot.reply_to(message, "❌ That card is not in your hand.\nCards in your binder cannot be sold.")
        return
    c = NUMBERED_CARDS[cid]
    price = SELL_PRICES[c['rarity']]
    remove_hand_card(uid, cid)
    new_jenny = update_jenny(uid, price)
    r = RARITY_EMOJI[c['rarity']]
    bot.reply_to(message, (
        f"💰 Sold {r} {c['emoji']} {c['name']}\n"
        f"+{price:,} Jenny\n"
        f"Balance: {new_jenny:,} Jenny"
    ))

# ─── /shop ────────────────────────────────────────────────────────────────────

@bot.message_handler(commands=['shop'])
def cmd_shop(message):
    lines = ["🛒 Spell Card Shop\n"]
    for spell_id, s in SPELL_CARDS.items():
        cost = s['cost']
        cost_str = f"{cost:,} Jenny" if cost > 0 else "FREE (via transform)"
        lines.append(f"{s['emoji']} {s['name']} — {cost_str}\n   {s['desc']}\n   Buy: /buy {spell_id}\n")
    bot.send_message(message.chat.id, "\n".join(lines))

@bot.message_handler(commands=['buy'])
def cmd_buy(message):
    if not check_registered(message): return
    parts = message.text.split()
    if len(parts) < 2:
        bot.reply_to(message, "Usage: /buy <spell_name>")
        return
    spell_id = parts[1].lower()
    if spell_id not in SPELL_CARDS:
        bot.reply_to(message, f"❌ Unknown spell: {spell_id}")
        return
    s = SPELL_CARDS[spell_id]
    if s['cost'] == 0:
        bot.reply_to(message, f"❌ {s['name']} can't be bought — earn it via /usespell transform")
        return
    uid = message.from_user.id
    jenny = get_jenny(uid)
    if jenny < s['cost']:
        bot.reply_to(message, f"❌ Not enough Jenny!\nNeed: {s['cost']:,} | Have: {jenny:,}")
        return
    update_jenny(uid, -s['cost'])
    add_spell(uid, spell_id)
    bot.reply_to(message, f"✅ Bought {s['emoji']} {s['name']}!\n💰 Jenny left: {jenny - s['cost']:,}")

# ─── /quest ───────────────────────────────────────────────────────────────────

@bot.message_handler(commands=['quest'])
def cmd_quest(message):
    if not check_registered(message): return
    uid = message.from_user.id
    lines = ["📋 Daily Quests\n"]
    for q in DAILY_QUESTS:
        row = get_quest_progress(uid, q['id'])
        progress = row[0] if row else 0
        completed = row[1] if row else False
        status = "✅ DONE" if completed else f"{progress}/{q['target']}"
        reward = f"+{q['jenny']} Jenny & {SPELL_CARDS[q['spell']]['emoji']} {q['spell'].title()} spell"
        lines.append(f"{q['name']} [{status}]\n   {q['desc']}\n   🎁 {reward}\n")
    bot.send_message(message.chat.id, "\n".join(lines))

def _check_quest_completion(uid, quest_type, chat_id):
    for q in DAILY_QUESTS:
        if q['type'] != quest_type:
            continue
        row = get_quest_progress(uid, q['id'])
        if not row:
            return
        progress, completed = row
        if not completed and progress >= q['target']:
            complete_quest(uid, q['id'])
            update_jenny(uid, q['jenny'])
            add_spell(uid, q['spell'])
            s = SPELL_CARDS[q['spell']]
            bot.send_message(chat_id,
                f"🎉 Quest Complete! — {q['name']}\n💰 +{q['jenny']:,} Jenny\n{s['emoji']} +1 {s['name']} spell!",
                )

# ─── /challenge ───────────────────────────────────────────────────────────────

@bot.message_handler(commands=['challenge'])
def cmd_challenge(message):
    if not check_registered(message): return
    if not message.reply_to_message:
        bot.reply_to(message, "💡 Reply to someone's message to challenge them!\nExample: Reply to @player then send /challenge")
        return
    target = message.reply_to_message.from_user
    uid = message.from_user.id
    if target.id == uid:
        bot.reply_to(message, "❌ You can't challenge yourself!")
        return
    if target.is_bot:
        bot.reply_to(message, "❌ Can't challenge bots!")
        return
    if not get_player(target.id):
        bot.reply_to(message, "❌ That player hasn't started the game yet (/start).")
        return

    t_hand = get_hand_cards(target.id)
    if not t_hand:
        bot.reply_to(message, f"❌ {uname(target)} has no hand cards to win!")
        return

    c_name = uname(message.from_user)
    t_name = uname(target)
    cid = create_pvp_challenge(uid, target.id, c_name, t_name)

    text = (
        f"⚔️ PvP Challenge!\n\n"
        f"{c_name} challenges {t_name} to battle!\n\n"
        f"🏆 Winner steals one random hand card from loser!\n\n"
        f"{t_name}: Reply with /accept {c_name.lstrip('@')} to accept!\n"
        f"⏳ Expires in 10 minutes | Challenge ID: #{cid}"
    )
    bot.send_message(message.chat.id, text)

@bot.message_handler(commands=['accept'])
def cmd_accept(message):
    if not check_registered(message): return
    parts = message.text.split()
    if len(parts) < 2:
        bot.reply_to(message, "Usage: /accept @challenger_username")
        return

    uid = message.from_user.id
    # Find challenge where this user is the target
    # We search by username in the DB; get challenger by username
    challenger_name = parts[1].lstrip('@')

    conn_temp = None
    try:
        import database as db
        conn_temp = db.get_conn()
        cur = conn_temp.cursor()
        cur.execute("""
            SELECT id, challenger_id, challenger_name FROM gi_pvp_challenges
            WHERE target_id = %s AND status = 'pending'
            AND created_at > NOW() - INTERVAL '10 minutes'
            ORDER BY created_at DESC LIMIT 1
        """, (uid,))
        row = cur.fetchone()
        cur.close()
    except Exception as e:
        bot.reply_to(message, f"❌ Error: {e}")
        return

    if not row:
        bot.reply_to(message, "❌ No pending challenge found for you.")
        return

    challenge_id, challenger_id, c_name = row

    # Battle!
    uid_power = _pvp_power(uid)
    c_power = _pvp_power(challenger_id)
    roll_uid = uid_power * random.uniform(0.7, 1.3)
    roll_c = c_power * random.uniform(0.7, 1.3)

    if roll_uid >= roll_c:
        winner_id = uid
        loser_id = challenger_id
        winner_name = uname(message.from_user)
        loser_name = c_name
    else:
        winner_id = challenger_id
        loser_id = uid
        winner_name = c_name
        loser_name = uname(message.from_user)

    # Steal a card
    loser_hand = get_hand_cards(loser_id)
    stolen_text = ""
    if loser_hand and not is_protected(loser_id):
        cid, _ = random.choice(loser_hand)
        remove_hand_card(loser_id, cid)
        add_hand_card(winner_id, cid)
        c = NUMBERED_CARDS[cid]
        stolen_text = f"\n🎯 {winner_name} stole {c['emoji']} {c['name']} from {loser_name}!"
    elif is_protected(loser_id):
        stolen_text = f"\n🔒 {loser_name} is protected — no card stolen!"
    else:
        stolen_text = f"\n💨 {loser_name} had no cards to steal!"

    update_pvp_record(winner_id, loser_id)
    close_pvp_challenge(challenge_id, 'done')
    increment_quest(winner_id, "pvp_win", 1)
    _check_quest_completion(winner_id, "pvp_win", message.chat.id)

    jenny_prize = 200
    update_jenny(winner_id, jenny_prize)

    text = (
        f"⚔️ PvP Battle Result!\n\n"
        f"🏆 {winner_name} WINS!\n"
        f"💀 {loser_name} defeated\n\n"
        f"Power: {winner_name} [{int(roll_uid if winner_id == uid else roll_c)}] vs "
        f"{loser_name} [{int(roll_c if winner_id == uid else roll_uid)}]\n"
        f"{stolen_text}\n"
        f"💰 +{jenny_prize} Jenny to winner!"
    )
    bot.send_message(message.chat.id, text)

def _pvp_power(user_id):
    binder = get_binder_count(user_id)
    hand = get_hand_cards(user_id)
    hand_power = sum(NUMBERED_CARDS[cid]['power'] * qty for cid, qty in hand)
    return (binder * 10) + hand_power + random.randint(1, 50)

def _get_best_card(user_id):
    """Get the highest power card from hand or binder"""
    hand = get_hand_cards(user_id)
    binder = get_binder_cards(user_id)
    all_cards = [cid for cid, _ in hand] + binder
    if not all_cards:
        return None
    return max(all_cards, key=lambda cid: NUMBERED_CARDS[cid]['power'])

# ─── BOSS HELPERS ────────────────────────────────────────────────────────────

def boss_hp_bar(hp, max_hp):
    pct = (hp / max_hp) * 100
    filled = int(pct / 10)
    bar = "█" * filled + "░" * (10 - filled)
    return bar, pct

def boss_message_text(b, boss_id, hp, max_hp, fight_id):
    bar, pct = boss_hp_bar(hp, max_hp)
    return (
        f"👹 {b['name']} {b['emoji']}\n"
        f"{b['description']}\n\n"
        f"❤️ HP: {hp:,}/{max_hp:,}\n"
        f"[{bar}] {pct:.1f}%\n\n"
        f"⚔️ ATK: {b['atk']} | 🛡️ DEF: {b['def']}\n\n"
        f"💰 Reward: {b['jenny_reward']:,} Jenny + Epic Cards!\n"
        f"👥 Everyone can join — pick your card and attack!"
    )

def attack_button(fight_id):
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("⚔️ Choose Card & Attack!", callback_data=f"boss_choose_{fight_id}"))
    return markup

def _give_boss_rewards(fight_id, b, chat_id):
    participants = get_boss_participants(fight_id)
    total_dmg = sum(d for _, _, d in participants)
    result = [f"💀 {b['name']} DEFEATED! {b['emoji']}\n\n🏆 Battle Results:\n"]
    rewards = []
    for i, (p_uid, p_name, p_dmg) in enumerate(participants, 1):
        share = (p_dmg / total_dmg) if total_dmg > 0 else 0
        jenny_earn = int(b['jenny_reward'] * share)
        update_jenny(p_uid, jenny_earn)
        reward_card = random.choice(b['card_rewards'])
        add_hand_card(p_uid, reward_card)
        rc = NUMBERED_CARDS[reward_card]
        r = RARITY_EMOJI[rc['rarity']]
        result.append(f"{i}. {p_name} — {p_dmg:,} dmg\n   +{jenny_earn:,} Jenny | {r} {rc['name']}")
        rewards.append((p_name, reward_card, rc))
    bot.send_message(chat_id, "\n".join(result))
    for p_name, reward_card, rc in rewards:
        send_card_photo(chat_id, reward_card, caption=f"🎁 Reward for {p_name}: {rc['name']}!")

# ─── /boss ────────────────────────────────────────────────────────────────────

@bot.message_handler(commands=['boss'])
def cmd_boss(message):
    if not check_registered(message): return
    chat_id = message.chat.id
    active = get_active_boss(chat_id)

    if active:
        fight_id, boss_id, hp, max_hp, msg_id = active
        b = BOSSES[boss_id]
        text = boss_message_text(b, boss_id, hp, max_hp, fight_id)
        bot.send_message(chat_id, text, reply_markup=attack_button(fight_id))
    else:
        markup = types.InlineKeyboardMarkup(row_width=2)
        for bid, b in BOSSES.items():
            markup.add(types.InlineKeyboardButton(
                f"{b['emoji']} {b['name']} (HP:{b['max_hp']:,})",
                callback_data=f"summon_{bid}"
            ))
        bot.send_message(chat_id, "👹 Summon a Boss!\n\nChoose your enemy:", reply_markup=markup)

@bot.message_handler(commands=['summon'])
def cmd_summon(message):
    if not check_registered(message): return
    parts = message.text.split()
    if len(parts) < 2:
        markup = types.InlineKeyboardMarkup(row_width=2)
        for bid, b in BOSSES.items():
            markup.add(types.InlineKeyboardButton(f"{b['emoji']} {b['name']}", callback_data=f"summon_{bid}"))
        bot.reply_to(message, "Choose a boss:", reply_markup=markup)
        return
    boss_id = parts[1].lower().split('@')[0]
    _do_summon(message.chat.id, boss_id, message)

def _do_summon(chat_id, boss_id, message=None):
    if boss_id not in BOSSES:
        if message: bot.reply_to(message, "❌ Unknown boss. Try: chimera_ant, phantom_troupe, hisoka, meruem")
        return
    active = get_active_boss(chat_id)
    if active:
        if message: bot.reply_to(message, "❌ A boss is already active! Defeat it first.")
        return
    b = BOSSES[boss_id]
    fight_id = create_boss_fight(chat_id, boss_id, b['max_hp'])
    text = boss_message_text(b, boss_id, b['max_hp'], b['max_hp'], fight_id)
    sent = bot.send_message(chat_id, "🚨 BOSS APPEARED! 🚨\n\n" + text, reply_markup=attack_button(fight_id))
    from database import update_boss_message_id
    update_boss_message_id(fight_id, sent.message_id)

@bot.message_handler(commands=['attack'])
def cmd_attack_legacy(message):
    """Legacy /attack command — now shows card picker"""
    if not check_registered(message): return
    chat_id = message.chat.id
    active = get_active_boss(chat_id)
    if not active:
        bot.reply_to(message, "❌ No active boss! Use /boss to summon one.")
        return
    fight_id, boss_id, hp, max_hp, msg_id = active
    if hp <= 0:
        bot.reply_to(message, "❌ Boss already defeated!")
        return
    _show_card_picker(message.from_user.id, chat_id, fight_id, message=message)

def _show_card_picker(uid, chat_id, fight_id, message=None, call=None):
    hand = get_hand_cards(uid)

    if not hand:
        txt = "❌ You have no hand cards! Use /drawcard first.\n(Binder cards are locked safely and can't be risked in battle.)"
        if call: bot.answer_callback_query(call.id, txt, show_alert=True)
        elif message: bot.reply_to(message, txt)
        return

    markup = types.InlineKeyboardMarkup(row_width=2)
    # Show top 8 cards by power
    sorted_cards = sorted(hand, key=lambda x: NUMBERED_CARDS[x[0]]['power'], reverse=True)[:8]
    for cid, qty in sorted_cards:
        c = NUMBERED_CARDS[cid]
        r = RARITY_EMOJI[c['rarity']]
        btn_text = f"{r} {c['name']} (ATK:{c['atk']})"
        markup.add(types.InlineKeyboardButton(btn_text, callback_data=f"boss_attack_{fight_id}_{cid}"))
    markup.add(types.InlineKeyboardButton("❌ Cancel", callback_data="cancel_attack"))

    txt = "🃏 Choose your card to attack with:\n⚠️ The boss may counterattack — your card could get hurt!"
    if call:
        bot.edit_message_text(txt, call.message.chat.id, call.message.message_id, reply_markup=markup)
    elif message:
        bot.reply_to(message, txt, reply_markup=markup)

# ─── BOSS CALLBACKS ───────────────────────────────────────────────────────────

@bot.callback_query_handler(func=lambda call: call.data.startswith('summon_'))
def cb_summon(call):
    if not get_player(call.from_user.id):
        bot.answer_callback_query(call.id, "❌ Use /start first!")
        return
    boss_id = call.data.replace('summon_', '')
    bot.answer_callback_query(call.id, f"Summoning {BOSSES.get(boss_id, {}).get('name', '?')}...")
    _do_summon(call.message.chat.id, boss_id)

@bot.callback_query_handler(func=lambda call: call.data.startswith('boss_choose_'))
def cb_boss_choose(call):
    if not get_player(call.from_user.id):
        bot.answer_callback_query(call.id, "❌ Use /start first!")
        return
    fight_id = int(call.data.replace('boss_choose_', ''))
    bot.answer_callback_query(call.id, "Choose your card!")
    _show_card_picker(call.from_user.id, call.message.chat.id, fight_id, call=call)

@bot.callback_query_handler(func=lambda call: call.data.startswith('boss_attack_'))
def cb_boss_attack(call):
    uid = call.from_user.id
    if not get_player(uid):
        bot.answer_callback_query(call.id, "❌ Use /start first!")
        return

    parts = call.data.split('_')
    # boss_attack_{fight_id}_{card_id}
    fight_id = int(parts[2])
    card_id = int(parts[3])
    chat_id = call.message.chat.id

    active = get_active_boss(chat_id)
    if not active:
        bot.answer_callback_query(call.id, "❌ No active boss!")
        return
    a_fight_id, boss_id, hp, max_hp, msg_id = active
    if hp <= 0:
        bot.answer_callback_query(call.id, "❌ Boss already defeated!")
        return

    c = NUMBERED_CARDS[card_id]
    b = BOSSES[boss_id]

    # Calculate damage using card ATK vs boss DEF
    base_dmg = max(10, c['atk'] - (b['def'] // 3) + random.randint(10, 60))
    crit = random.random() < 0.20
    if crit:
        base_dmg = int(base_dmg * 2.2)

    # Apply ability effects
    ability = c['ability_effect']
    bonus_text = ""
    if ability == 'pierce':
        base_dmg = int(c['atk'] * 1.3)
        bonus_text = "\n🗡️ Pierce! Ignored defense!"
    elif ability == 'crit' and random.random() < 0.3:
        base_dmg = int(base_dmg * 2)
        bonus_text = "\n💥 Ability Crit! 2x damage!"
    elif ability == 'truedmg':
        base_dmg = c['atk']
        bonus_text = "\n✨ True Damage! DEF ignored!"
    elif ability == 'double':
        base_dmg = int(base_dmg * 1.8)
        bonus_text = "\n👥 Double Hit!"
    elif ability == 'triple':
        base_dmg = int(base_dmg * 2.2)
        bonus_text = "\n🎯 Triple Strike!"
    elif ability == 'execute' and hp < (max_hp * 0.2) and random.random() < 0.25:
        base_dmg = hp  # instant kill
        bonus_text = "\n💀 EXECUTE! Finishing blow!"

    new_hp = damage_boss(fight_id, uid, uname(call.from_user), base_dmg)
    increment_quest(uid, "boss_dmg", base_dmg)
    _check_quest_completion(uid, "boss_dmg", chat_id)

    crit_text = " 💥 CRITICAL!" if crit else ""
    r = RARITY_EMOJI[c['rarity']]

    if new_hp == 0:
        # Boss defeated — edit final message
        result_text = (
            f"💀 {b['name']} DEFEATED! {b['emoji']}\n\n"
            f"Final blow by {uname(call.from_user)} with {r} {c['name']}!\n"
            f"⚔️ -{base_dmg:,} HP!{bonus_text}"
        )
        try:
            bot.edit_message_text(result_text, chat_id, call.message.message_id)
        except: pass
        _give_boss_rewards(fight_id, b, chat_id)
        return

    # BOSS COUNTERATTACK
    counter_text = ""
    dodge_chance = {"Common": 0.10, "Rare": 0.15, "Epic": 0.20, "Legendary": 0.25}[c['rarity']]
    if c['ability_effect'] == 'dodge':
        dodge_chance += 0.25
    dodged = random.random() < dodge_chance

    if dodged:
        counter_text = f"\n🌀 {c['name']} dodged the boss's counterattack!"
    elif random.random() < 0.75:
        counter_dmg = max(15, b['atk'] - (c['def'] // 2) + random.randint(0, 40))
        if c['ability_effect'] == 'shield':
            counter_dmg = int(counter_dmg * 0.5)

        break_chance = 0.30 if counter_dmg >= c['def'] else 0.0
        card_broke = random.random() < break_chance

        if card_broke:
            remove_hand_card(uid, card_id)
            set_last_discarded(uid, card_id)
            counter_text = (
                f"\n💥 {b['name']} counterattacks!\n"
                f"💔 Your {c['name']} took {counter_dmg} dmg and was destroyed!\n"
                f"💡 Use /usespell recover to try get it back."
            )
        else:
            jenny_loss = min(get_jenny(uid), counter_dmg * 4)
            update_jenny(uid, -jenny_loss)
            counter_text = (
                f"\n💥 {b['name']} counterattacks for {counter_dmg} dmg!\n"
                f"💰 You lost {jenny_loss:,} Jenny in repairs!"
            )

    bar, pct = boss_hp_bar(new_hp, max_hp)
    new_text = (
        f"👹 {b['name']} {b['emoji']}\n"
        f"❤️ HP: {new_hp:,}/{max_hp:,}\n"
        f"[{bar}] {pct:.1f}%\n\n"
        f"⚔️{crit_text} {uname(call.from_user)} dealt -{base_dmg:,} HP!\n"
        f"{r} {c['emoji']} {c['name']} — {c['ability']}{bonus_text}"
        f"{counter_text}\n\n"
        f"💰 Reward: {b['jenny_reward']:,} Jenny + Cards!"
    )
    try:
        bot.edit_message_text(new_text, chat_id, msg_id, reply_markup=attack_button(fight_id))
    except: pass
    bot.answer_callback_query(call.id, f"⚔️ -{base_dmg:,} HP dealt!")

@bot.callback_query_handler(func=lambda call: call.data == 'cancel_attack')
def cb_cancel_attack(call):
    bot.answer_callback_query(call.id, "Cancelled!")
    try:
        bot.delete_message(call.message.chat.id, call.message.message_id)
    except: pass

# ─── /leaderboard ─────────────────────────────────────────────────────────────

@bot.message_handler(commands=['leaderboard'])
def cmd_leaderboard(message):
    rows = get_leaderboard()
    if not rows:
        bot.reply_to(message, "No players yet!")
        return
    medals = ["🥇", "🥈", "🥉"] + ["🏅"] * 7
    lines = ["🏆 Greed Island Leaderboard\n"]
    for i, (username, jenny, wins, binder_count) in enumerate(rows):
        lines.append(f"{medals[i]} {username} — {binder_count}/100 cards | {jenny:,}💰 | {wins}W")
    bot.send_message(message.chat.id, "\n".join(lines))

# ─── /trade ───────────────────────────────────────────────────────────────────

@bot.message_handler(commands=['trade'])
def cmd_trade(message):
    if not check_registered(message): return
    if not message.reply_to_message:
        bot.reply_to(message, "💡 Reply to a player's message, then:\n/trade <your_card_id> <want_card_id>")
        return
    parts = message.text.split()
    if len(parts) < 3:
        bot.reply_to(message, "Usage: /trade <your_card_id> <want_card_id>")
        return
    uid = message.from_user.id
    target = message.reply_to_message.from_user
    if target.id == uid:
        bot.reply_to(message, "❌ Can't trade with yourself!")
        return
    if not get_player(target.id):
        bot.reply_to(message, "❌ Target player hasn't started the game.")
        return

    try:
        offer_id = int(parts[1])
        want_id = int(parts[2])
    except ValueError:
        bot.reply_to(message, "❌ Card IDs must be numbers.")
        return

    if offer_id not in NUMBERED_CARDS or want_id not in NUMBERED_CARDS:
        bot.reply_to(message, "❌ Invalid card IDs (1–100).")
        return
    if not has_hand_card(uid, offer_id):
        bot.reply_to(message, f"❌ You don't have Card #{offer_id} in your hand.")
        return
    if not has_hand_card(target.id, want_id):
        bot.reply_to(message, f"❌ {uname(target)} doesn't have Card #{want_id} in their hand.")
        return

    # Store trade offer
    import database as db
    conn = db.get_conn()
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO gi_trade_offers (sender_id, receiver_id, offer_card_id, want_card_id)
        VALUES (%s, %s, %s, %s) RETURNING id
    """, (uid, target.id, offer_id, want_id))
    trade_id = cur.fetchone()[0]
    conn.commit()
    cur.close()

    offer_c = NUMBERED_CARDS[offer_id]
    want_c = NUMBERED_CARDS[want_id]
    t_name = uname(target)
    s_name = uname(message.from_user)

    text = (
        f"🔄 Trade Offer!\n\n"
        f"{s_name} offers:\n"
        f"{RARITY_EMOJI[offer_c['rarity']]} {offer_c['emoji']} {offer_c['name']} (#{offer_id})\n\n"
        f"In exchange for:\n"
        f"{RARITY_EMOJI[want_c['rarity']]} {want_c['emoji']} {want_c['name']} (#{want_id})\n\n"
        f"{t_name}: /accept_trade {trade_id} to accept\n"
        f"Offer ID: #{trade_id}"
    )
    bot.send_message(message.chat.id, text)

@bot.message_handler(commands=['accept_trade'])
def cmd_accept_trade(message):
    if not check_registered(message): return
    parts = message.text.split()
    if len(parts) < 2 or not parts[1].isdigit():
        bot.reply_to(message, "Usage: /accept_trade <trade_id>")
        return
    trade_id = int(parts[1])
    uid = message.from_user.id

    import database as db
    conn = db.get_conn()
    cur = conn.cursor()
    cur.execute("""
        SELECT sender_id, receiver_id, offer_card_id, want_card_id, status
        FROM gi_trade_offers WHERE id = %s
    """, (trade_id,))
    row = cur.fetchone()
    if not row:
        bot.reply_to(message, "❌ Trade offer not found.")
        cur.close()
        return
    sender_id, receiver_id, offer_id, want_id, status = row
    if receiver_id != uid:
        bot.reply_to(message, "❌ This trade is not for you.")
        cur.close()
        return
    if status != 'pending':
        bot.reply_to(message, "❌ This trade has already been resolved.")
        cur.close()
        return

    # Execute trade
    if not has_hand_card(sender_id, offer_id) or not has_hand_card(uid, want_id):
        bot.reply_to(message, "❌ One or both cards are no longer available for trade.")
        cur.execute("UPDATE gi_trade_offers SET status = 'cancelled' WHERE id = %s", (trade_id,))
        conn.commit()
        cur.close()
        return

    remove_hand_card(sender_id, offer_id)
    add_hand_card(uid, offer_id)
    remove_hand_card(uid, want_id)
    add_hand_card(sender_id, want_id)
    cur.execute("UPDATE gi_trade_offers SET status = 'completed' WHERE id = %s", (trade_id,))
    conn.commit()
    cur.close()

    oc = NUMBERED_CARDS[offer_id]
    wc = NUMBERED_CARDS[want_id]
    bot.send_message(message.chat.id,
        f"✅ Trade Complete!\n\n"
        f"🔄 {oc['emoji']} {oc['name']} ↔️ {wc['emoji']} {wc['name']}\n"
        f"Successfully exchanged!")

# ─── Run ──────────────────────────────────────────────────────────────────────

if __name__ == '__main__':
    init_db()
    print("🎮 Greed Island Bot is running!")
    bot.infinity_polling(timeout=60, long_polling_timeout=30)
