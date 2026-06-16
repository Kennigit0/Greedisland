NUMBERED_CARDS = {}

common_cards = [
    ("Iron Sword", "⚔️"), ("Wooden Shield", "🛡️"), ("Leather Boots", "👢"), ("Cotton Gloves", "🧤"),
    ("Healing Herb", "🌿"), ("Fire Arrow", "🏹"), ("Stone Axe", "🪓"), ("Rope Trap", "🪢"),
    ("Basic Map", "🗺️"), ("Water Flask", "🧴"), ("Lucky Charm", "🍀"), ("Smoke Bomb", "💨"),
    ("Simple Bow", "🏹"), ("Rusty Knife", "🔪"), ("Hemp Rope", "🪢"), ("Flint Stone", "🪨"),
    ("Old Compass", "🧭"), ("Tin Pot", "🫕"), ("Reed Whistle", "🎵"), ("Clay Tablet", "📜"),
    ("Mushroom Spore", "🍄"), ("Vine Whip", "🌿"), ("Sand Bag", "💼"), ("Echo Stone", "💎"),
    ("Night Lamp", "🪔"), ("Pepper Spray", "💧"), ("Thorn Net", "🕸️"), ("Mud Ball", "🟤"),
    ("Mirror Shard", "🪞"), ("Bone Club", "🦴"), ("Cricket Cage", "🦗"), ("Fish Hook", "🪝"),
    ("Hollow Reed", "🎋"), ("Bark Scroll", "📜"), ("Pebble Shot", "⚪"), ("Rag Doll", "🧸"),
    ("Candle Wax", "🕯️"), ("Dried Meat", "🥩"), ("Salt Pouch", "🧂"), ("Empty Bottle", "🍶"),
    ("Cloth Bandage", "🩹"), ("Worn Boot", "👟"), ("Copper Coin", "🪙"), ("Dust Cloud", "💨"),
    ("Twig Wand", "🪄"), ("Rock Hammer", "🔨"), ("Leaf Wrap", "🍃"), ("Feather Pen", "🪶"),
    ("Ink Pot", "⚫"), ("Wooden Bead", "📿"),
]

rare_cards = [
    ("Silver Sword", "🗡️"), ("Knight Shield", "🛡️"), ("Nen Gloves", "🥊"), ("Shadow Cloak", "🧥"),
    ("Phoenix Feather", "🔥"), ("Thunder Arrow", "⚡"), ("Steel Axe", "🪓"), ("Hunter Trap", "🪤"),
    ("Enchanted Map", "🗺️"), ("Mana Flask", "💙"), ("Fortune Crystal", "🔮"), ("Flash Bomb", "💥"),
    ("Elven Bow", "🏹"), ("Assassin Blade", "🗡️"), ("Silk Rope", "🪢"), ("Dragon Scale", "🐉"),
    ("Magic Compass", "🧭"), ("Alchemy Pot", "⚗️"), ("War Horn", "📯"), ("Ancient Tablet", "🪨"),
    ("Poison Mushroom", "🍄"), ("Chain Whip", "⛓️"), ("Iron Cage", "🔒"), ("Echo Gem", "💎"),
    ("Lunar Lamp", "🌙"),
]

epic_cards = [
    ("Gold Sword", "⚔️"), ("Nen Shield", "🔵"), ("Aura Gauntlets", "🥊"), ("Phantom Cloak", "👻"),
    ("Dragon Egg", "🥚"), ("Lightning Spear", "⚡"), ("Mithril Axe", "🪓"), ("Aura Trap", "🌀"),
    ("World Map", "🌍"), ("Nen Flask", "🫧"), ("Fate Crystal", "🔮"), ("Aura Bomb", "💣"),
    ("Dragon Bow", "🐉"), ("Shadow Blade", "🖤"), ("Nen Chain", "⛓️"),
]

legendary_cards = [
    ("Excalibur", "⚡"), ("Godhand", "🖐️"), ("Nen Master Robe", "👘"), ("Dimensional Cloak", "🌌"),
    ("Phoenix Egg", "🔥"), ("Thor Hammer", "🔨"), ("Adamantium Axe", "💀"), ("Fate Trap", "🕸️"),
    ("Complete World Map", "🌏"), ("Nen Elixir", "✨"),
]

for i, (name, emoji) in enumerate(common_cards, 1):
    NUMBERED_CARDS[i] = {"name": name, "rarity": "Common", "emoji": emoji, "power": i}

for i, (name, emoji) in enumerate(rare_cards, 51):
    NUMBERED_CARDS[i] = {"name": name, "rarity": "Rare", "emoji": emoji, "power": i * 2}

for i, (name, emoji) in enumerate(epic_cards, 76):
    NUMBERED_CARDS[i] = {"name": name, "rarity": "Epic", "emoji": emoji, "power": i * 4}

for i, (name, emoji) in enumerate(legendary_cards, 91):
    NUMBERED_CARDS[i] = {"name": name, "rarity": "Legendary", "emoji": emoji, "power": i * 10}

RARITY_EMOJI = {"Common": "⚪", "Rare": "🔵", "Epic": "🟣", "Legendary": "🟡"}
RARITY_WEIGHTS = {"Common": 55, "Rare": 27, "Epic": 13, "Legendary": 5}

SPELL_CARDS = {
    "gain":      {"name": "Gain",      "emoji": "🎁", "desc": "Draw a random card from the game world",         "cost": 300},
    "levy":      {"name": "Levy",      "emoji": "🎯", "desc": "Steal a specific card from a player's hand",     "cost": 700},
    "clone":     {"name": "Clone",     "emoji": "👥", "desc": "Duplicate one card you currently hold",          "cost": 900},
    "discard":   {"name": "Discard",   "emoji": "🗑️", "desc": "Force a player to lose a random hand card",     "cost": 600},
    "protect":   {"name": "Protect",   "emoji": "🔒", "desc": "Shield your hand cards from theft for 24h",     "cost": 450},
    "reveal":    {"name": "Reveal",    "emoji": "👁️", "desc": "See a player's full binder contents",           "cost": 350},
    "transform": {"name": "Transform", "emoji": "✨", "desc": "Convert 3 Common cards into 1 Rare card",        "cost": 0},
    "lottery":   {"name": "Lottery",   "emoji": "🎰", "desc": "Random wild effect — good or catastrophic!",    "cost": 150},
    "recover":   {"name": "Recover",   "emoji": "💊", "desc": "Retrieve your last discarded card",             "cost": 500},
    "scan":      {"name": "Scan",      "emoji": "🔍", "desc": "See how many of a specific card exist in game", "cost": 200},
}

BOSSES = {
    "chimera_ant": {
        "name": "Chimera Ant Soldier", "emoji": "🐜",
        "max_hp": 5000, "jenny_reward": 1000,
        "card_rewards": [76, 77, 78, 79],
        "description": "A fierce soldier from the Chimera Ant colony!"
    },
    "phantom_troupe": {
        "name": "Phantom Troupe Member", "emoji": "🕷️",
        "max_hp": 10000, "jenny_reward": 2000,
        "card_rewards": [84, 85, 86, 87, 88],
        "description": "A skilled member of the infamous Phantom Troupe!"
    },
    "hisoka": {
        "name": "Hisoka Morow", "emoji": "🃏",
        "max_hp": 18000, "jenny_reward": 5000,
        "card_rewards": [91, 92, 93, 94, 95],
        "description": "The terrifying magician hunter himself! ♦♣♥♠"
    },
    "meruem": {
        "name": "Meruem - King of Ants", "emoji": "👑",
        "max_hp": 50000, "jenny_reward": 15000,
        "card_rewards": [96, 97, 98, 99, 100],
        "description": "The ultimate being. Only the strongest may survive!"
    }
}

DAILY_QUESTS = [
    {"id": "collect3",   "name": "Card Hunter",    "desc": "Collect 3 cards via /drawcard",  "type": "collect",  "target": 3,   "jenny": 400,  "spell": "gain"},
    {"id": "win2pvp",    "name": "PvP Champion",   "desc": "Win 2 PvP battles",               "type": "pvp_win",  "target": 2,   "jenny": 600,  "spell": "levy"},
    {"id": "boss100",    "name": "Boss Slayer",     "desc": "Deal 200+ dmg to any boss",       "type": "boss_dmg", "target": 200, "jenny": 800,  "spell": "clone"},
    {"id": "spells2",    "name": "Spell Caster",    "desc": "Use 2 spell cards",               "type": "use_spell","target": 2,   "jenny": 450,  "spell": "protect"},
    {"id": "binder5",    "name": "Archivist",       "desc": "Add 5 cards to your binder",      "type": "binder",   "target": 5,   "jenny": 500,  "spell": "reveal"},
]
