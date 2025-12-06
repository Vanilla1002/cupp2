from dataclasses import dataclass, field
from typing import List, Optional
from datetime import date
from utils import DateUtils

@dataclass
class GeneratorConfig:
    min_length: int = 6
    max_length: int = 20

    enable_case_mutations: bool = True
    enable_reverse: bool = True

    leet_level: int = 1 # 0 = none, 1 = low, 2 = medium
    leet_map: dict = field(default_factory=lambda: {
        'a': ['4', '@'], 'e': ['3'], 'i': ['1', '!'], 'o': ['0'], 's': ['5', '$'], 't': ['7']
    })

    max_combination_depth: int = 2

    add_special_chars: bool = True
    special_chars: List[str] = field(default_factory=lambda: ['!', '@', '#', '$', '%', '?'])

    separators: List[str] = field(default_factory=lambda: ['', '.', '_', '-', '!', "and", '&', "+", "xoxo", "1", "lol", "XD"])

    add_common_numbers: bool = True
    common_numbers: List[str] = field(default_factory=lambda: [
        '123', '1234', '12345', '007', '69', '420', '666', '777', '888', '999', '111', '000', '1', '12', '123456', '123456789', '0', '01', '21', '11', '13', '19', '20', '2000', '2010', '2020' , '2468', '1357', '69', '420', '911', '67', '88', '246'
    ])

    
    word_leet_threshold: int = 12  # max length for applying leet transformations

    bruteforce_mode: bool = False

    max_passwords: Optional[int] = 1000000000  # 100 million by default, None for unlimited 


    def __post_init__(self):
        if self.min_length > self.max_length:
            raise ValueError(f"Min length ({self.min_length}) cannot be greater than max length ({self.max_length})")
        
        if self.leet_level not in [0, 1, 2]:
            raise ValueError("Leet level must be 0, 1, or 2")
        
        if self.max_passwords is not None and self.max_passwords < 0:
            raise ValueError("max_passwords must be >= 0 when specified")




@dataclass
class BaseEntity:
    name : str
    nickname : Optional[str] = None

    def get_keywords(self) -> List[str]:
        keywords = [self.name]
        if self.nickname:
            keywords.append(self.nickname)
        return [w for w in keywords if w]


@dataclass
class Pet(BaseEntity):
    pass


@dataclass
class Person(BaseEntity):
    family_name: Optional[str] = None
    birth_date: Optional[date] = None
    id_number: Optional[str] = None
    professions: List[str] = field(default_factory=list)

    def get_keywords(self) -> List[str]:
        keywords = super().get_keywords()
        if self.family_name:
            keywords.append(self.family_name)
        return [w for w in keywords if w]
    
    def get_date_permutations(self) -> List[str]:
        return DateUtils.get_permutations(self.birth_date)    
        
@dataclass
class Target(Person):
    partners : List[Person] = field(default_factory=list)
    parents : List[Person] = field(default_factory=list)
    children : List[Person] = field(default_factory=list)
    pets : List[Pet] = field(default_factory=list)
    special_keywords : List[str] = field(default_factory=list)
    special_dates : List[date] = field(default_factory=list)
    special_numbers : List[str] = field(default_factory=list)

    def add_partner(self, partner: Person):
        self.partners.append(partner)
    def add_child(self, child: Person):
        self.children.append(child)
    def add_pet(self, pet: Pet):
        self.pets.append(pet)
    
    def get_all_special_date_permutations(self) -> List[str]:
        perms = []
        for d in self.special_dates:
            perms.extend(DateUtils.get_permutations(d))
        return list(set(perms))

    
    
