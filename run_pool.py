from profile_models import Target, Person, Pet, GeneratorConfig
from engine import PasswordGenerator
from datetime import date


def main():
    # Simple config
    config = GeneratorConfig(
        min_length=4,
        max_length=16,
        enable_case_mutations=True,
        enable_reverse=True,
        leet_level=1,
        bruteforce_mode=True,
    )

    # Simple target with a couple of relations and keywords
    target = Target(
        name="Alice",
        nickname="ali",
        family_name="Wonder",
        birth_date=date(1992, 5, 15),
        professions=["dev"],
        special_keywords=["guitar", "coffee"],
    )

    # Optional relations
    partner = Person(name="Bob", nickname="bobby", family_name="Builder")
    child = Person(name="Charlie")
    pet = Pet(name="Milo")

    target.add_partner(partner)
    target.add_child(child)
    target.add_pet(pet)

    generator = PasswordGenerator(target, config)
    pool = generator._build_base_word_pool()

    total = sum(len(sub) for sub in pool)
    print(total) 
    print(pool)


if __name__ == "__main__":
    main()
