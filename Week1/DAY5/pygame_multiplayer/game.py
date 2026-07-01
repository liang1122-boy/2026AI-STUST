# 遊戲主畫面：WASD 移動、左鍵射擊、Enter 打字、F11 全螢幕、右下角聊天視窗

import pygame
import threading
import json
import time
import math

from constants import (
    WORLD_W, WORLD_H, SCREEN_W, SCREEN_H, MINIMAP_SIZE,
    MAX_HP, MOVE_SPEED, PLAYER_SIZE, CHAT_DURATION,
    BULLET_RADIUS, PICKUP_RADIUS,
    SPEED_BUFF_MULT, ORBIT_BULLET_RADIUS,
    CHAT_LOG_SHOW, CHAT_PANEL_W, CHAT_PANEL_H,
    BUFF_COLORS, BUFF_LABELS, BUFF_ZH,
)


def run_game(sock, config):
    screen = pygame.display.get_surface()
    if screen is None:
        screen = pygame.display.set_mode((SCREEN_W, SCREEN_H), pygame.SCALED)
    pygame.display.set_caption(f"多人射擊 - {config['id']}   (F11 全螢幕)")

    try:
        font = pygame.font.SysFont("Microsoft JhengHei", 15)
        small = pygame.font.SysFont("Microsoft JhengHei", 13)
        big  = pygame.font.SysFont("Microsoft JhengHei", 32, bold=True)
        huge = pygame.font.SysFont("Microsoft JhengHei", 64, bold=True)
    except Exception:
        font = pygame.font.Font(None, 18)
        small = pygame.font.Font(None, 16)
        big  = pygame.font.Font(None, 40)
        huge = pygame.font.Font(None, 72)

    clock = pygame.time.Clock()
    pygame.key.stop_text_input()
    pygame.mouse.set_visible(True)

    # ====== 狀態 ======
    my_id = config["id"]
    my_x, my_y = WORLD_W / 2, WORLD_H / 2

    latest = {"players": [], "bullets": [], "pickups": [], "orbits": [], "chat_log": []}
    state_lock = threading.Lock()
    running = True

    chat_active = False
    chat_text   = ""

    # ====== 網路 ======
    def send(m):
        try:
            sock.sendall((json.dumps(m) + "\n").encode("utf-8"))
        except OSError:
            pass

    def recv_loop():
        buf = b""
        while running:
            try:
                data = sock.recv(16384)
            except OSError:
                return
            if not data:
                return
            buf += data
            while b"\n" in buf:
                line, buf = buf.split(b"\n", 1)
                try:
                    msg = json.loads(line.decode("utf-8"))
                except (json.JSONDecodeError, UnicodeDecodeError):
                    continue
                if msg.get("type") == "state":
                    with state_lock:
                        latest["players"]  = msg.get("players", [])
                        latest["bullets"]  = msg.get("bullets", [])
                        latest["pickups"]  = msg.get("pickups", [])
                        latest["orbits"]   = msg.get("orbits", [])
                        latest["chat_log"] = msg.get("chat_log", [])

    threading.Thread(target=recv_loop, daemon=True).start()

    # ====== 繪圖小工具 ======
    def draw_shape(surf, shape, col, sx, sy, size):
        col = tuple(col)
        if shape == "circle":
            pygame.draw.circle(surf, col, (sx, sy), size)
            pygame.draw.circle(surf, (0, 0, 0), (sx, sy), size, 2)
        elif shape == "square":
            r = pygame.Rect(sx - size, sy - size, size * 2, size * 2)
            pygame.draw.rect(surf, col, r)
            pygame.draw.rect(surf, (0, 0, 0), r, 2)
        elif shape == "triangle":
            pts = [(sx, sy - size), (sx - size, sy + size), (sx + size, sy + size)]
            pygame.draw.polygon(surf, col, pts)
            pygame.draw.polygon(surf, (0, 0, 0), pts, 2)

    def draw_hp_bar(surf, sx, sy, hp, size):
        w, h = max(40, size * 2 + 8), 5
        x = sx - w // 2
        y = sy - size - 12
        pygame.draw.rect(surf, (60, 0, 0), (x, y, w, h))
        pygame.draw.rect(surf, (60, 200, 60), (x, y, int(w * hp / MAX_HP), h))
        pygame.draw.rect(surf, (0, 0, 0), (x, y, w, h), 1)

    def draw_bubble(surf, sx, sy, text, size):
        if not text:
            return
        t = font.render(text, True, (0, 0, 0))
        w, h = t.get_size()
        pad = 6
        b = pygame.Rect(sx - w // 2 - pad, sy - size - 30 - h - pad,
                        w + pad * 2, h + pad * 2)
        pygame.draw.rect(surf, (255, 255, 255), b, border_radius=8)
        pygame.draw.rect(surf, (0, 0, 0), b, 2, border_radius=8)
        tip = [(sx - 5, b.bottom), (sx + 5, b.bottom), (sx, b.bottom + 6)]
        pygame.draw.polygon(surf, (255, 255, 255), tip)
        pygame.draw.line(surf, (0, 0, 0), tip[0], tip[2], 2)
        pygame.draw.line(surf, (0, 0, 0), tip[1], tip[2], 2)
        surf.blit(t, (b.x + pad, b.y + pad))

    def draw_pickup(surf, sx, sy, ptype):
        col = BUFF_COLORS.get(ptype, (200, 200, 200))
        pygame.draw.circle(surf, col, (sx, sy), PICKUP_RADIUS)
        pygame.draw.circle(surf, (0, 0, 0), (sx, sy), PICKUP_RADIUS, 2)
        if ptype == "hp":
            pygame.draw.rect(surf, (255, 255, 255), (sx - 2, sy - 7, 4, 14))
            pygame.draw.rect(surf, (255, 255, 255), (sx - 7, sy - 2, 14, 4))
        else:
            label = BUFF_LABELS.get(ptype, "?")
            t = font.render(label, True, (0, 0, 0))
            surf.blit(t, (sx - t.get_width() // 2, sy - t.get_height() // 2))

    def find_me(snap):
        for p in snap:
            if p["id"] == my_id:
                return p
        return None

    # ====== 主迴圈 ======
    try:
        while running:
            dt = clock.tick(60) / 1000
            now = time.time()

            with state_lock:
                players_snap = list(latest["players"])
                bullets_snap = list(latest["bullets"])
                pickups_snap = list(latest["pickups"])
                orbits_snap  = list(latest["orbits"])
                chat_log     = list(latest["chat_log"])

            me = find_me(players_snap)
            alive = (me is None) or me.get("alive", True)
            my_buffs = me.get("buffs", {}) if me else {}
            my_size = PLAYER_SIZE + (me.get("size_bonus", 0) if me else 0)
            speed_now = MOVE_SPEED * (SPEED_BUFF_MULT if my_buffs.get("speed", 0) > 0 else 1.0)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False

                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_F11:
                        pygame.display.toggle_fullscreen()

                    elif chat_active:
                        if event.key == pygame.K_RETURN:
                            if chat_text.strip():
                                send({"type": "chat", "text": chat_text.strip()})
                            chat_text = ""
                            chat_active = False
                            pygame.key.stop_text_input()
                        elif event.key == pygame.K_BACKSPACE:
                            chat_text = chat_text[:-1]
                        elif event.key == pygame.K_ESCAPE:
                            chat_text = ""
                            chat_active = False
                            pygame.key.stop_text_input()
                    else:
                        if event.key == pygame.K_RETURN:
                            if alive:
                                chat_active = True
                                pygame.key.start_text_input()
                            else:
                                send({"type": "respawn"})

                elif event.type == pygame.TEXTINPUT and chat_active:
                    chat_text += event.text

                elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    if alive and not chat_active:
                        mx, my = event.pos
                        dx = mx - SCREEN_W / 2
                        dy = my - SCREEN_H / 2
                        if dx * dx + dy * dy > 4:
                            send({"type": "shoot", "dx": dx, "dy": dy})

            # 移動
            if alive and not chat_active:
                keys = pygame.key.get_pressed()
                if keys[pygame.K_w]: my_y -= speed_now * dt
                if keys[pygame.K_s]: my_y += speed_now * dt
                if keys[pygame.K_a]: my_x -= speed_now * dt
                if keys[pygame.K_d]: my_x += speed_now * dt
                my_x = max(0, min(WORLD_W, my_x))
                my_y = max(0, min(WORLD_H, my_y))
                send({"type": "update", "x": my_x, "y": my_y})
            elif me:
                # 死亡（或重生後）跟隨 server 座標，避免視角錯位
                my_x = me.get("x", my_x)
                my_y = me.get("y", my_y)

            cam_x = my_x - SCREEN_W / 2
            cam_y = my_y - SCREEN_H / 2

            screen.fill((240, 240, 220))

            # 地圖格線
            grid = 100
            gx0 = int(-cam_x % grid)
            gy0 = int(-cam_y % grid)
            for x in range(gx0, SCREEN_W, grid):
                pygame.draw.line(screen, (210, 210, 190), (x, 0), (x, SCREEN_H))
            for y in range(gy0, SCREEN_H, grid):
                pygame.draw.line(screen, (210, 210, 190), (0, y), (SCREEN_W, y))

            # 世界邊界
            pygame.draw.rect(screen, (150, 150, 150),
                             pygame.Rect(-cam_x, -cam_y, WORLD_W, WORLD_H), 3)

            # 道具
            for pk in pickups_snap:
                sx = int(pk["x"] - cam_x); sy = int(pk["y"] - cam_y)
                if -50 < sx < SCREEN_W + 50 and -50 < sy < SCREEN_H + 50:
                    draw_pickup(screen, sx, sy, pk.get("type", "hp"))

            # 玩家
            for p in players_snap:
                psize = PLAYER_SIZE + p.get("size_bonus", 0)
                sx = int(p["x"] - cam_x); sy = int(p["y"] - cam_y)
                if not (-80 < sx < SCREEN_W + 80 and -80 < sy < SCREEN_H + 80):
                    continue
                if p.get("alive", True):
                    draw_shape(screen, p["shape"], p["color"], sx, sy, psize)
                    draw_hp_bar(screen, sx, sy, p["hp"], psize)
                else:
                    pygame.draw.circle(screen, (120, 120, 120), (sx, sy), psize, 2)
                    xx = font.render("X_X", True, (120, 120, 120))
                    screen.blit(xx, (sx - xx.get_width() // 2, sy - xx.get_height() // 2))
                id_s = font.render(p["id"], True, (0, 0, 0))
                screen.blit(id_s, (sx - id_s.get_width() // 2, sy + psize + 6))
                if p.get("chat") and now - p.get("chat_time", 0) < CHAT_DURATION:
                    draw_bubble(screen, sx, sy, p["chat"], psize)

            # 軌道子彈
            for o in orbits_snap:
                sx = int(o["x"] - cam_x); sy = int(o["y"] - cam_y)
                if -50 < sx < SCREEN_W + 50 and -50 < sy < SCREEN_H + 50:
                    col = tuple(o.get("color", (200, 100, 220)))
                    pygame.draw.circle(screen, col, (sx, sy), ORBIT_BULLET_RADIUS)
                    pygame.draw.circle(screen, (255, 255, 255), (sx, sy), ORBIT_BULLET_RADIUS, 2)

            # 子彈
            for b in bullets_snap:
                sx = int(b["x"] - cam_x); sy = int(b["y"] - cam_y)
                if -50 < sx < SCREEN_W + 50 and -50 < sy < SCREEN_H + 50:
                    if b.get("homing"):
                        pygame.draw.circle(screen, (240, 220, 60), (sx, sy), BULLET_RADIUS + 2)
                        pygame.draw.circle(screen, (0, 0, 0), (sx, sy), BULLET_RADIUS + 2, 1)
                    else:
                        pygame.draw.circle(screen, (255, 80, 20), (sx, sy), BULLET_RADIUS)
                        pygame.draw.circle(screen, (0, 0, 0), (sx, sy), BULLET_RADIUS, 1)

            # 準心（大十字 + 中央小點）
            if alive:
                mx, my = pygame.mouse.get_pos()
                pygame.draw.line(screen, (0, 0, 0), (mx - 12, my), (mx - 3, my), 2)
                pygame.draw.line(screen, (0, 0, 0), (mx + 3, my), (mx + 12, my), 2)
                pygame.draw.line(screen, (0, 0, 0), (mx, my - 12), (mx, my - 3), 2)
                pygame.draw.line(screen, (0, 0, 0), (mx, my + 3), (mx, my + 12), 2)
                pygame.draw.circle(screen, (255, 0, 0), (mx, my), 2)

            # 小地圖
            mm_x, mm_y = 10, SCREEN_H - MINIMAP_SIZE - 10
            mm_rect = pygame.Rect(mm_x, mm_y, MINIMAP_SIZE, MINIMAP_SIZE)
            pygame.draw.rect(screen, (30, 30, 30), mm_rect)
            pygame.draw.rect(screen, (255, 255, 255), mm_rect, 2)
            view_x = mm_x + cam_x * MINIMAP_SIZE / WORLD_W
            view_y = mm_y + cam_y * MINIMAP_SIZE / WORLD_H
            view_w = SCREEN_W * MINIMAP_SIZE / WORLD_W
            view_h = SCREEN_H * MINIMAP_SIZE / WORLD_H
            pygame.draw.rect(screen, (255, 255, 0),
                             pygame.Rect(view_x, view_y, view_w, view_h), 1)
            for pk in pickups_snap:
                mmx = mm_x + int(pk["x"] * MINIMAP_SIZE / WORLD_W)
                mmy = mm_y + int(pk["y"] * MINIMAP_SIZE / WORLD_H)
                pygame.draw.circle(screen, BUFF_COLORS.get(pk.get("type", "hp"), (200, 200, 200)),
                                   (mmx, mmy), 3)
            for p in players_snap:
                if not p.get("alive", True):
                    continue
                mmx = mm_x + int(p["x"] * MINIMAP_SIZE / WORLD_W)
                mmy = mm_y + int(p["y"] * MINIMAP_SIZE / WORLD_H)
                pygame.draw.circle(screen, tuple(p["color"]), (mmx, mmy), 3)

            # ====== HUD ======
            # 血條
            if me:
                hp = me["hp"]
                pygame.draw.rect(screen, (60, 0, 0), (10, 10, 320, 26))
                pygame.draw.rect(screen, (60, 200, 60), (10, 10, int(320 * hp / MAX_HP), 26))
                pygame.draw.rect(screen, (255, 255, 255), (10, 10, 320, 26), 2)
                hp_text = font.render(f"HP {hp} / {MAX_HP}", True, (255, 255, 255))
                screen.blit(hp_text, (16, 13))

            # 我的 Buff 條列（左上血條下方）
            if my_buffs:
                y = 44
                for name, remaining in my_buffs.items():
                    if name == "hp" or remaining <= 0:
                        continue
                    col = BUFF_COLORS.get(name, (200, 200, 200))
                    pygame.draw.circle(screen, col, (20, y + 10), 9)
                    pygame.draw.circle(screen, (0, 0, 0), (20, y + 10), 9, 1)
                    label_txt = f"{BUFF_ZH.get(name, name)}  {remaining:.1f}s"
                    t = font.render(label_txt, True, (255, 255, 255))
                    # 描邊背景
                    bg = pygame.Rect(32, y + 2, t.get_width() + 8, 20)
                    s = pygame.Surface((bg.w, bg.h), pygame.SRCALPHA)
                    s.fill((0, 0, 0, 130))
                    screen.blit(s, bg.topleft)
                    screen.blit(t, (36, y + 3))
                    y += 22

            # 玩家數
            cnt = font.render(f"線上：{len(players_snap)}", True, (0, 0, 0))
            screen.blit(cnt, (SCREEN_W - cnt.get_width() - 10, 10))

            # ====== 右下角半透明聊天視窗 ======
            panel_x = SCREEN_W - CHAT_PANEL_W - 10
            panel_y = SCREEN_H - CHAT_PANEL_H - 10
            panel = pygame.Surface((CHAT_PANEL_W, CHAT_PANEL_H), pygame.SRCALPHA)
            panel.fill((0, 0, 0, 130))
            screen.blit(panel, (panel_x, panel_y))
            pygame.draw.rect(screen, (255, 255, 255), (panel_x, panel_y, CHAT_PANEL_W, CHAT_PANEL_H), 1)

            # 訊息（最新 CHAT_LOG_SHOW 則）
            msgs = chat_log[-CHAT_LOG_SHOW:]
            row_h = 20
            text_y = panel_y + 8
            for m in msgs:
                line = f"[{m.get('author','?')}] {m.get('text','')}"
                if font.size(line)[0] > CHAT_PANEL_W - 16:
                    # 太長就截斷
                    while font.size(line + "…")[0] > CHAT_PANEL_W - 16 and len(line) > 3:
                        line = line[:-1]
                    line += "…"
                t = font.render(line, True, (255, 255, 255))
                screen.blit(t, (panel_x + 8, text_y))
                text_y += row_h

            # 輸入區
            input_y = panel_y + CHAT_PANEL_H - 32
            pygame.draw.rect(screen, (0, 0, 0), (panel_x, input_y, CHAT_PANEL_W, 32))
            pygame.draw.rect(screen, (255, 255, 255), (panel_x, input_y, CHAT_PANEL_W, 32), 1)
            if chat_active:
                caret = "|" if (pygame.time.get_ticks() // 500) % 2 == 0 else " "
                t = font.render("> " + chat_text + caret, True, (255, 255, 255))
                screen.blit(t, (panel_x + 8, input_y + 8))
            else:
                t = small.render("按 Enter 打字聊天 (中文 OK)", True, (170, 170, 170))
                screen.blit(t, (panel_x + 8, input_y + 10))

            # 底部操作提示
            hint = small.render(
                "WASD 移動 | 左鍵射擊 | Enter 打字 | F11 全螢幕",
                True, (60, 60, 60)
            )
            screen.blit(hint, (10 + MINIMAP_SIZE + 20, SCREEN_H - 22))

            # GameOver
            if me and not me.get("alive", True):
                overlay = pygame.Surface((SCREEN_W, SCREEN_H), pygame.SRCALPHA)
                overlay.fill((0, 0, 0, 150))
                screen.blit(overlay, (0, 0))
                go = huge.render("GAME OVER", True, (255, 60, 60))
                screen.blit(go, (SCREEN_W // 2 - go.get_width() // 2, SCREEN_H // 2 - 80))
                hint2 = big.render("按 Enter 重生", True, (255, 255, 255))
                screen.blit(hint2, (SCREEN_W // 2 - hint2.get_width() // 2, SCREEN_H // 2 + 10))

            pygame.display.flip()

    finally:
        running = False
