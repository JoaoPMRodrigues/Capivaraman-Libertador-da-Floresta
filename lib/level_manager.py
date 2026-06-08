import json
import os


class LevelManager:
    SAVE_FILE = "save_data.json"
    TOTAL_LEVELS = 5

    def __init__(self):
        self.total_levels = self.TOTAL_LEVELS
        self._max_unlocked = 1      
        self._current_level = 1     
        self._load()

    # ------------------------------------------------------------------
    # Propriedades
    # ------------------------------------------------------------------

    @property
    def current_level(self) -> int:
        return self._current_level

    @current_level.setter
    def current_level(self, value: int):
        value = max(1, min(value, self.total_levels))
        self._current_level = value

    @property
    def max_unlocked(self) -> int:
        return self._max_unlocked

    # ------------------------------------------------------------------
    # API Pública
    # ------------------------------------------------------------------

    def is_unlocked(self, level: int) -> bool:
        return 1 <= level <= self._max_unlocked

    def unlock_next(self):
        next_level = self._current_level + 1
        if next_level <= self.total_levels:
            self._max_unlocked = max(self._max_unlocked, next_level)
        self._save()

    def advance(self):
        if self._current_level < self.total_levels:
            self._current_level += 1
            return True
        return False

    def reset_progress(self):
        self._max_unlocked = 1
        self._current_level = 1
        self._save()

    # ------------------------------------------------------------------
    # Persistência
    # ------------------------------------------------------------------

    def _load(self):
        if not os.path.exists(self.SAVE_FILE):
            return
        try:
            with open(self.SAVE_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
            self._max_unlocked = max(1, int(data.get("max_unlocked", 1)))
            self._current_level = max(1, int(data.get("current_level", 1)))
            # segurança: nunca ultrapassar limites
            self._max_unlocked = min(self._max_unlocked, self.total_levels)
            self._current_level = min(self._current_level, self.total_levels)
        except (json.JSONDecodeError, KeyError, ValueError):
            # arquivo corrompido → recomeça do zero
            self._max_unlocked = 1
            self._current_level = 1

    def _save(self):
        data = {
            "max_unlocked": self._max_unlocked,
            "current_level": self._current_level,
        }
        with open(self.SAVE_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)
