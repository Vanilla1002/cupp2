#cli file
from profile_models import GeneratorConfig, Target
from profile_models import Person, Pet
from engine import PasswordGenerator
from datetime import date
import argparse
from typing import Optional, List

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
            mm = int(s[0:2]); dd = int(s[2:4]); yyyy = int(s[4:8])
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

def run_interactive():
    print("Interactive mode: answer the following about your target.")
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

    # Config (use sensible defaults, ask for max length/count)

    cfg = GeneratorConfig()

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

def main():
    parser = argparse.ArgumentParser(description="CUPP2 — Contextual password generator")
    parser.add_argument("-i", "--interactive", action="store_true", help="Run interactive CLI prompts")
    args = parser.parse_args()

    if args.interactive:
        run_interactive()
    else:
        parser.print_help()

if __name__ == "__main__":
    main()


