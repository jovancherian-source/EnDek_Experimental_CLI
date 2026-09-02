import sys
import os
import time

# ── UTF-8 Compatibility ───────────────────────────────────────
# Windows terminals default to cp1252 which breaks Unicode glyphs.

if sys.stdout.encoding != "utf-8":
    sys.stdout.reconfigure(encoding="utf-8")
if sys.stderr.encoding != "utf-8":
    sys.stderr.reconfigure(encoding="utf-8")


# ══════════════════════════════════════════════════════════════
#  COLOR SYSTEM
# ══════════════════════════════════════════════════════════════
# The orange palette (ANSI-214 / 208 / 172) is the brand identity.
# Supporting tones create a layered visual hierarchy without
# departing from the original color intention.

ORANGE       = "\033[38;5;214m"    # ● Primary brand
AMBER        = "\033[38;5;208m"    # ● Accent headings / active state
BURNT        = "\033[38;5;172m"    # ● Deep accent (breadcrumbs, muted)
DIM          = "\033[2m"           #   De-emphasized / secondary text
DIM_ORANGE   = "\033[2;38;5;214m"  #   Structural lines
BOLD         = "\033[1m"           #   Generic emphasis
BOLD_ORANGE  = "\033[1;38;5;214m"  #   Strong brand emphasis
BOLD_AMBER   = "\033[1;38;5;208m"  #   Active / highlighted option
RED          = "\033[38;5;203m"    # ● Danger
BOLD_RED     = "\033[1;38;5;203m"  #   Danger emphasis
GREEN        = "\033[38;5;114m"    # ● Success
BOLD_GREEN   = "\033[1;38;5;114m"  #   Success emphasis
CYAN         = "\033[38;5;116m"    # ● Info / hints
WHITE        = "\033[38;5;255m"    #   High-contrast text
GRAY         = "\033[38;5;245m"    #   Muted labels
DARK_GRAY    = "\033[38;5;240m"    #   Very muted (timestamps, etc.)
RESET        = "\033[0m"

# Cursor & line control
HIDE_CURSOR  = "\033[?25l"
SHOW_CURSOR  = "\033[?25h"
CLEAR_LINE   = "\033[2K\r"


# ══════════════════════════════════════════════════════════════
#  KEY INPUT  (cross-platform raw keypress reader)
# ══════════════════════════════════════════════════════════════

def _read_key():
    """
    Block until one keypress and return a semantic string:
      'up', 'down', 'enter', 'escape', or a character like '1'.
    Windows uses msvcrt; Unix uses tty/termios.
    """
    if os.name == "nt":
        import msvcrt
        raw = msvcrt.getwch()
        # Arrow keys on Windows send a two-char sequence: '\xe0' or '\x00'
        # followed by a scan-code character.
        if raw in ("\xe0", "\x00"):
            code = msvcrt.getwch()
            return {"H": "up", "P": "down", "K": "left", "M": "right"}.get(code)
        if raw == "\r":
            return "enter"
        if raw == "\x1b":
            return "escape"
        return raw  # regular character (digit, letter, etc.)
    else:
        import tty
        import termios
        import select as _select
        fd = sys.stdin.fileno()
        old = termios.tcgetattr(fd)
        try:
            tty.setraw(fd)
            ch = sys.stdin.read(1)
            if ch == "\x1b":
                # Could be a standalone Escape or the start of an arrow seq.
                if _select.select([sys.stdin], [], [], 0.05)[0]:
                    ch2 = sys.stdin.read(1)
                    if ch2 == "[":
                        ch3 = sys.stdin.read(1)
                        return {"A": "up", "B": "down", "C": "right", "D": "left"}.get(ch3)
                return "escape"
            if ch in ("\r", "\n"):
                return "enter"
            return ch
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old)


# ══════════════════════════════════════════════════════════════
#  ANIMATION ENGINE
# ══════════════════════════════════════════════════════════════

def _type_text(text, delay=0.018, color="", end="\n"):
    """Typewriter effect — prints each character with a small delay."""
    sys.stdout.write(color)
    for ch in text:
        sys.stdout.write(ch)
        sys.stdout.flush()
        time.sleep(delay)
    sys.stdout.write(RESET + end)
    sys.stdout.flush()


def _spinner(message, duration=1.2, color=ORANGE):
    """Inline braille spinner that runs for a fixed duration, then clears."""
    frames = ["⠋", "⠙", "⠹", "⠸", "⠼", "⠴", "⠦", "⠧", "⠇", "⠏"]
    end_time = time.time() + duration
    i = 0
    sys.stdout.write(HIDE_CURSOR)
    try:
        while time.time() < end_time:
            sys.stdout.write(f"{CLEAR_LINE}{color}{frames[i % len(frames)]}  {message}{RESET}")
            sys.stdout.flush()
            time.sleep(0.08)
            i += 1
    finally:
        sys.stdout.write(f"{CLEAR_LINE}{SHOW_CURSOR}")
        sys.stdout.flush()


def _progress_dots(message, count=3, delay=0.35, color=ORANGE):
    """Prints a message followed by animated dots."""
    sys.stdout.write(f"{color}{message}{RESET}")
    sys.stdout.flush()
    for _ in range(count):
        time.sleep(delay)
        sys.stdout.write(f"{DIM}.{RESET}")
        sys.stdout.flush()
    print()


# ══════════════════════════════════════════════════════════════
#  LAYOUT PRIMITIVES
# ══════════════════════════════════════════════════════════════

def _separator(width=50):
    """Thin dim rule — the primary structural element."""
    return f"{DIM_ORANGE}{'─' * width}{RESET}"


def _heavy_separator(width=50):
    """Double-stroke rule for major section boundaries."""
    return f"{BURNT}{'━' * width}{RESET}"


def _header(title, icon="", breadcrumb=""):
    """
    Section header with optional breadcrumb trail.
    Style: dim breadcrumb above, icon + bold-amber title, separator.
    """
    parts = []
    if breadcrumb:
        parts.append(f"  {DARK_GRAY}{breadcrumb}{RESET}")
    prefix = f"{icon}  " if icon else ""
    parts.append(f"\n{BOLD_AMBER}{prefix}{title}{RESET}")
    parts.append(_separator())
    return "\n".join(parts)


def _option(key, label, indent=2, active=False):
    """
    Menu option row.
    Active  → amber-filled circle ● + bold amber text
    Default → dim circle ○ + gray key + orange label
    """
    pad = " " * indent
    if active:
        return f"{pad}{AMBER}●{RESET}  {BOLD_AMBER}{key}{RESET}  {BOLD_AMBER}{label}{RESET}"
    return f"{pad}{DARK_GRAY}○{RESET}  {GRAY}{key}{RESET}  {ORANGE}{label}{RESET}"


def _prompt(text="❯"):
    """Minimal branded input prompt (for non-menu text inputs)."""
    return f"\n{BOLD_ORANGE}{text}{RESET} "


def _clear_screen():
    """Clear the viewport and park the cursor at 1,1."""
    sys.stdout.write("\033[2J\033[H")
    sys.stdout.flush()


# ══════════════════════════════════════════════════════════════
#  INTERACTIVE SELECTOR
# ══════════════════════════════════════════════════════════════
#
#  Arrow-key menu inspired by Claude Code / Inquirer prompts.
#    ↑/↓  navigate
#    Enter confirm
#    1-9   instant jump (press number key to select directly)
#    Esc   select last option (usually "Back" / "Exit")
#
#  Falls back to classic number input when stdin is not a tty.

def _select_menu(options, indent=2):
    """
    Interactive keyboard-driven menu.

    Parameters
    ----------
    options : list[tuple[str, str]]
        Each entry is (key, label), e.g. ("1", "Encryption Settings").

    Returns
    -------
    str
        The *key* string of the selected option ("1", "2", …).
    """
    # ── Fallback for non-interactive / piped stdin ────────────
    if not sys.stdin.isatty():
        for key, label in options:
            print(_option(key, label, indent=indent))
        print()
        print(_separator())
        return input(_prompt()).strip()

    selected = 0
    count = len(options)
    hint = f"  {DARK_GRAY}↑↓ navigate  ↵ select  {DIM}[1-{count}] quick-pick{RESET}"
    extra_lines = 2  # blank line + hint line
    total_lines = count + extra_lines

    sys.stdout.write(HIDE_CURSOR)
    sys.stdout.flush()

    # ── Initial staggered reveal ──────────────────────────────
    for i, (key, label) in enumerate(options):
        sys.stdout.write(
            _option(key, label, indent=indent, active=(i == selected)) + "\n"
        )
        sys.stdout.flush()
        time.sleep(0.04)

    sys.stdout.write("\n" + hint + "\n")
    sys.stdout.flush()

    # ── Navigation loop ───────────────────────────────────────
    try:
        while True:
            k = _read_key()

            if k == "up":
                selected = (selected - 1) % count
            elif k == "down":
                selected = (selected + 1) % count
            elif k == "enter":
                break
            elif k == "escape":
                selected = count - 1   # jump to last ("Back" / "Exit")
                break
            elif k is not None and k.isdigit():
                # Quick-pick: press a number key to jump + confirm
                for idx, (okey, _label) in enumerate(options):
                    if okey == k:
                        selected = idx
                        break
                break  # confirm immediately on number press
            else:
                continue

            # ── Re-render options in place ────────────────────
            sys.stdout.write(f"\033[{total_lines}A")
            for i, (key, label) in enumerate(options):
                sys.stdout.write(
                    CLEAR_LINE
                    + _option(key, label, indent=indent, active=(i == selected))
                    + "\n"
                )
            sys.stdout.write(CLEAR_LINE + "\n")
            sys.stdout.write(CLEAR_LINE + hint + "\n")
            sys.stdout.flush()

    finally:
        sys.stdout.write(SHOW_CURSOR)
        sys.stdout.flush()

    # ── Collapse to selection confirmation ────────────────────
    # Replace the entire options block with a single answer line.
    sys.stdout.write(f"\033[{total_lines}A")
    # First line: the confirmed choice
    sys.stdout.write(
        CLEAR_LINE
        + f"  {BOLD_GREEN}✔{RESET}  {ORANGE}{options[selected][1]}{RESET}\n"
    )
    # Clear remaining lines
    for _ in range(total_lines - 1):
        sys.stdout.write(CLEAR_LINE + "\n")
    # Move cursor back up to right after the answer line
    sys.stdout.write(f"\033[{total_lines - 1}A")
    sys.stdout.flush()

    return options[selected][0]


# ══════════════════════════════════════════════════════════════
#  STATUS MESSAGES  (for use in Encrypter.py or anywhere)
# ══════════════════════════════════════════════════════════════

def success(msg):
    """Green checkmark + message."""
    print(f"  {BOLD_GREEN}✔{RESET}  {GREEN}{msg}{RESET}")

def error(msg):
    """Red cross + message."""
    print(f"  {BOLD_RED}✖{RESET}  {RED}{msg}{RESET}")

def warn(msg):
    """Amber warning triangle + message."""
    print(f"  {BOLD_AMBER}▲{RESET}  {AMBER}{msg}{RESET}")

def info(msg):
    """Cyan info dot + message."""
    print(f"  {CYAN}●{RESET}  {CYAN}{msg}{RESET}")


# ══════════════════════════════════════════════════════════════
#  LOGO / BANNER
# ══════════════════════════════════════════════════════════════

_LOGO_LINES = [
    "  ███████╗",
    "  ██╔════╝      ██████╗       ██╗  ██╗",
    "  ██║    _ __   ██╔══██╗      ██║ ██╔╝",
    "  █████╗| '_ \\  ██║  ██║/ _ \\ ██╠═██╔╝",
    "  ██╔══╝| | | | ██║  ██║  __/ ██║╚██╗",
    "  ██║   |_| |_| ██████╔╝\\___| ██║ ╚██╗",
    "  ███████╗      ╚═════╝       ╚═╝  ╚═╝",
]


def logos():
    """Animated banner with staggered line reveal + typewriter tagline."""
    _clear_screen()
    print()

    for line in _LOGO_LINES:
        print(f"{ORANGE}{line}{RESET}")
        sys.stdout.flush()
        time.sleep(0.045)

    print()
    _type_text("  terminal encryption toolkit", delay=0.025, color=DIM)
    print(f"  {DARK_GRAY}{'─' * 38}{RESET}")
    print()


# ══════════════════════════════════════════════════════════════
#  MENUS
# ══════════════════════════════════════════════════════════════

def EnDek_config_logo():
    """
    Main configuration hub.
    Returns the key string of the selected option ("1"–"5").
    """
    print(_header("EnDek Config", "⚙", breadcrumb="home"))
    print()

    return _select_menu([
        ("1", "Encryption Settings"),
        ("2", "Account Settings"),
        ("3", "Database Settings"),
        ("4", "EnDek Settings"),
        ("5", "Exit"),
    ])


# ── EnDek Settings ───────────────────────────────────────────

def endek_dual_settings():
    print(_header("EnDek Settings", "⚙", breadcrumb="home / config"))
    print()

    return _select_menu([
        ("1", "About EnDek"),
        ("2", "Check for Updates"),
        ("3", "← Back"),
    ])


# ── Encryption Settings ──────────────────────────────────────

def EnDek_encyption_settings_menu():
    print(_header("Encryption Settings", "🔐", breadcrumb="home / config"))
    print()

    return _select_menu([
        ("1", "Enter custom key"),
        ("2", "Generate secure random key"),
        ("3", "Scramble settings"),
        ("4", "Export key"),
        ("5", "Back"),
    ])


# ── Database Settings ─────────────────────────────────────────

def Database_settings_menu():
    print(_header("Database Settings", "🗄", breadcrumb="home / config"))
    print()
    print(f"  {BOLD_RED}▲  Warning{RESET}")
    print(f"  {GRAY}Clearing the database permanently removes{RESET}")
    print(f"  {GRAY}all stored data. This cannot be undone.{RESET}")
    print()
    print(_separator())
    print()

    return _select_menu([
        ("1", "Clear Database"),
        ("2", "← Back"),
    ])


# ── Account Settings ──────────────────────────────────────────

def Account_settings_menu():
    print(_header("Account Settings", "👤", breadcrumb="home / config"))
    print()
    print(f"  {GRAY}General{RESET}")

    # Print the "General" option manually, then danger section,
    # but use a single _select_menu over all options for unified navigation.

    return _select_menu([
        ("1", "Log Out"),
        ("2", "Delete Account"),
        ("3", "← Back"),
    ])


# ── Delete Account Confirmation ───────────────────────────────

def Account_confirmation_menu():
    print(_header("Delete Account", "▲", breadcrumb="home / config / account"))
    print()
    print(f"  {BOLD_RED}This action cannot be undone.{RESET}")
    print(f"  {GRAY}Your account and all associated data{RESET}")
    print(f"  {GRAY}will be permanently deleted.{RESET}")
    print()
    print(_separator())
    print()

    return _select_menu([
        ("1", "Yes, Delete My Account"),
        ("2", "Cancel"),
    ])


# ── Scramble Settings (first time) ────────────────────────────

def first_Scramble_settings_menu():
    print(_header("Scramble Settings", "🔀", breadcrumb="home / config / encryption"))
    print()

    return _select_menu([
        ("1", "Enable Text Scrambling"),
        ("2", "← Back"),
    ])


# ── Scramble Settings (already enabled) ───────────────────────

def Scramble_settings_menu():
    print(_header("Scrambler Settings", "🔀", breadcrumb="home / config / encryption"))
    print()

    return _select_menu([
        ("1", "Change Scrambler"),
        ("2", "Disable Scrambler"),
        ("3", "← Back"),
    ])


# ── Change Scrambler — method picker ─────────────────────────

def new_Scramble_settings_menu():
    """
    Shown when the user picks 'Change Scrambler'.
    Returns "1" (custom key), "2" (random key), or "3" (cancel).
    """
    print(_header("Scrambler Key", "🔑", breadcrumb="home / config / encryption / scrambler"))
    print()

    return _select_menu([
        ("1", "Enter Custom Scrambler Key"),
        ("2", "Generate Random Scrambler Key"),
        ("3", "Cancel"),
    ])


# ── Enter Custom Scrambler Key ────────────────────────────────

def new_Scramble_key_for_pre_user():
    """
    Prompts the user to type a custom scrambler key string.
    Returns the raw key string.
    """
    print(_header("Custom Scrambler Key", "🔑", breadcrumb="home / config / encryption / scrambler"))
    print()
    return prompt_text("Scrambler Key")


# ══════════════════════════════════════════════════════════════
#  INTERACTIVE INPUT PROMPTS
# ══════════════════════════════════════════════════════════════
#
#  Styled input helpers for login, passwords, confirmations,
#  and the main REPL. These replace raw input()/getpass calls
#  in Encrypter.py for a cohesive Claude Code-like experience.

import getpass as _getpass


def prompt_username():
    """
    Styled username input with label and branded prompt.
    Returns the entered username string.
    """
    print(f"\n  {GRAY}Sign in to EnDek{RESET}")
    print(_separator())
    return input(f"  {ORANGE}username{RESET} {BOLD_ORANGE}❯{RESET} ")


def prompt_password(label="password"):
    """
    Styled password input — characters are masked.
    Uses getpass for secure entry with a branded label.
    """
    return _getpass.getpass(f"  {ORANGE}{label}{RESET} {BOLD_ORANGE}❯{RESET} ")


def prompt_confirm(question, default_yes=False):
    """
    Interactive yes/no selector using the keyboard menu.
    Returns True for yes, False for no.
    """
    print(f"\n  {AMBER}{question}{RESET}")
    print()
    if default_yes:
        opts = [("y", "Yes"), ("n", "No")]
    else:
        opts = [("n", "No"), ("y", "Yes")]
    result = _select_menu(opts, indent=2)
    return result == "y"


def prompt_text(label):
    """
    Styled single-line text input with a visible label.
    """
    return input(f"  {ORANGE}{label}{RESET} {BOLD_ORANGE}❯{RESET} ")


def prompt_repl(username=None):
    """
    Main REPL prompt for encrypt/decrypt input.
    Hint: type /config for settings, exit to quit.
    """
    return input(f"\n  {BOLD_ORANGE}❯{RESET} ")


def prompt_guest_repl():
    """
    REPL prompt for non-authenticated guest sessions.
    """
    return input(f"\n  {BOLD_ORANGE}❯{RESET} ")


def welcome(username):
    """
    Welcome banner shown after successful login.
    """
    _spinner(f"Authenticating {username}", duration=0.8)
    print()
    print(f"  {BOLD_GREEN}✔{RESET}  {GREEN}Welcome back, {BOLD}{username}{RESET}")
    print(f"  {DARK_GRAY}Type text to encrypt · /config for settings · exit to quit{RESET}")
    print(_separator())


def welcome_new_user(username):
    """
    Welcome banner shown after account creation.
    """
    _spinner("Creating account", duration=0.8)
    print()
    print(f"  {BOLD_GREEN}✔{RESET}  {GREEN}Account created for {BOLD}{username}{RESET}")
    print(_separator())


def show_result(text):
    """
    Display an encryption/decryption result with visual emphasis.
    """
    print(f"\n  {BOLD_ORANGE}→{RESET}  {WHITE}{text}{RESET}")


def show_key(label, value):
    """
    Display a key-value pair (e.g. encryption key export).
    """
    print(f"  {GRAY}{label}:{RESET} {WHITE}{value}{RESET}")