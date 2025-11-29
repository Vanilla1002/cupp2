from dataclasses import dataclass, field
from typing import List, Optional
from datetime import date
from utils import DateUtils

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

    
    
