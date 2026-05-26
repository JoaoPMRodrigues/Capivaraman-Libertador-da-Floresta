def show_fps(window, cooldown, dt, fps):

    cooldown -= dt

    if cooldown < 0:
        fps = int(1 / dt) if dt > 0 else 0
        cooldown = 0.3
    window.draw_text(
        f"FPS: {fps}", 10, 10, size=50, color=(255, 255, 255))

    return cooldown, fps
