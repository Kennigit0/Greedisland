import psycopg2
import os
import threading

local = threading.local()

def get_conn():
    if not hasattr(local, 'conn') or local.conn.closed:
        local.conn = psycopg2.connect(os.environ['DATABASE_URL'])
        local.conn.autocommit = False
    return local.conn

def init_db():
    conn = get_conn()
    cur = conn.cursor()

    cur.execute("""
        CREATE TABLE IF NOT EXISTS gi_players (
            user_id BIGINT PRIMARY KEY,
            username TEXT,
            jenny BIGINT DEFAULT 1000,
            wins INT DEFAULT 0,
            losses INT DEFAULT 0,
            total_cards_collected INT DEFAULT 0,
            protected_until TIMESTAMP,
            last_draw TIMESTAMP,
            created_at TIMESTAMP DEFAULT NOW()
        )
    """)

    # Cards in hand (not in binder, can be stolen/traded)
    cur.execute("""
        CREATE TABLE IF NOT EXISTS gi_hand_cards (
            user_id BIGINT,
            card_id INT,
            quantity INT DEFAULT 1,
            PRIMARY KEY (user_id, card_id)
        )
    """)

    # Cards locked into binder (safe from theft)
    cur.execute("""
        CREATE TABLE IF NOT EXISTS gi_binder (
            user_id BIGINT,
            card_id INT,
            added_at TIMESTAMP DEFAULT NOW(),
            PRIMARY KEY (user_id, card_id)
        )
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS gi_spell_cards (
            user_id BIGINT,
            spell_id TEXT,
            quantity INT DEFAULT 1,
            PRIMARY KEY (user_id, spell_id)
        )
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS gi_quest_progress (
            user_id BIGINT,
            quest_id TEXT,
            progress INT DEFAULT 0,
            date DATE DEFAULT CURRENT_DATE,
            completed BOOLEAN DEFAULT FALSE,
            PRIMARY KEY (user_id, quest_id, date)
        )
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS gi_pvp_challenges (
            id SERIAL PRIMARY KEY,
            challenger_id BIGINT,
            target_id BIGINT,
            challenger_name TEXT,
            target_name TEXT,
            status TEXT DEFAULT 'pending',
            created_at TIMESTAMP DEFAULT NOW()
        )
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS gi_boss_fights (
            id SERIAL PRIMARY KEY,
            chat_id BIGINT,
            boss_id TEXT,
            current_hp INT,
            max_hp INT,
            status TEXT DEFAULT 'active',
            message_id BIGINT,
            started_at TIMESTAMP DEFAULT NOW()
        )
    """)
    # Add message_id column if it doesn't exist (migration)
    cur.execute("""
        ALTER TABLE gi_boss_fights ADD COLUMN IF NOT EXISTS message_id BIGINT
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS gi_boss_participants (
            boss_fight_id INT,
            user_id BIGINT,
            username TEXT,
            damage_dealt INT DEFAULT 0,
            PRIMARY KEY (boss_fight_id, user_id)
        )
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS gi_trade_offers (
            id SERIAL PRIMARY KEY,
            sender_id BIGINT,
            receiver_id BIGINT,
            offer_card_id INT,
            want_card_id INT,
            status TEXT DEFAULT 'pending',
            created_at TIMESTAMP DEFAULT NOW()
        )
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS gi_last_discarded (
            user_id BIGINT PRIMARY KEY,
            card_id INT,
            discarded_at TIMESTAMP DEFAULT NOW()
        )
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS gi_known_chats (
            chat_id BIGINT PRIMARY KEY,
            title TEXT,
            last_seen TIMESTAMP DEFAULT NOW()
        )
    """)

    # Indexes
    cur.execute("CREATE INDEX IF NOT EXISTS idx_gi_hand_user ON gi_hand_cards(user_id)")
    cur.execute("CREATE INDEX IF NOT EXISTS idx_gi_binder_user ON gi_binder(user_id)")
    cur.execute("CREATE INDEX IF NOT EXISTS idx_gi_pvp_status ON gi_pvp_challenges(status)")
    cur.execute("CREATE INDEX IF NOT EXISTS idx_gi_boss_chat ON gi_boss_fights(chat_id, status)")

    conn.commit()
    cur.close()
    print("✅ Greed Island DB initialized!")

# ─── Player helpers ───────────────────────────────────────────────────────────

def register_player(user_id, username):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO gi_players (user_id, username) VALUES (%s, %s)
        ON CONFLICT (user_id) DO UPDATE SET username = EXCLUDED.username
    """, (user_id, username))
    conn.commit()
    cur.close()

def get_player(user_id):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("SELECT * FROM gi_players WHERE user_id = %s", (user_id,))
    row = cur.fetchone()
    cur.close()
    if not row:
        return None
    cols = ["user_id","username","jenny","wins","losses","total_cards_collected",
            "protected_until","last_draw","created_at"]
    return dict(zip(cols, row))

def update_jenny(user_id, amount):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("UPDATE gi_players SET jenny = GREATEST(0, jenny + %s) WHERE user_id = %s RETURNING jenny", (amount, user_id))
    result = cur.fetchone()
    conn.commit()
    cur.close()
    return result[0] if result else 0

def get_jenny(user_id):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("SELECT jenny FROM gi_players WHERE user_id = %s", (user_id,))
    row = cur.fetchone()
    cur.close()
    return row[0] if row else 0

# ─── Card helpers ─────────────────────────────────────────────────────────────

def add_hand_card(user_id, card_id, qty=1):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO gi_hand_cards (user_id, card_id, quantity) VALUES (%s, %s, %s)
        ON CONFLICT (user_id, card_id) DO UPDATE SET quantity = gi_hand_cards.quantity + %s
    """, (user_id, card_id, qty, qty))
    cur.execute("UPDATE gi_players SET total_cards_collected = total_cards_collected + %s WHERE user_id = %s", (qty, user_id))
    conn.commit()
    cur.close()

def remove_hand_card(user_id, card_id, qty=1):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("SELECT quantity FROM gi_hand_cards WHERE user_id = %s AND card_id = %s", (user_id, card_id))
    row = cur.fetchone()
    if not row or row[0] < qty:
        conn.rollback()
        cur.close()
        return False
    if row[0] == qty:
        cur.execute("DELETE FROM gi_hand_cards WHERE user_id = %s AND card_id = %s", (user_id, card_id))
    else:
        cur.execute("UPDATE gi_hand_cards SET quantity = quantity - %s WHERE user_id = %s AND card_id = %s", (qty, user_id, card_id))
    conn.commit()
    cur.close()
    return True

def get_hand_cards(user_id):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("SELECT card_id, quantity FROM gi_hand_cards WHERE user_id = %s ORDER BY card_id", (user_id,))
    rows = cur.fetchall()
    cur.close()
    return rows  # list of (card_id, qty)

def has_hand_card(user_id, card_id):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("SELECT quantity FROM gi_hand_cards WHERE user_id = %s AND card_id = %s", (user_id, card_id))
    row = cur.fetchone()
    cur.close()
    return row[0] if row else 0

def add_binder_card(user_id, card_id):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO gi_binder (user_id, card_id) VALUES (%s, %s)
        ON CONFLICT DO NOTHING
    """, (user_id, card_id))
    conn.commit()
    cur.close()

def get_binder_cards(user_id):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("SELECT card_id FROM gi_binder WHERE user_id = %s ORDER BY card_id", (user_id,))
    rows = cur.fetchall()
    cur.close()
    return [r[0] for r in rows]

def in_binder(user_id, card_id):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("SELECT 1 FROM gi_binder WHERE user_id = %s AND card_id = %s", (user_id, card_id))
    row = cur.fetchone()
    cur.close()
    return bool(row)

def remove_binder_card(user_id, card_id):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("DELETE FROM gi_binder WHERE user_id = %s AND card_id = %s", (user_id, card_id))
    conn.commit()
    cur.close()

def get_binder_count(user_id):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("SELECT COUNT(*) FROM gi_binder WHERE user_id = %s", (user_id,))
    row = cur.fetchone()
    cur.close()
    return row[0] if row else 0

# ─── Spell card helpers ───────────────────────────────────────────────────────

def add_spell(user_id, spell_id, qty=1):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO gi_spell_cards (user_id, spell_id, quantity) VALUES (%s, %s, %s)
        ON CONFLICT (user_id, spell_id) DO UPDATE SET quantity = gi_spell_cards.quantity + %s
    """, (user_id, spell_id, qty, qty))
    conn.commit()
    cur.close()

def remove_spell(user_id, spell_id):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("SELECT quantity FROM gi_spell_cards WHERE user_id = %s AND spell_id = %s", (user_id, spell_id))
    row = cur.fetchone()
    if not row or row[0] < 1:
        conn.rollback()
        cur.close()
        return False
    if row[0] == 1:
        cur.execute("DELETE FROM gi_spell_cards WHERE user_id = %s AND spell_id = %s", (user_id, spell_id))
    else:
        cur.execute("UPDATE gi_spell_cards SET quantity = quantity - 1 WHERE user_id = %s AND spell_id = %s", (user_id, spell_id))
    conn.commit()
    cur.close()
    return True

def get_spells(user_id):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("SELECT spell_id, quantity FROM gi_spell_cards WHERE user_id = %s AND quantity > 0", (user_id,))
    rows = cur.fetchall()
    cur.close()
    return rows

def has_spell(user_id, spell_id):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("SELECT quantity FROM gi_spell_cards WHERE user_id = %s AND spell_id = %s", (user_id, spell_id))
    row = cur.fetchone()
    cur.close()
    return (row[0] if row else 0) > 0

# ─── Quest helpers ────────────────────────────────────────────────────────────

def get_quest_progress(user_id, quest_id):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("""
        SELECT progress, completed FROM gi_quest_progress
        WHERE user_id = %s AND quest_id = %s AND date = CURRENT_DATE
    """, (user_id, quest_id))
    row = cur.fetchone()
    cur.close()
    return row  # (progress, completed) or None

def increment_quest(user_id, quest_type, amount=1):
    from cards_data import DAILY_QUESTS
    conn = get_conn()
    cur = conn.cursor()
    for q in DAILY_QUESTS:
        if q["type"] == quest_type:
            cur.execute("""
                INSERT INTO gi_quest_progress (user_id, quest_id, progress)
                VALUES (%s, %s, %s)
                ON CONFLICT (user_id, quest_id, date) DO UPDATE
                SET progress = LEAST(gi_quest_progress.progress + %s, %s)
                WHERE gi_quest_progress.completed = FALSE
            """, (user_id, q["id"], amount, amount, q["target"]))
    conn.commit()
    cur.close()

def complete_quest(user_id, quest_id):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("""
        UPDATE gi_quest_progress SET completed = TRUE
        WHERE user_id = %s AND quest_id = %s AND date = CURRENT_DATE
    """, (user_id, quest_id))
    conn.commit()
    cur.close()

# ─── PvP helpers ─────────────────────────────────────────────────────────────

def create_pvp_challenge(challenger_id, target_id, c_name, t_name):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO gi_pvp_challenges (challenger_id, target_id, challenger_name, target_name)
        VALUES (%s, %s, %s, %s) RETURNING id
    """, (challenger_id, target_id, c_name, t_name))
    row = cur.fetchone()
    conn.commit()
    cur.close()
    return row[0]

def get_pending_challenge(target_id, challenger_id):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("""
        SELECT id, challenger_id, challenger_name FROM gi_pvp_challenges
        WHERE target_id = %s AND challenger_id = %s AND status = 'pending'
        AND created_at > NOW() - INTERVAL '10 minutes'
        ORDER BY created_at DESC LIMIT 1
    """, (target_id, challenger_id))
    row = cur.fetchone()
    cur.close()
    return row

def close_pvp_challenge(challenge_id, status):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("UPDATE gi_pvp_challenges SET status = %s WHERE id = %s", (status, challenge_id))
    conn.commit()
    cur.close()

def update_pvp_record(winner_id, loser_id):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("UPDATE gi_players SET wins = wins + 1 WHERE user_id = %s", (winner_id,))
    cur.execute("UPDATE gi_players SET losses = losses + 1 WHERE user_id = %s", (loser_id,))
    conn.commit()
    cur.close()

# ─── Boss helpers ─────────────────────────────────────────────────────────────

def get_active_boss(chat_id):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("""
        SELECT id, boss_id, current_hp, max_hp, message_id FROM gi_boss_fights
        WHERE chat_id = %s AND status = 'active'
        ORDER BY started_at DESC LIMIT 1
    """, (chat_id,))
    row = cur.fetchone()
    cur.close()
    return row  # (id, boss_id, current_hp, max_hp, message_id)

def create_boss_fight(chat_id, boss_id, hp, message_id=None):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO gi_boss_fights (chat_id, boss_id, current_hp, max_hp, message_id)
        VALUES (%s, %s, %s, %s, %s) RETURNING id
    """, (chat_id, boss_id, hp, hp, message_id))
    row = cur.fetchone()
    conn.commit()
    cur.close()
    return row[0]

def damage_boss(fight_id, user_id, username, damage):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("UPDATE gi_boss_fights SET current_hp = GREATEST(0, current_hp - %s) WHERE id = %s RETURNING current_hp", (damage, fight_id))
    row = cur.fetchone()
    new_hp = row[0]
    cur.execute("""
        INSERT INTO gi_boss_participants (boss_fight_id, user_id, username, damage_dealt)
        VALUES (%s, %s, %s, %s)
        ON CONFLICT (boss_fight_id, user_id) DO UPDATE SET damage_dealt = gi_boss_participants.damage_dealt + %s
    """, (fight_id, user_id, username, damage, damage))
    if new_hp == 0:
        cur.execute("UPDATE gi_boss_fights SET status = 'defeated' WHERE id = %s", (fight_id,))
    conn.commit()
    cur.close()
    return new_hp

def get_boss_participants(fight_id):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("SELECT user_id, username, damage_dealt FROM gi_boss_participants WHERE boss_fight_id = %s ORDER BY damage_dealt DESC", (fight_id,))
    rows = cur.fetchall()
    cur.close()
    return rows

def update_boss_message_id(fight_id, message_id):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("UPDATE gi_boss_fights SET message_id = %s WHERE id = %s", (message_id, fight_id))
    conn.commit()
    cur.close()

# ─── Leaderboard ─────────────────────────────────────────────────────────────

def get_leaderboard():
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("""
        SELECT p.username, p.jenny, p.wins,
               (SELECT COUNT(*) FROM gi_binder WHERE user_id = p.user_id) as binder_count
        FROM gi_players p
        ORDER BY binder_count DESC, p.jenny DESC
        LIMIT 10
    """)
    rows = cur.fetchall()
    cur.close()
    return rows

# ─── Protection helpers ───────────────────────────────────────────────────────

def is_protected(user_id):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("SELECT protected_until FROM gi_players WHERE user_id = %s", (user_id,))
    row = cur.fetchone()
    cur.close()
    if not row or not row[0]:
        return False
    from datetime import datetime, timezone
    return row[0].replace(tzinfo=timezone.utc) > datetime.now(timezone.utc)

def set_protection(user_id, hours=24):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("""
        UPDATE gi_players SET protected_until = NOW() + INTERVAL '%s hours' WHERE user_id = %s
    """, (hours, user_id))
    conn.commit()
    cur.close()

# ─── Last discarded ───────────────────────────────────────────────────────────

def set_last_discarded(user_id, card_id):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO gi_last_discarded (user_id, card_id) VALUES (%s, %s)
        ON CONFLICT (user_id) DO UPDATE SET card_id = %s, discarded_at = NOW()
    """, (user_id, card_id, card_id))
    conn.commit()
    cur.close()

def get_last_discarded(user_id):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("SELECT card_id FROM gi_last_discarded WHERE user_id = %s", (user_id,))
    row = cur.fetchone()
    cur.close()
    return row[0] if row else None

# ─── Draw cooldown ────────────────────────────────────────────────────────────

def can_draw(user_id):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("SELECT last_draw FROM gi_players WHERE user_id = %s", (user_id,))
    row = cur.fetchone()
    cur.close()
    if not row or not row[0]:
        return True, 0
    from datetime import datetime, timezone, timedelta
    last = row[0].replace(tzinfo=timezone.utc)
    now = datetime.now(timezone.utc)
    diff = (now - last).total_seconds()
    cooldown = 300  # 5 minutes
    if diff >= cooldown:
        return True, 0
    return False, int(cooldown - diff)

def update_last_draw(user_id):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("UPDATE gi_players SET last_draw = NOW() WHERE user_id = %s", (user_id,))
    conn.commit()
    cur.close()

def reset_draw_cooldown(user_id):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("UPDATE gi_players SET last_draw = NULL WHERE user_id = %s", (user_id,))
    conn.commit()
    cur.close()

# ─── Chat tracking (for /broadcast) ───────────────────────────────────────────

def upsert_chat(chat_id, title):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO gi_known_chats (chat_id, title) VALUES (%s, %s)
        ON CONFLICT (chat_id) DO UPDATE SET title = %s, last_seen = NOW()
    """, (chat_id, title, title))
    conn.commit()
    cur.close()

def get_all_chat_ids():
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("SELECT chat_id FROM gi_known_chats")
    rows = cur.fetchall()
    cur.close()
    return [r[0] for r in rows]

# ─── Admin helpers ─────────────────────────────────────────────────────────────

def cancel_boss_fight(fight_id):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("UPDATE gi_boss_fights SET status = 'cancelled' WHERE id = %s", (fight_id,))
    conn.commit()
    cur.close()

def set_jenny_absolute(user_id, amount):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("UPDATE gi_players SET jenny = %s WHERE user_id = %s RETURNING jenny", (amount, user_id))
    row = cur.fetchone()
    conn.commit()
    cur.close()
    return row[0] if row else 0

def clear_protection(user_id):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("UPDATE gi_players SET protected_until = NULL WHERE user_id = %s", (user_id,))
    conn.commit()
    cur.close()

def reset_player(user_id):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("DELETE FROM gi_hand_cards WHERE user_id = %s", (user_id,))
    cur.execute("DELETE FROM gi_binder WHERE user_id = %s", (user_id,))
    cur.execute("DELETE FROM gi_spell_cards WHERE user_id = %s", (user_id,))
    cur.execute("""
        UPDATE gi_players SET jenny = 1000, wins = 0, losses = 0,
        total_cards_collected = 0, protected_until = NULL, last_draw = NULL
        WHERE user_id = %s
    """, (user_id,))
    conn.commit()
    cur.close()

def get_global_stats():
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("SELECT COUNT(*) FROM gi_players")
    total_players = cur.fetchone()[0]
    cur.execute("SELECT COALESCE(SUM(jenny),0) FROM gi_players")
    total_jenny = cur.fetchone()[0]
    cur.execute("SELECT COALESCE(SUM(quantity),0) FROM gi_hand_cards")
    total_hand_cards = cur.fetchone()[0]
    cur.execute("SELECT COUNT(*) FROM gi_binder")
    total_binder_cards = cur.fetchone()[0]
    cur.execute("SELECT COUNT(*) FROM gi_boss_fights WHERE status = 'active'")
    active_bosses = cur.fetchone()[0]
    cur.execute("SELECT COUNT(*) FROM gi_known_chats")
    total_chats = cur.fetchone()[0]
    cur.execute("SELECT COUNT(*) FROM gi_players WHERE (SELECT COUNT(*) FROM gi_binder b WHERE b.user_id = gi_players.user_id) = 100")
    completed_games = cur.fetchone()[0]
    cur.close()
    return {
        "total_players": total_players,
        "total_jenny": total_jenny,
        "total_hand_cards": total_hand_cards,
        "total_binder_cards": total_binder_cards,
        "active_bosses": active_bosses,
        "total_chats": total_chats,
        "completed_games": completed_games,
    }

def find_user_by_username(username):
    """username without leading @"""
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("SELECT user_id FROM gi_players WHERE username ILIKE %s", (f"@{username}",))
    row = cur.fetchone()
    cur.close()
    return row[0] if row else None
