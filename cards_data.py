NUMBERED_CARDS = {}

# Format: (name, emoji, atk, def, spd, ability_name, ability_desc, ability_effect)
# ability_effect: burn, poison, stun, heal, lifesteal, shield, double, counter, dodge, execute

common_cards = [
    # id 1-50
    ("Iron Sword",      "⚔️",  45, 10, 30, "Slash",        "Basic slash attack",                      "none"),
    ("Wooden Shield",   "🛡️",  10, 60, 15, "Block",        "Reduce incoming damage by 20%",           "shield"),
    ("Leather Boots",   "👢",  20, 15, 70, "Quick Step",   "Goes first regardless of speed",          "firstrike"),
    ("Cotton Gloves",   "🧤",  30, 20, 40, "Grip",         "10% chance to disarm opponent",           "disarm"),
    ("Healing Herb",    "🌿",  10, 25, 20, "Regrowth",     "Heal 15% HP each round",                  "heal"),
    ("Fire Arrow",      "🏹",  55, 5,  45, "Ignite",       "Burns enemy for 10 dmg/round for 3 rounds","burn"),
    ("Stone Axe",       "🪓",  50, 20, 20, "Cleave",       "Deals 80% dmg ignoring defense",          "pierce"),
    ("Rope Trap",       "🪢",  15, 30, 25, "Entangle",     "30% chance to stun enemy for 1 round",    "stun"),
    ("Basic Map",       "🗺️",  5,  10, 60, "Scout",        "Reveals enemy card stats before battle",  "reveal"),
    ("Water Flask",     "🧴",  5,  30, 30, "Splash",       "Reduce enemy speed by 20% for 2 rounds",  "slow"),
    ("Lucky Charm",     "🍀",  25, 25, 25, "Fortune",      "20% chance to dodge any attack",          "dodge"),
    ("Smoke Bomb",      "💨",  10, 20, 55, "Blind",        "Enemy misses next attack",                "blind"),
    ("Simple Bow",      "🏹",  40, 10, 50, "Volley",       "Attacks twice at 60% power",              "double"),
    ("Rusty Knife",     "🔪",  35, 10, 45, "Backstab",     "30% chance to deal 2x damage",            "crit"),
    ("Hemp Rope",       "🪢",  20, 25, 20, "Bind",         "Reduces enemy attack by 25%",             "weaken"),
    ("Flint Stone",     "🪨",  30, 30, 15, "Spark",        "10% chance to cause instant burn",        "burn"),
    ("Old Compass",     "🧭",  10, 20, 65, "Navigate",     "Increase own speed by 30% for 2 rounds",  "haste"),
    ("Tin Pot",         "🫕",  15, 50, 10, "Clang",        "Stuns enemy for 1 round on hit",          "stun"),
    ("Reed Whistle",    "🎵",  5,  15, 40, "Melody",       "Confuses enemy — 25% self-damage chance", "confuse"),
    ("Clay Tablet",     "📜",  10, 40, 20, "Ancient Word", "Seals enemy ability for 2 rounds",        "seal"),
    ("Mushroom Spore",  "🍄",  20, 20, 30, "Toxic Cloud",  "Poisons enemy for 8 dmg/round",           "poison"),
    ("Vine Whip",       "🌿",  35, 15, 35, "Lash",         "Ignores 15% of enemy defense",            "pierce"),
    ("Sand Bag",        "💼",  40, 35, 10, "Heavy Hit",    "Reduces enemy speed by 30%",              "slow"),
    ("Echo Stone",      "💎",  25, 25, 35, "Reflect",      "20% chance to reflect damage back",       "counter"),
    ("Night Lamp",      "🪔",  10, 30, 40, "Dazzle",       "Blinds enemy — 35% miss chance",         "blind"),
    ("Pepper Spray",    "💧",  15, 10, 50, "Sting",        "Reduces enemy attack by 20% for 2 rounds","weaken"),
    ("Thorn Net",       "🕸️",  25, 40, 20, "Ensnare",      "Enemy takes 5 dmg every time they attack","thorns"),
    ("Mud Ball",        "🟤",  20, 15, 35, "Sling",        "20% chance to stun",                      "stun"),
    ("Mirror Shard",    "🪞",  15, 35, 30, "Deflect",      "30% chance to reflect attack",            "counter"),
    ("Bone Club",       "🦴",  48, 25, 15, "Smash",        "Reduces enemy defense by 20%",            "break"),
    ("Cricket Cage",    "🦗",  5,  10, 55, "Chirp",        "Distracts enemy — skip their turn 15%",   "stun"),
    ("Fish Hook",       "🪝",  30, 20, 40, "Snag",         "Steals 10% of enemy's max HP",            "lifesteal"),
    ("Hollow Reed",     "🎋",  10, 45, 25, "Fortify",      "Increases own defense by 25% for 3 rounds","shield"),
    ("Bark Scroll",     "📜",  15, 30, 30, "Inscribe",     "Seals one enemy ability permanently",     "seal"),
    ("Pebble Shot",     "⚪",  25, 10, 60, "Rapid Fire",   "Attacks 3 times at 40% power each",       "triple"),
    ("Rag Doll",        "🧸",  5,  55, 10, "Distract",     "25% chance enemy attacks the doll instead","taunt"),
    ("Candle Wax",      "🕯️",  20, 30, 25, "Drip",         "Burns for 5 dmg/round for 4 rounds",      "burn"),
    ("Dried Meat",      "🥩",  5,  20, 20, "Nourish",      "Heals 20% HP at start of battle",         "heal"),
    ("Salt Pouch",      "🧂",  25, 15, 35, "Corrode",      "Reduces enemy defense by 15% each round", "break"),
    ("Empty Bottle",    "🍶",  10, 25, 45, "Shatter",      "10% chance to instantly stun for 2 rounds","stun"),
    ("Cloth Bandage",   "🩹",  5,  30, 20, "First Aid",    "Heal 25% HP when HP falls below 30%",     "heal"),
    ("Worn Boot",       "👟",  20, 15, 60, "Kick",         "15% chance to stun on hit",               "stun"),
    ("Copper Coin",     "🪙",  10, 20, 40, "Lucky Toss",   "25% chance to double all damage this round","crit"),
    ("Dust Cloud",      "💨",  15, 20, 50, "Obscure",      "Reduces enemy accuracy by 30%",           "blind"),
    ("Twig Wand",       "🪄",  30, 10, 45, "Flick",        "15% chance to seal enemy ability",        "seal"),
    ("Rock Hammer",     "🔨",  52, 30, 10, "Pound",        "Ignores 10% of enemy defense",            "pierce"),
    ("Leaf Wrap",       "🍃",  10, 45, 20, "Nature Guard", "Heals 10% HP each round",                 "heal"),
    ("Feather Pen",     "🪶",  10, 15, 65, "Swift Write",  "Goes first always; +10% damage",          "firstrike"),
    ("Ink Pot",         "⚫",  20, 25, 35, "Stain",        "Reduces enemy speed by 25% permanently",  "slow"),
    ("Wooden Bead",     "📿",  15, 35, 30, "Prayer",       "15% chance to fully heal HP",             "heal"),
]

rare_cards = [
    # id 51-75
    ("Silver Sword",    "🗡️",  85, 30, 55, "Silver Strike",  "20% chance to deal 3x critical damage",   "crit"),
    ("Knight Shield",   "🛡️",  20, 110,25, "Iron Wall",      "Absorbs first 50 damage for free",         "shield"),
    ("Nen Gloves",      "🥊",  90, 40, 60, "Nen Punch",      "Deals bonus 30 true damage (ignores def)",  "truedmg"),
    ("Shadow Cloak",    "🧥",  40, 50, 85, "Vanish",         "30% chance to dodge any attack",            "dodge"),
    ("Phoenix Feather", "🔥",  70, 35, 65, "Rebirth",        "Revive once with 30% HP when defeated",     "revive"),
    ("Thunder Arrow",   "⚡",  95, 15, 75, "Thunderbolt",    "Stuns enemy for 1 round on every hit",      "stun"),
    ("Steel Axe",       "🪓",  100,45, 35, "War Cleave",     "Reduces enemy defense by 30% permanently",  "break"),
    ("Hunter Trap",     "🪤",  50, 60, 40, "Snap",           "40% chance to skip enemy turn completely",  "stun"),
    ("Enchanted Map",   "🗺️",  30, 45, 70, "Foresight",      "Predicts enemy attack; reduce it by 40%",   "shield"),
    ("Mana Flask",      "💙",  40, 50, 50, "Mana Burst",     "Doubles own ability power for 2 rounds",    "boost"),
    ("Fortune Crystal", "🔮",  55, 55, 55, "Fate Twist",     "30% chance to reverse enemy ability on them","counter"),
    ("Flash Bomb",      "💥",  75, 20, 70, "Flashbang",      "Blinds enemy for 2 full rounds",            "blind"),
    ("Elven Bow",       "🏹",  88, 20, 80, "Multishot",      "Attacks 3 times at 55% power each",         "triple"),
    ("Assassin Blade",  "🗡️",  105,15, 90, "Death Mark",     "Enemy marked — 50% chance to instakill",    "execute"),
    ("Silk Rope",       "🪢",  45, 65, 50, "Binding Arts",   "Fully seals enemy ability for entire battle","seal"),
    ("Dragon Scale",    "🐉",  60, 120,30, "Scale Armor",    "Reduces all damage taken by 25%",           "shield"),
    ("Magic Compass",   "🧭",  35, 55, 95, "True North",     "Always attacks first; speed unaffected",     "firstrike"),
    ("Alchemy Pot",     "⚗️",  60, 60, 45, "Transmute",      "Converts 20% of damage into healing",        "lifesteal"),
    ("War Horn",        "📯",  70, 70, 60, "Battle Cry",     "Boosts all stats by 15% for 3 rounds",      "boost"),
    ("Ancient Tablet",  "🪨",  45, 80, 35, "Ancient Seal",   "Permanently reduces enemy attack by 35%",   "weaken"),
    ("Poison Mushroom", "🍄",  55, 45, 55, "Spore Burst",    "Poisons enemy for 20 dmg/round for 5 rounds","poison"),
    ("Chain Whip",      "⛓️",  80, 40, 65, "Flail",          "Hits twice; each hit can trigger stun 20%", "double"),
    ("Iron Cage",       "🔒",  30, 90, 30, "Lockdown",       "Traps enemy — they can't use ability",      "seal"),
    ("Echo Gem",        "💎",  65, 65, 60, "Resonance",      "Copies and uses enemy's ability against them","counter"),
    ("Lunar Lamp",      "🌙",  50, 70, 70, "Moonbeam",       "Heals 20% HP at end of each round",         "heal"),
]

epic_cards = [
    # id 76-90
    ("Gold Sword",      "⚔️",  150,60, 80, "Golden Slash",   "50% chance to deal 2.5x damage",           "crit"),
    ("Nen Shield",      "🔵",  40, 180,50, "Nen Barrier",    "Blocks all damage for 1 round; activates when HP < 40%","shield"),
    ("Aura Gauntlets",  "🥊",  170,70, 90, "Aura Crush",     "60 true damage + 40% chance to stun 2 rounds","truedmg"),
    ("Phantom Cloak",   "👻",  80, 100,130,"Phase",          "50% dodge chance; when dodged deal 80 counter dmg","dodge"),
    ("Dragon Egg",      "🥚",  100,100,100,"Hatch",          "Summons baby dragon — extra 80 dmg/round",  "summon"),
    ("Lightning Spear", "⚡",  180,40, 110,"Thunder God",    "Pierces all defense; stuns for 2 rounds",   "pierce"),
    ("Mithril Axe",     "🪓",  165,80, 60, "Mithril Break",  "Destroys enemy defense completely for 3 rounds","break"),
    ("Aura Trap",       "🌀",  90, 120,75, "Aura Snare",     "70% chance to skip enemy turn; deals 60 dmg","stun"),
    ("World Map",       "🌍",  70, 110,120,"Omniscience",    "Reveals and copies the best stat of enemy card","reveal"),
    ("Nen Flask",       "🫧",  110,110,110,"Nen Overload",   "All stats boosted by 40% for 2 rounds",     "boost"),
    ("Fate Crystal",    "🔮",  130,130,80, "Destiny",        "50% chance to completely reverse battle outcome","counter"),
    ("Aura Bomb",       "💣",  200,30, 95, "Aura Explosion", "Deals massive damage but lowers own DEF by 50%","sacrifice"),
    ("Dragon Bow",      "🐉",  160,50, 140,"Dragon Volley",  "Fires 4 shots at 60% power; each can burn",  "triple"),
    ("Shadow Blade",    "🖤",  175,45, 125,"Shadow Kill",    "70% chance to deal 3x damage as shadow strike","crit"),
    ("Nen Chain",       "⛓️",  120,140,85, "Soul Chain",     "Drains 25% of enemy max HP as lifesteal/round","lifesteal"),
]

legendary_cards = [
    # id 91-100
    ("Excalibur",         "⚡",  300,100,150,"Holy Judgment",   "Always crits; ignores ALL defense; stuns 2 rounds","execute"),
    ("Godhand",           "🖐️",  280,200,120,"Divine Smite",    "Deals 250 true dmg + heals 30% HP on hit",  "truedmg"),
    ("Nen Master Robe",   "👘",  150,280,130,"Perfect Nen",     "Nullifies first 3 attacks completely",      "shield"),
    ("Dimensional Cloak", "🌌",  180,180,200,"Void Step",       "80% dodge; counter for 200 dmg on dodge",   "dodge"),
    ("Phoenix Egg",       "🔥",  220,150,160,"Phoenix Rise",    "Revive twice with 50% HP; deal 150 burn dmg","revive"),
    ("Thor Hammer",       "🔨",  350,120,100,"Mjolnir Strike",  "Deals 300 dmg + stuns for 3 rounds on hit", "stun"),
    ("Adamantium Axe",    "💀",  320,160,90, "Death Cleave",    "Ignores ALL defense; 30% instakill chance",  "execute"),
    ("Fate Trap",         "🕸️",  200,200,170,"Destiny Snare",   "90% stun chance; trapped enemy loses 20% HP/round","stun"),
    ("Complete World Map","🌏",  240,240,240,"Omnipotence",     "Copies ALL enemy stats + adds own on top",   "counter"),
    ("Nen Elixir",        "✨",  260,260,180,"God Aura",        "Heals 50% HP; boosts ALL stats by 60%; TRUE dmg","truedmg"),
]

# Build NUMBERED_CARDS with full stats
for i, (name, emoji, atk, dfn, spd, abl_name, abl_desc, abl_effect) in enumerate(common_cards, 1):
    NUMBERED_CARDS[i] = {
        "name": name, "rarity": "Common", "emoji": emoji,
        "atk": atk, "def": dfn, "spd": spd,
        "ability": abl_name, "ability_desc": abl_desc, "ability_effect": abl_effect,
        "power": atk + dfn + spd
    }

for i, (name, emoji, atk, dfn, spd, abl_name, abl_desc, abl_effect) in enumerate(rare_cards, 51):
    NUMBERED_CARDS[i] = {
        "name": name, "rarity": "Rare", "emoji": emoji,
        "atk": atk, "def": dfn, "spd": spd,
        "ability": abl_name, "ability_desc": abl_desc, "ability_effect": abl_effect,
        "power": atk + dfn + spd
    }

for i, (name, emoji, atk, dfn, spd, abl_name, abl_desc, abl_effect) in enumerate(epic_cards, 76):
    NUMBERED_CARDS[i] = {
        "name": name, "rarity": "Epic", "emoji": emoji,
        "atk": atk, "def": dfn, "spd": spd,
        "ability": abl_name, "ability_desc": abl_desc, "ability_effect": abl_effect,
        "power": atk + dfn + spd
    }

for i, (name, emoji, atk, dfn, spd, abl_name, abl_desc, abl_effect) in enumerate(legendary_cards, 91):
    NUMBERED_CARDS[i] = {
        "name": name, "rarity": "Legendary", "emoji": emoji,
        "atk": atk, "def": dfn, "spd": spd,
        "ability": abl_name, "ability_desc": abl_desc, "ability_effect": abl_effect,
        "power": atk + dfn + spd
    }

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
        "atk": 80, "def": 40,
        "card_rewards": [76, 77, 78, 79],
        "description": "A fierce soldier from the Chimera Ant colony!"
    },
    "phantom_troupe": {
        "name": "Phantom Troupe Member", "emoji": "🕷️",
        "max_hp": 10000, "jenny_reward": 2000,
        "atk": 150, "def": 80,
        "card_rewards": [84, 85, 86, 87, 88],
        "description": "A skilled member of the infamous Phantom Troupe!"
    },
    "hisoka": {
        "name": "Hisoka Morow", "emoji": "🃏",
        "max_hp": 18000, "jenny_reward": 5000,
        "atk": 250, "def": 130,
        "card_rewards": [91, 92, 93, 94, 95],
        "description": "The terrifying magician hunter himself! ♦♣♥♠"
    },
    "meruem": {
        "name": "Meruem - King of Ants", "emoji": "👑",
        "max_hp": 50000, "jenny_reward": 15000,
        "atk": 500, "def": 300,
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
