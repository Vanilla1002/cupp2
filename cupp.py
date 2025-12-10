#cli file
from profile_models import GeneratorConfig, Target
from profile_models import Person, Pet
from engine import PasswordGenerator
from utils import banner
from datetime import date
import argparse
from typing import Optional, List
import sys

def _ask(prompt: str, default: Optional[str] = None) -> str:
    p = f"{prompt}"
    if default:
        p += f" [{default}]"
    p += ": "
    ans = input(p).strip()
    return ans or (default or "")

def _ask_yes_no(prompt: str, default: bool = False) -> bool:
    d = "y" if default else "n"
    while True:
        ans = input(f"{prompt} (y/n) [{d}]: ").strip().lower()
        if ans == "":
            return default
        if ans in ("y", "yes"):
            return True
        if ans in ("n", "no"):
            return False
        print("Please answer y or n.")

def _ask_list(prompt: str) -> List[str]:
    print(f"{prompt} (enter one per line; blank to finish)")
    items: List[str] = []
    while True:
        v = input("- ").strip()
        if not v:
            break
        items.append(v)
    return items

def _sanitize_numbers(items: List[str]) -> List[str]:
    cleaned: List[str] = []
    seen = set()
    for raw in items:
        digits = ''.join(ch for ch in raw if ch.isdigit())
        if not digits or digits in seen:
            continue
        seen.add(digits)
        cleaned.append(digits)
    return cleaned

def parse_date(date_str: str):
    # the input should be 8 digits, (month and day placed before year)
    if len(date_str) != 8 or not date_str.isdigit():
        raise argparse.ArgumentTypeError("Date must be in MMDDYYYY or DDMMYYYY format")
    month = int(date_str[0:2])
    day = int(date_str[2:4])
    year = int(date_str[4:8])
    
    return date(year, month, day)

def _ask_date(prompt: str) -> Optional[date]:
    while True:
        s = _ask(prompt + " (DDMMYYYY, blank to skip)").strip()
        if not s:
            return None
        if len(s) != 8 or not s.isdigit():
            print("Date must be exactly 8 digits (MMDDYYYY or DDMMYYYY). Please try again or leave blank to skip.")
            continue
        try:
            dd = int(s[0:2]); mm = int(s[2:4]); yyyy = int(s[4:8])
            try:
                return date(yyyy, mm, dd)
            except ValueError:
                return date(yyyy, dd, mm)       
        except Exception:
            print("Invalid date value. Please try again or leave blank to skip.")
            continue

def _collect_person(label: str) -> Person:
    print(f"\n{label} details:")
    name = _ask("First name") 
    family_name = _ask("Family/last name") or None
    nickname = _ask("Nickname") or None
    birth = _ask_date("Birth date")
    id_num = _ask("ID number ") or None
    professions = _ask_list("Professions (one per line; blank to finish)")
    return Person(
        name=name,
        family_name=family_name,
        nickname=nickname,
        birth_date=birth,
        id_number=id_num,
        professions=professions,
    )

def _collect_people(section_label: str) -> List[Person]:
    print(f"\n{section_label} — add entries")
    people: List[Person] = []
    while _ask_yes_no("Add one?", False):
        people.append(_collect_person(section_label[:-1] if section_label.endswith('s') else section_label))
    return people

def _collect_pet() -> Pet:
    print("\nPet details:")
    name = _ask("Pet name")
    nickname = _ask("Pet nickname") or None
    return Pet(name=name, nickname=nickname)

def _collect_pets() -> List[Pet]:
    print("\nPets — add entries")
    pets: List[Pet] = []
    while _ask_yes_no("Add a pet?", False):
        pets.append(_collect_pet())
    return pets

def run_interactive(cfg: Optional[GeneratorConfig] = None):
    print("Interactive mode: answer the following about your target.\n")
    print("blank entries will be skipped\n")
    print("---------------------------------\n")
    
    # Core identity (use person collector)
    target_person = _collect_person("Target")

    # Relations
    parents = _collect_people("Parents")
    partners = _collect_people("Partners")
    children = _collect_people("Children")
    pets = _collect_pets()

    # Specials
    special_keywords = _ask_list("Special keywords (hobbies, company, interests)")
    special_numbers = _ask_list("Special numbers (IDs, phone fragments)")
    special_numbers = _sanitize_numbers(special_numbers)

    print("Special dates (anniversaries, memorable) — optional")
    special_dates: List[date] = []
    while _ask_yes_no("Add a special date?", False):
        d = _ask_date("Date (MMDDYYYY)")
        if d:
            special_dates.append(d)

    # Config: use provided cfg or load from file by default
    cfg = cfg or GeneratorConfig.from_file()

    target = Target(
        name=target_person.name,
        nickname=target_person.nickname,
        family_name=target_person.family_name,
        birth_date=target_person.birth_date,
        id_number=target_person.id_number,
        professions=target_person.professions,
        parents=parents,
        partners=partners,
        children=children,
        pets=pets,
        special_keywords=special_keywords,
        special_dates=special_dates,
        special_numbers=special_numbers,
    )

    gen = PasswordGenerator(target, cfg)
    print("\nGenerated passwords:\n")
    count = 0
    for pw in gen.generate_passwords():
        print(pw)
        count += 1
    print(f"\nTotal: {count}")

def _build_config_from_args(args) -> GeneratorConfig:
    """Load config from file and apply overrides from CLI args (only used with -i)."""
    cfg = GeneratorConfig.from_file()
    # Apply overrides if provided
    if getattr(args, "min_length", None) is not None:
        cfg.min_length = args.min_length
    if getattr(args, "max_length", None) is not None:
        cfg.max_length = args.max_length
    if getattr(args, "max_passwords", None) is not None:
        cfg.max_passwords = args.max_passwords
    if getattr(args, "leet_level", None) is not None:
        cfg.leet_level = args.leet_level
    if getattr(args, "no_case_mutations", False):
        cfg.enable_case_mutations = False
    if getattr(args, "no_reverse", False):
        cfg.enable_reverse = False
    if getattr(args, "no_special_chars", False):
        cfg.add_special_chars = False
    if getattr(args, "separators", None):
        cfg.separators = [s.strip() for s in args.separators.split(',') if s.strip() != '']
    if getattr(args, "max_depth", None) is not None:
        cfg.max_combination_depth = args.max_depth
    if getattr(args, "no_common_numbers", False):
        cfg.add_common_numbers = False
    if getattr(args, "bruteforce", False):
        cfg.bruteforce_mode = True
    return cfg

def _run_interactive_with_overrides(args):
    """Run interactive flow using config built from args; affects only -i path."""
    cfg = _build_config_from_args(args)
    run_interactive(cfg)

def main():
    parser = argparse.ArgumentParser(
        description=banner,
        formatter_class=argparse.RawTextHelpFormatter,
        add_help=False  
    )

    # --- Group 1: Main Execution Modes ---
    mode_group = parser.add_argument_group("  Execution Mode")
    mode_group.add_argument("-h", "--help", action="help", help="Show this help message and exit")
    mode_group.add_argument("-i", "--interactive", action="store_true", help="Start the interactive generation wizard")

    # --- Group 2: Configuration Overrides ---
    config_group = parser.add_argument_group(
        "  Configuration Overrides", 
        "  (Optional flags to customize generation behavior when using -i)"
    )
    
    config_group.add_argument("--min-length", type=int, metavar="N", help="Set minimum password length")
    config_group.add_argument("--max-length", type=int, metavar="N", help="Set maximum password length")
    config_group.add_argument("--max-passwords", type=int, metavar="N", help="Limit number of passwords generated")
    config_group.add_argument("--leet-level", type=int, choices=[0,1,2], metavar="LVL", help="Leet substitution level (0, 1, or 2)")
    config_group.add_argument("--max-depth", type=int, metavar="N", help="Max combination depth (e.g., 2 or 3)")
    config_group.add_argument("--separators", type=str, metavar="CHARS", help="Comma-separated separators (e.g. ',-,_,!')")
    
    # Boolean flags
    config_group.add_argument("--bruteforce", action="store_true", help="Enable bruteforce mode (creates more variants)")
    config_group.add_argument("--no-case-mutations", action="store_true", help="Disable case mutations (Capitalization)")
    config_group.add_argument("--no-reverse", action="store_true", help="Disable reverse mutations")
    config_group.add_argument("--no-special-chars", action="store_true", help="Disable special characters")
    config_group.add_argument("--no-common-numbers", action="store_true", help="Disable appending common numbers")

    if len(sys.argv) == 1:
        parser.print_help(sys.stderr)
        sys.exit(1)

    args = parser.parse_args()

    if args.interactive:
        _run_interactive_with_overrides(args)
    else:
        # If user provides flags but forgets -i, we can hint them or just show help
        parser.print_help()

if __name__ == "__main__":
    main()