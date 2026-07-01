# 全部共用常數 — server 和 client 都 import 這個檔案
# 只改一個地方，兩邊就一致

PORT = 5555

# 世界 / 螢幕大小
WORLD_W = 2000
WORLD_H = 2000
SCREEN_W = 1200
SCREEN_H = 800
TICK_HZ = 30

# 玩家
PLAYER_SIZE = 16
MAX_HP = 100
MOVE_SPEED = 260

# 血包成長
HP_SIZE_BONUS = 2          # 每吃一個血包長 2 px
MAX_SIZE_BONUS = 20        # 最多長 20 px

# 子彈
BULLET_SPEED = 500
BULLET_RADIUS = 5
BULLET_DAMAGE = 5
BULLET_LIFETIME = 1.5
SHOOT_COOLDOWN = 0.30
SHOOT_COOLDOWN_RAPID = 0.09

# 道具（HP + 4 種 Buff）
PICKUP_HEAL = 25
PICKUP_RADIUS = 14
PICKUP_MAX = 8
PICKUP_SPAWN_INTERVAL = 3
PICKUP_TYPES = ["hp", "rapid", "speed", "orbit", "homing"]
PICKUP_WEIGHTS = [5, 2, 2, 2, 2]

# Buff 時效與參數
BUFF_DURATION = 8.0
SPEED_BUFF_MULT = 1.7

# 軌道子彈（吃了自帶）
ORBIT_COUNT = 3
ORBIT_RADIUS = 55
ORBIT_ANGULAR_SPEED = 3.0     # rad/s
ORBIT_HIT_DAMAGE = 6
ORBIT_HIT_CD = 0.4            # 同一目標多久可以再被打一次
ORBIT_BULLET_RADIUS = 7

# 追蹤子彈
HOMING_TURN_RATE = 6.0        # rad/s
HOMING_RANGE = 500

# UI
MINIMAP_SIZE = 200
CHAT_DURATION = 5              # 聊天泡泡秒數
CHAT_LOG_MAX = 30
CHAT_LOG_SHOW = 7              # 右下視窗顯示幾則
CHAT_PANEL_W = 340
CHAT_PANEL_H = 220

# 大廳 / 選單可選項
SHAPES = ["circle", "square", "triangle"]
COLORS = [
    ("紅", [220,  50,  50]),
    ("藍", [ 50, 100, 220]),
    ("綠", [ 50, 200,  80]),
    ("黃", [240, 220,  60]),
    ("紫", [180,  80, 220]),
]

# Buff 顯示顏色與圖示字元（畫在道具上）
BUFF_COLORS = {
    "hp":     (100, 220, 100),
    "rapid":  (255, 140,  40),
    "speed":  ( 60, 200, 220),
    "orbit":  (200, 100, 220),
    "homing": (240, 220,  60),
}
BUFF_LABELS = {
    "hp":     "+",
    "rapid":  "R",
    "speed":  "S",
    "orbit":  "O",
    "homing": "H",
}
BUFF_ZH = {
    "rapid":  "快速射擊",
    "speed":  "加速移動",
    "orbit":  "軌道護盾",
    "homing": "追蹤子彈",
}
