from enum import Enum

class Role(Enum):
    ADMIN = "Admin"
    LECTURER = "Lecturer"
    STUDENT = "Student"

class Status(Enum):
    ACTIVE = "ACTIVE"
    LOCKED = "LOCKED"
    ON_LEAVE = "ON_LEAVE"
    GRADUATED = "GRADUATED"
    DROPPED = "DROPPED"

# Mapping màu sắc giao diện dùng chung
COLORS = {
    "PRIMARY": "#0F766E",  # Teal đậm
    "SECONDARY": "#2A9D8F",
    "DANGER": "#EF4444",
    "SUCCESS": "#10B981",
    "TEXT": "#111827",
    "BG_LIGHT": "#F3F4F6"
}