import itertools
from typing import Iterator, List
from profile_models import Target, GeneratorConfig
from utils import DateUtils

class PasswordGenerator:
    def __init__(self, target: Target, config: GeneratorConfig):
        self.target = target
        self.config = config

    def _is_valid_length(self, password: str) -> bool:
        return self.config.min_length <= len(password) <= self.config.max_length
    
    def _generate_leet(self, word: str) -> List[str]:
        if self.config.leet_level == 0:
            return [word]
        char_options = []
        for char in word:
            opts = {char} 
            lower_c = char.lower()
            
            if lower_c in self.config.leet_map:
                opts.update(self.config.leet_map[lower_c])
            
            if self.config.bruteforce_mode and len(word) <= self.config.word_leet_threshold: # to avoid combinatorial explosion
                opts.add(char.swapcase())
        
            char_options.append(list(opts))
        
        return ["".join(p) for p in itertools.product(*char_options)]
    
    def _apply_case_mutations(self, word: str) -> List[str]:
        if not self.config.enable_case_mutations:
            return [word]
        if self.config.bruteforce_mode:
            return [word] #already handled in leet generation
        options = [(char.lower(), char.upper()) for char in word]

        mutations = [''.join(chars) for chars in itertools.product(*options)]

        return list(mutations)
    
    def _apply_reverse(self, word: str) -> List[str]:
        if not self.config.enable_reverse:
            return [word]
        return [word[::-1]]
    
    def _build_base_word_pool(self) -> List[List[str]]:
        raw_keywords = set(self.target.get_keywords())
        for relation in self.target.parents + self.target.children + self.target.partners + self.target.pets:
            raw_keywords.update(relation.get_keywords())

        raw_keywords.update(self.target.special_keywords)

        all_keyword_variants = []   
        for keyword in raw_keywords:
            case_forms = set(self._generate_leet(keyword))
            case_forms.update(self._apply_case_mutations(keyword))

            reversed_forms = set(
                itertools.chain.from_iterable(self._apply_reverse(cf) for cf in case_forms)
            )
            case_forms.update(reversed_forms)

            all_keyword_variants.append(list(case_forms))

        return all_keyword_variants
    
    def _dates_pool(self) -> List[str]:
        date_permutations = []
        if self.target.birth_date:
            date_permutations.extend(self.target.get_date_permutations())
        for relation in self.target.parents + self.target.children + self.target.partners:
            if relation.birth_date:
                date_permutations.extend(relation.get_date_permutations())
        for special_date in self.target.special_dates:
            date_permutations.extend(DateUtils.get_permutations(special_date))
        return date_permutations
    
    def _numbers_pool(self) -> List[str]:
        return self.target.special_numbers
    
    def generate_passwords(self) -> Iterator[str]:
        return