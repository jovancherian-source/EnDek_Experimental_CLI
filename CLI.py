"""
EnDek CLI — Terminal Interface
Redesigned with Anthropic Claude Code aesthetic:
  - Exact palette from Design.md (Warm Coral #cc785c, Cream #faf9f5, Dark Surface #181715)
  - Claude Code Clawd mascot + filled block logo with vertical warm coral gradient
  - Arrow-key interactive navigation with in-place collapse
  - Rounded Unicode cards, callouts, and code-block result containers
  - Full cross-platform support (Windows / macOS / Linux)
"""

import sys
import os
import time
import textwrap
import getpass as _getpass

# ── UTF-8 Compatibility ───────────────────────────────────────
# Windows terminals default to cp1252 which breaks Unicode glyphs.
if sys.stdout.encoding != "utf-8":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass
if sys.stderr.encoding != "utf-8":
    try:
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass


# ══════════════════════════════════════════════════════════════
#  COLOR SYSTEM  (24-bit TrueColor matching Design.md)
# ══════════════════════════════════════════════════════════════
# Anthropic Claude Palette:
#   primary:              #cc785c  (signature warm coral)
#   primary-active:       #a9583e  (active / pressed coral)
#   accent-amber:         #e8a55a  (warm companion tone)
#   accent-teal:          #5db8a6  (status indicator teal)
#   canvas / on-dark:     #faf9f5  (warm cream white)
#   surface-card:         #efe9de  (cream card tone)
#   on-dark-soft:         #a09d96  (secondary muted text)
#   muted:                #6c6a64  (dark muted / breadcrumbs)
#   hairline / border:    #3d3d3a  (structural borders)
#   success:              #5db872  (Claude success green)
#   warning:              #d4a017  (warning amber)
#   error:                #c64545  (error coral-red)

RESET         = "\033[0m"
BOLD          = "\033[1m"
DIM           = "\033[2m"
ITALIC        = "\033[3m"
UNDERLINE     = "\033[4m"

# Signature Anthropic Claude colors (TrueColor 24-bit)
CORAL         = "\033[38;2;204;120;92m"    # #cc785c  Primary brand
CORAL_ACTIVE  = "\033[38;2;169;88;62m"     # #a9583e  Active / hover
CORAL_LIGHT   = "\033[38;2;225;145;98m"    # Highlight gradient step
AMBER         = "\033[38;2;232;165;90m"    # #e8a55a  Accent amber
TEAL          = "\033[38;2;93;184;166m"    # #5db8a6  Accent teal
CREAM         = "\033[38;2;250;249;245m"   # #faf9f5  High-contrast text (on-dark)
CREAM_CARD    = "\033[38;2;239;233;222m"   # #efe9de  Card cream
MUTED         = "\033[38;2;160;157;150m"   # #a09d96  Secondary labels / captions
MUTED_DARK    = "\033[38;2;108;106;100m"   # #6c6a64  Sub-headings / keys
BORDER        = "\033[38;2;61;61;58m"      # #3d3d3a  Hairline separators
BORDER_SUBTLE = "\033[38;2;46;44;41m"      # #2e2c29  Inner dividers

SEMANTIC_SUCCESS = "\033[38;2;93;184;114m" # #5db872  Success green
SEMANTIC_WARNING = "\033[38;2;212;160;23m" # #d4a017  Warning gold
SEMANTIC_ERROR   = "\033[38;2;198;69;69m"  # #c64545  Error red

# Background tones for cards/badges
BG_CARD       = "\033[48;2;37;35;32m"      # #252320  Surface dark elevated
BG_CORAL      = "\033[48;2;204;120;92m"    # #cc785c  Coral pill fill
BG_DARK_SOFT  = "\033[48;2;31;30;27m"      # #1f1e1b  Soft dark panel

# Backward-compatibility aliases for existing references
ORANGE        = CORAL
BURNT         = CORAL_ACTIVE
DIM_ORANGE    = BORDER
BOLD_ORANGE   = f"{BOLD}{CORAL}"
BOLD_AMBER    = f"{BOLD}{AMBER}"
GREEN         = SEMANTIC_SUCCESS
BOLD_GREEN    = f"{BOLD}{SEMANTIC_SUCCESS}"
RED           = SEMANTIC_ERROR
BOLD_RED      = f"{BOLD}{SEMANTIC_ERROR}"
CYAN          = TEAL
WHITE         = CREAM
GRAY          = MUTED
DARK_GRAY     = MUTED_DARK

# Cursor & terminal control
HIDE_CURSOR   = "\033[?25l"
SHOW_CURSOR   = "\033[?25h"
CLEAR_LINE    = "\033[2K\r"


# ══════════════════════════════════════════════════════════════
#  CROSS-PLATFORM RAW KEY INPUT
# ══════════════════════════════════════════════════════════════

def _read_key():
    """
    Block until one keypress and return a semantic string:
      'up', 'down', 'enter', 'escape', or a character like '1'.
    Supports arrow keys and vim navigation ('k'/'j').
    """
    if os.name == "nt":
        import msvcrt
        raw = msvcrt.getwch()
        if raw in ("\xe0", "\x00"):
            code = msvcrt.getwch()
            return {"H": "up", "P": "down", "K": "left", "M": "right"}.get(code)
        if raw == "\r":
            return "enter"
        if raw == "\x1b":
            return "escape"
        if raw in ("k", "K"):
            return "up"
        if raw in ("j", "J"):
            return "down"
        return raw
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
                if _select.select([sys.stdin], [], [], 0.05)[0]:
                    ch2 = sys.stdin.read(1)
                    if ch2 == "[":
                        ch3 = sys.stdin.read(1)
                        return {"A": "up", "B": "down", "C": "right", "D": "left"}.get(ch3)
                return "escape"
            if ch in ("\r", "\n"):
                return "enter"
            if ch in ("k", "K"):
                return "up"
            if ch in ("j", "J"):
                return "down"
            return ch
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old)


# ══════════════════════════════════════════════════════════════
#  ANIMATION & SPINNER ENGINE
# ══════════════════════════════════════════════════════════════

def _type_text(text, delay=0.015, color=MUTED, end="\n"):
    """Smooth typewriter effect for taglines and system messages."""
    sys.stdout.write(color)
    for ch in text:
        sys.stdout.write(ch)
        sys.stdout.flush()
        time.sleep(delay)
    sys.stdout.write(RESET + end)
    sys.stdout.flush()


def _spinner(message, duration=0.8, color=CORAL):
    """
    Claude Code-style smooth braille activity spinner.
    Ensures cursor is safely restored upon completion.
    """
    frames = ["⠋", "⠙", "⠹", "⠸", "⠼", "⠴", "⠦", "⠧", "⠇", "⠏"]
    end_time = time.time() + duration
    i = 0
    sys.stdout.write(HIDE_CURSOR)
    try:
        while time.time() < end_time:
            sys.stdout.write(f"{CLEAR_LINE}  {color}{frames[i % len(frames)]}{RESET}  {MUTED}{message}{RESET}")
            sys.stdout.flush()
            time.sleep(0.07)
            i += 1
    finally:
        sys.stdout.write(f"{CLEAR_LINE}{SHOW_CURSOR}")
        sys.stdout.flush()


def _progress_dots(message, count=3, delay=0.25, color=CORAL):
    """Prints a message followed by animated dots."""
    sys.stdout.write(f"  {color}{message}{RESET}")
    sys.stdout.flush()
    for _ in range(count):
        time.sleep(delay)
        sys.stdout.write(f"{MUTED_DARK}.{RESET}")
        sys.stdout.flush()
    print()


# ══════════════════════════════════════════════════════════════
#  LAYOUT PRIMITIVES & CARDS (Claude Editorial Aesthetic)
# ══════════════════════════════════════════════════════════════

def _separator(width=52):
    """Sleek hairline rule matching Design.md dark theme."""
    return f"  {BORDER}{'─' * width}{RESET}"


def _heavy_separator(width=52):
    """Accent hairline rule."""
    return f"  {CORAL_ACTIVE}{'─' * width}{RESET}"


def _header(title, breadcrumb=""):
    """
    Section header with breadcrumb trail and Anthropic radial spark.
    Follows Claude Code visual hierarchy.
    """
    lines = []
    if breadcrumb:
        lines.append(f"\n  {MUTED_DARK}{breadcrumb}{RESET}")
    else:
        lines.append("")
    lines.append(f"  {CORAL}✻{RESET}  {BOLD}{CREAM}{title}{RESET}")
    lines.append(_separator())
    return "\n".join(lines)


def _callout(title, lines, color=SEMANTIC_WARNING, width=52):
    """
    Anthropic-style rounded callout box for warnings, notices, and errors.
    """
    title_bar = f"╭─ {title} "
    fill_len = max(width - len(title) - 5, 2)
    print(f"  {color}{title_bar}{'─' * fill_len}╮{RESET}")
    for line in lines:
        pad_len = max(width - len(line) - 4, 0)
        print(f"  {color}│{RESET}  {CREAM}{line}{' ' * pad_len}  {color}│{RESET}")
    print(f"  {color}╰{'─' * width}╯{RESET}")


def _option(key, label, indent=2, active=False):
    """
    Menu option row styled after Claude Code interactive selectors.
    Active   → Bold Coral pointer '❯' + Coral key + Bold Cream label
    Inactive → Muted key + Soft Cream label
    """
    pad = " " * indent
    if active:
        return f"{pad}{BOLD}{CORAL}❯{RESET} {BOLD}{CORAL}{key}.{RESET}  {BOLD}{CREAM}{label}{RESET}"
    return f"{pad}  {MUTED_DARK}{key}.{RESET}  {MUTED}{label}{RESET}"


def _prompt(text="❯"):
    """Signature Claude Code Coral prompt indicator."""
    return f"\n  {BOLD}{CORAL}{text}{RESET} "


def _clear_screen():
    """Clear the terminal viewport."""
    sys.stdout.write("\033[2J\033[H")
    sys.stdout.flush()


# ══════════════════════════════════════════════════════════════
#  INTERACTIVE KEYBOARD SELECTOR
# ══════════════════════════════════════════════════════════════

def _select_menu(options, indent=2):
    """
    Keyboard-driven interactive menu styled after Claude Code.

    Features:
      ↑/↓ or j/k : Navigate options
      Enter      : Confirm selection
      1-9        : Quick-pick direct option
      Esc        : Select last option (Back/Exit)

    Parameters
    ----------
    options : list[tuple[str, str]]
        List of (key, label) tuples.

    Returns
    -------
    str
        The selected key string.
    """
    # Fallback for non-interactive / piped environments
    if not sys.stdin.isatty():
        for key, label in options:
            print(_option(key, label, indent=indent))
        print(_separator())
        try:
            return input(_prompt()).strip()
        except EOFError:
            return options[-1][0]

    selected = 0
    count = len(options)
    hint = f"  {MUTED_DARK}↑/↓ navigate  •  ↵ select  •  [1-{count}] quick pick  •  esc back{RESET}"
    extra_lines = 2  # blank line + hint line
    total_lines = count + extra_lines

    sys.stdout.write(HIDE_CURSOR)
    sys.stdout.flush()

    # Initial reveal
    for i, (key, label) in enumerate(options):
        sys.stdout.write(_option(key, label, indent=indent, active=(i == selected)) + "\n")
        sys.stdout.flush()
        time.sleep(0.02)

    sys.stdout.write("\n" + hint + "\n")
    sys.stdout.flush()

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
                selected = count - 1
                break
            elif k is not None and k.isdigit():
                # Quick-pick direct jump
                matched = False
                for idx, (okey, _label) in enumerate(options):
                    if okey == k:
                        selected = idx
                        matched = True
                        break
                if matched:
                    break
            else:
                continue

            # In-place re-render of option lines
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

    except KeyboardInterrupt:
        sys.stdout.write(SHOW_CURSOR)
        sys.stdout.flush()
        raise
    finally:
        sys.stdout.write(SHOW_CURSOR)
        sys.stdout.flush()

    # In-place collapse to a single clean confirmation line
    sys.stdout.write(f"\033[{total_lines}A")
    sys.stdout.write(
        CLEAR_LINE
        + f"  {SEMANTIC_SUCCESS}✔{RESET}  {BOLD}{CREAM}{options[selected][1]}{RESET}\n"
    )
    for _ in range(total_lines - 1):
        sys.stdout.write(CLEAR_LINE + "\n")
    sys.stdout.write(f"\033[{total_lines - 1}A")
    sys.stdout.flush()

    return options[selected][0]


# ══════════════════════════════════════════════════════════════
#  STATUS MESSAGES (Claude Editorial Indicators)
# ══════════════════════════════════════════════════════════════

def success(msg):
    """Claude green checkmark + message."""
    print(f"  {SEMANTIC_SUCCESS}✔{RESET}  {CREAM}{msg}{RESET}")


def error(msg):
    """Claude red cross + message."""
    print(f"  {SEMANTIC_ERROR}✖{RESET}  {SEMANTIC_ERROR}{msg}{RESET}")


def warn(msg):
    """Claude amber warning indicator + message."""
    print(f"  {SEMANTIC_WARNING}▲{RESET}  {AMBER}{msg}{RESET}")


def info(msg):
    """Claude teal Anthropic radial spark + message."""
    print(f"  {TEAL}✻{RESET}  {MUTED}{msg}{RESET}")


# ══════════════════════════════════════════════════════════════
#  CLAUDE CODE LOGO / STARTUP BANNER
# ══════════════════════════════════════════════════════════════
# Features:
#   1. Clawd mascot block with version pills
#   2. Filled block wordmark 'ENDEK' with 6-step vertical coral gradient
#   3. Typewriter tagline with Anthropic radial spark

_ENDEK_BLOCK_LOGO = [
    "  ███████╗███╗   ██╗██████╗ ███████╗██╗  ██╗",
    "  ██╔════╝████╗  ██║██╔══██╗██╔════╝██║ ██╔╝",
    "  █████╗  ██╔██╗ ██║██║  ██║█████╗  █████╔╝ ",
    "  ██╔══╝  ██║╚██╗██║██║  ██║██╔══╝  ██╔═██╗ ",
    "  ███████╗██║ ╚████║██████╔╝███████╗██║  ██╗",
    "  ╚══════╝╚═╝  ╚═══╝╚═════╝ ╚══════╝╚═╝  ╚═╝",
]

_GRADIENT_STEPS = [
    "\033[38;2;238;175;110m",  # Soft amber highlight
    "\033[38;2;225;145;98m",   # Amber-coral
    "\033[38;2;215;130;94m",   # Vibrant coral
    "\033[38;2;204;120;92m",   # Signature Claude Coral (#cc785c)
    "\033[38;2;185;102;76m",   # Deep coral
    "\033[38;2;169;88;62m",    # Primary active coral (#a9583e)
]


def logos():
    """
    Claude Code-inspired startup banner with animated Clawd mascot,
    vertical coral gradient wordmark, and tagline.
    """
    _clear_screen()
    print()

    # 1. Claude Code Mascot Header
    print(f"  {CORAL}▐▛▀▀▀▀▜▌{RESET}  {BOLD}{CREAM}EnDek{RESET} {MUTED}v2.7.0{RESET} {BORDER}·{RESET} {TEAL}Experimental CLI v1.5.0{RESET}")
    print(f"  {CORAL}▐▌ · ·▐▌{RESET}  {MUTED}Lightweight interactive encryption toolkit{RESET}")
    print(f"  {CORAL}▐▙▄▄▄▄▟▌{RESET}  {MUTED_DARK}https://github.com/jovancherian-source/EnDek{RESET}")
    print()
    sys.stdout.flush()
    time.sleep(0.04)

    # 2. Gradient Block Logo Reveal
    for color, line in zip(_GRADIENT_STEPS, _ENDEK_BLOCK_LOGO):
        print(f"{color}{line}{RESET}")
        sys.stdout.flush()
        time.sleep(0.025)

    print()
    # 3. Subtitle Tagline
    _type_text(f"  {CORAL}✻{RESET}  {MUTED}terminal encryption toolkit{RESET}  {BORDER}·{RESET}  {MUTED_DARK}interactive session{RESET}", delay=0.012)
    print(_separator())
    print()


# ══════════════════════════════════════════════════════════════
#  MENUS
# ══════════════════════════════════════════════════════════════

def EnDek_config_logo():
    """
    Main configuration hub.
    Returns selected option key ("1"–"5").
    """
    print(_header("EnDek Configuration", breadcrumb="home › config"))
    print()
    return _select_menu([
        ("1", "Encryption Settings"),
        ("2", "Account Settings"),
        ("3", "Database Settings"),
        ("4", "EnDek Settings"),
        ("5", "Exit"),
    ])


def endek_dual_settings():
    """EnDek system and version settings."""
    print(_header("EnDek Settings", breadcrumb="home › config › system"))
    print()
    return _select_menu([
        ("1", "About EnDek"),
        ("2", "Check for Updates"),
        ("3", "← Back"),
    ])


def EnDek_encyption_settings_menu():
    """Encryption key and algorithm settings."""
    print(_header("Encryption Settings", breadcrumb="home › config › encryption"))
    print()
    return _select_menu([
        ("1", "Enter Custom Key"),
        ("2", "Generate Secure Random Key"),
        ("3", "Scramble Settings"),
        ("4", "Export Key"),
        ("5", "← Back"),
    ])


def Database_settings_menu():
    """Database management settings with callout warning."""
    print(_header("Database Settings", breadcrumb="home › config › database"))
    print()
    _callout("▲ Warning", [
        "Clearing the database permanently removes all stored data.",
        "Your encryption keys and accounts will be deleted.",
        "This action cannot be undone."
    ], color=SEMANTIC_WARNING)
    print()
    return _select_menu([
        ("1", "Clear Database"),
        ("2", "← Back"),
    ])


def Account_settings_menu():
    """Account profile settings."""
    print(_header("Account Settings", breadcrumb="home › config › account"))
    print()
    return _select_menu([
        ("1", "Log Out"),
        ("2", "Delete Account"),
        ("3", "← Back"),
    ])


def Account_confirmation_menu():
    """Account deletion confirmation dialog."""
    print(_header("Delete Account", breadcrumb="home › config › account › delete"))
    print()
    _callout("▲ Permanent Deletion", [
        "Your local account and all associated keys will be wiped.",
        "Data encrypted with your current keys will be lost",
        "unless you have exported them."
    ], color=SEMANTIC_ERROR)
    print()
    return _select_menu([
        ("1", "Yes, Permanently Delete My Account"),
        ("2", "Cancel"),
    ])


def first_Scramble_settings_menu():
    """First-time text scrambling toggle."""
    print(_header("Scramble Settings", breadcrumb="home › config › encryption › scrambler"))
    print()
    return _select_menu([
        ("1", "Enable Text Scrambling"),
        ("2", "← Back"),
    ])


def Scramble_settings_menu():
    """Scrambler management menu."""
    print(_header("Scrambler Settings", breadcrumb="home › config › encryption › scrambler"))
    print()
    return _select_menu([
        ("1", "Change Scrambler Key"),
        ("2", "Disable Scrambler"),
        ("3", "← Back"),
    ])


def new_Scramble_settings_menu():
    """Scrambler key generation mode."""
    print(_header("Scrambler Key Setup", breadcrumb="home › config › encryption › scrambler › key"))
    print()
    return _select_menu([
        ("1", "Enter Custom Scrambler Key"),
        ("2", "Generate Random Scrambler Key"),
        ("3", "Cancel"),
    ])


def new_Scramble_key_for_pre_user():
    """Prompt for a custom scrambler key string."""
    print(_header("Custom Scrambler Key", breadcrumb="home › config › encryption › scrambler › key"))
    print()
    return prompt_text("Scrambler Key")


# ══════════════════════════════════════════════════════════════
#  INTERACTIVE INPUT PROMPTS & REPL
# ══════════════════════════════════════════════════════════════

def prompt_username():
    """
    Styled username input in Claude Code editorial style.
    """
    print()
    print(f"  {CORAL}✻{RESET}  {BOLD}{CREAM}Sign in to EnDek{RESET}")
    print(_separator())
    return input(f"  {MUTED}username{RESET} {BOLD}{CORAL}❯{RESET} ").strip()


def prompt_password(label="password"):
    """
    Secure password prompt with Claude Code styling.
    """
    return _getpass.getpass(f"  {MUTED}{label}{RESET} {BOLD}{CORAL}❯{RESET} ").strip()


def prompt_confirm(question, default_yes=False):
    """
    Interactive keyboard yes/no selector.
    Returns True for Yes, False for No.
    """
    print()
    print(f"  {CORAL}✻{RESET}  {CREAM}{question}{RESET}")
    if default_yes:
        opts = [("y", "Yes"), ("n", "No")]
    else:
        opts = [("n", "No"), ("y", "Yes")]
    result = _select_menu(opts, indent=2)
    return result == "y"


def prompt_text(label):
    """
    Styled single-line text input with clean prompt.
    """
    return input(f"  {MUTED}{label}{RESET} {BOLD}{CORAL}❯{RESET} ").strip()


def prompt_repl(username=None):
    """
    Main interactive REPL prompt styled after Claude Code.
    """
    return input(f"\n  {BOLD}{CORAL}❯{RESET} ").strip()


def prompt_guest_repl():
    """
    Guest REPL prompt for non-authenticated sessions.
    """
    return input(f"\n  {MUTED_DARK}[guest]{RESET} {BOLD}{CORAL}❯{RESET} ").strip()


def welcome(username):
    """
    Welcome banner displayed after successful user authentication.
    """
    _spinner(f"Authenticating {username}", duration=0.6)
    print()
    print(f"  {SEMANTIC_SUCCESS}✔{RESET}  {BOLD}{CREAM}Welcome back, {username}{RESET}")
    print(f"  {MUTED}Enter plain text to encrypt, or ciphertext to decrypt.{RESET}")
    print(f"  {MUTED_DARK}Commands: {CORAL}/config{MUTED_DARK} settings  •  {CORAL}/logout{MUTED_DARK} sign out  •  {CORAL}/exit{MUTED_DARK} quit{RESET}")
    print(_separator())


def welcome_new_user(username):
    """
    Welcome banner displayed after account registration.
    """
    _spinner("Initializing new user profile", duration=0.7)
    print()
    print(f"  {SEMANTIC_SUCCESS}✔{RESET}  {BOLD}{CREAM}Account created for {username}{RESET}")
    print(f"  {MUTED}Your encryption keys will be stored locally for future sessions.{RESET}")
    print(_separator())


def show_result(text, label="Result"):
    """
    Display cryptographic output in a Claude Code terminal code card.
    Handles long text wrapping gracefully.
    """
    max_w = 66
    lines = textwrap.wrap(text, width=max_w) if len(text) > max_w else [text]
    box_w = max(max(len(l) for l in lines) + 4, len(label) + 8, 46)

    print(f"\n  {BORDER}╭─ {CORAL}{label}{BORDER} {'─' * (box_w - len(label) - 5)}╮{RESET}")
    for l in lines:
        pad = box_w - len(l) - 4
        print(f"  {BORDER}│{RESET}  {BOLD}{CREAM}{l}{RESET}{' ' * pad}  {BORDER}│{RESET}")
    print(f"  {BORDER}╰{'─' * box_w}╯{RESET}")


def show_key(label, value):
    """
    Display an exported key-value pair with Claude Code alignment.
    """
    print(f"  {MUTED}{label:<18}{RESET} {BORDER}│{RESET}  {BOLD}{CREAM}{value}{RESET}")


def show_about(version, cli_version, key_status="Active", users_count=1, scrambler_enabled=False):
    """
    Display formatted system information in an Anthropic Claude Code card.
    """
    w = 54
    scramble_str = f"{SEMANTIC_SUCCESS}Enabled{RESET}" if scrambler_enabled else f"{MUTED}Disabled{RESET}"
    user_str = f"{users_count} local user" if users_count == 1 else f"{users_count} local users"

    print(f"\n  {BORDER}╭─ {CORAL}EnDek System Information{BORDER} {'─' * (w - 29)}╮{RESET}")
    print(f"  {BORDER}│{RESET}  {MUTED}{'EnDek Core':<20}{RESET} {BORDER}│{RESET}  {CREAM}{version:<25}{RESET}  {BORDER}│{RESET}")
    print(f"  {BORDER}│{RESET}  {MUTED}{'CLI Interface':<20}{RESET} {BORDER}│{RESET}  {CREAM}{cli_version + ' (Claude Code Style)':<25}{RESET}  {BORDER}│{RESET}")
    print(f"  {BORDER}│{RESET}  {MUTED}{'Key Status':<20}{RESET} {BORDER}│{RESET}  {SEMANTIC_SUCCESS}{key_status:<25}{RESET}  {BORDER}│{RESET}")
    print(f"  {BORDER}│{RESET}  {MUTED}{'Registered Users':<20}{RESET} {BORDER}│{RESET}  {CREAM}{user_str:<25}{RESET}  {BORDER}│{RESET}")
    print(f"  {BORDER}│{RESET}  {MUTED}{'Scrambler Engine':<20}{RESET} {BORDER}│{RESET}  {scramble_str:<34}{RESET} {BORDER}│{RESET}")
    print(f"  {BORDER}╰{'─' * w}╯{RESET}\n")