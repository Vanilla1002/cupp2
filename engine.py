import itertools
from logging import config
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
            
        
            char_options.append(list(opts))
        
        return ["".join(p) for p in itertools.product(*char_options)]
    
    def _apply_case_mutations(self, word: str) -> List[str]:
        if not self.config.enable_case_mutations:
            return [word]
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

        if self.target.name:
            raw_keywords.add(self.target.name[0:1].lower())
            raw_keywords.add(self.target.name[0:1].upper())
        if self.target.family_name:
            raw_keywords.add(self.target.family_name[0:1].lower())
            raw_keywords.add(self.target.family_name[0:1].upper())
        
        raw_keywords.update(self.target.special_keywords)
        all_keyword_variants = []   
        for keyword in raw_keywords:
            case_forms = set(self._generate_leet(keyword))
            case_forms.update(self._apply_case_mutations(keyword))
            if self.config.bruteforce_mode:
                reversed_forms = set(
                    itertools.chain.from_iterable(self._apply_reverse(cf) for cf in case_forms)
                )
                case_forms.update(reversed_forms)
            else:
                case_forms.update(self._apply_reverse(keyword))
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
        keyword_pools = self._build_base_word_pool()
        flat_keywords = set(itertools.chain.from_iterable(keyword_pools))
        date_pool = set(self._dates_pool())
        number_pool = set(self._numbers_pool())
        if self.config.add_common_numbers:
            number_pool.update(self.config.common_numbers)
        specials = self.config.special_chars if self.config.add_special_chars else ['']
        separators = self.config.separators

        # Max passwords cap
        limit = self.config.max_passwords if self.config.max_passwords is not None and self.config.max_passwords > 0 else None
        count = 0

        #strategy 1: single keywords
        for k in (flat_keywords | number_pool | date_pool):
            if limit is not None and count >= limit:
                return
            if self._is_valid_length(k):
                count += 1
                yield k
        
        #strategy 2: keyword + suffix combinations
        suffixes = number_pool.union(date_pool)
        for k, sep, suf in itertools.product(flat_keywords, separators, suffixes):
            if limit is not None and count >= limit:
                return
            password = f"{k}{sep}{suf}" # keyword+separator+suffix example: ali&1992 ,ali1992
            if self._is_valid_length(password):
                count += 1
                yield password
            password = f"{suf}{sep}{k}" # suffix+separator+keyword example: 1992&ali ,1992ali
            if self._is_valid_length(password):
                count += 1
                yield password
            
            #strategy 3: strategy 2 with special chars
            if self.config.add_special_chars:
                for special in specials:
                    if limit is not None and count >= limit:
                        return
                    password = f"{k}{sep}{suf}{special}" # keyword+separator+suffix+special example: ali&1992!
                    if self._is_valid_length(password):
                        count += 1
                        yield password
                    password = f"{special}{k}{sep}{suf}" # special+keyword+separator+suffix example: !ali&1992
                    if self._is_valid_length(password):
                        count += 1
                        yield password
                    password = f"{suf}{sep}{k}{special}" # suffix+separator+keyword+special example: 1992&ali!
                    if self._is_valid_length(password):
                        count += 1
                        yield password
                    password = f"{special}{suf}{sep}{k}" # special+suffix+separator+keyword example: !1992&ali
                    if self._is_valid_length(password):
                        count += 1
                        yield password

        #strategy 4: keyword + special
        if self.config.add_special_chars:
            for k, special in itertools.product(flat_keywords, specials):
                if limit is not None and count >= limit:
                    return
                password = f"{k}{special}" # keyword+special example: ali!
                if self._is_valid_length(password):
                    count += 1
                    yield password
                password = f"{special}{k}" # special+keyword example: !ali
                if self._is_valid_length(password):
                    count += 1
                    yield password

        # strategy 5: Multi-Word Combinations
        if self.config.max_combination_depth >= 2:
            for group_a, group_b in itertools.permutations(keyword_pools, 2):
                for word_a, word_b in itertools.product(group_a, group_b):
                    for sep in separators:
                        # Base: wordA+separator+wordB example: ali&Wonder
                        password = f"{word_a}{sep}{word_b}"
                        if self._is_valid_length(password):
                            count += 1
                            if limit is not None and count > limit:
                                return
                            yield password

                        # strategy 6: Multi-Word Combinations with suffix (and special chars)
                        if self.config.max_combination_depth >= 3:
                            for suff in suffixes:
                               
                                suffix_variations = [
                                    f"{word_a}{sep}{word_b}{suff}", # wordA+separator+wordB+suffix example: ali&Wonder1992
                                    f"{suff}{word_a}{sep}{word_b}", # suffix+wordA+separator+wordB example: 1992ali&Wonder
                                    f"{word_a}{suff}{sep}{word_b}", # wordA+suffix+separator+wordB example: ali1992&Wonder
                                ]

                                # Add separator-dependent variation if separator exists
                                if sep:
                                    suffix_variations.append(f"{word_a}{sep}{suff}{word_b}") # wordA+separator+suffix+wordB example: ali&1992Wonder

                                # Optimization: If the basic structure is too long, skip all variations for this suffix
                                if not self._is_valid_length(suffix_variations[0]):
                                    continue 
                                
                                for p in suffix_variations:
                                    count += 1
                                    if limit is not None and count > limit:
                                        return
                                    yield p

                                # --- Suffix + Special Char Combinations ---
                                if self.config.add_special_chars:
                                    for special in specials:
                                        # Pre-check length to save processing time (commutative length check)
                                        test_len = f"{word_a}{sep}{word_b}{suff}{special}"
                                        if not self._is_valid_length(test_len):
                                            continue
                                        
                                        # Define all patterns in exact order
                                        special_variations = [
                                            # 1. Both at Ends (Split)
                                            f"{suff}{word_a}{sep}{word_b}{special}", # suffix+wordA+separator+wordB+special example: 1992ali&Wonder!
                                            f"{special}{word_a}{sep}{word_b}{suff}", # special+wordA+separator+wordB+suffix example: !ali&Wonder1992

                                            # 2. Both at End (Combined)
                                            f"{word_a}{sep}{word_b}{suff}{special}", # wordA+separator+wordB+suffix+special example: ali&Wonder1992!
                                            f"{word_a}{sep}{word_b}{special}{suff}", # wordA+separator+wordB+special+suffix example: ali&Wonder!1992

                                            # 3. Both at Start (Combined)
                                            f"{special}{suff}{word_a}{sep}{word_b}", # special+suffix+wordA+separator+wordB example: !1992ali&Wonder
                                            f"{suff}{special}{word_a}{sep}{word_b}", # suffix+special+wordA+separator+wordB example: 1992!ali&Wonder

                                            # 4. Middle Injections (One Middle, One End/Start)
                                            f"{word_a}{suff}{sep}{word_b}{special}", # wordA+suffix+separator+wordB+special example: ali1992&Wonder!
                                            f"{word_a}{special}{sep}{word_b}{suff}", # wordA+special+separator+wordB+suffix example: ali!&Wonder1992
                                            f"{special}{word_a}{suff}{sep}{word_b}", # special+wordA+suffix+separator+wordB example: !ali1992&Wonder
                                            f"{suff}{word_a}{special}{sep}{word_b}", # suffix+wordA+special+separator+wordB example: 1992ali!&Wonder
                                        ]

                                        # 5. Separator Dependent (Inside Insertions)
                                        if sep:
                                            special_variations.extend([
                                                f"{word_a}{sep}{suff}{word_b}{special}", # wordA+separator+suffix+wordB+special example: ali&1992Wonder!
                                                f"{word_a}{sep}{special}{word_b}{suff}", # wordA+separator+special+wordB+suffix example: ali&!Wonder1992
                                                f"{special}{word_a}{sep}{suff}{word_b}", # special+wordA+separator+suffix+wordB example: !ali&1992Wonder
                                                f"{suff}{word_a}{sep}{special}{word_b}", # suffix+wordA+separator+special+wordB example: 1992ali&!Wonder
                                            ])

                                        # Yield all generated variations (length checked via test_len optimization)
                                        for p in special_variations:
                                            count += 1
                                            if limit is not None and count > limit:
                                                return
                                            yield p  
    def estimate_password_count(self) -> int:
        keyword_pools = self._build_base_word_pool()
        flat_keywords = set(itertools.chain.from_iterable(keyword_pools))
        len_keywords = len(flat_keywords)

        date_pool = set(self._dates_pool())
        number_pool = set(self._numbers_pool())
        if self.config.add_common_numbers:
            number_pool.update(self.config.common_numbers)
        len_suf = len(number_pool)

        separators = self.config.separators
        len_separators = len(separators) if separators else 1  

        if self.config.add_special_chars:
            len_specials = len(self.config.special_chars)
        else:
            len_specials = 0
        
        len_pairs = 0
        if self.config.max_combination_depth >= 2:
            for group_a, group_b in itertools.permutations(keyword_pools, 2):
                len_pairs += len(group_a) * len(group_b)
            
        total_count = 0

        total_count += len_keywords  # Single keywords
        total_count += 2 * len_keywords * len_separators * len_suf  # Keyword + Suffix combinations
        total_count += 4 * len_keywords * len_separators * len_suf * len_specials  # Strategy 3 variations 
        total_count += 2 * len_keywords * len_specials  # Keyword + Special combinations

        if self.config.max_combination_depth >= 2:

            total_count += len_pairs * len_separators  # Multi-Word Combinations

            if self.config.max_combination_depth >= 3:
                vars_per_suffix = (3 * len_separators) + (len_separators - 1) # Base variations
                total_count += len_pairs * len_suf * vars_per_suffix  # Strategy 6 base variations

                if len_specials > 0:
                    vars_per_special = (10 * len_separators) + (4 * (len_separators - 1))  # Special variations 
                    total_count += len_pairs * len_suf * len_specials * vars_per_special  # Strategy 6 special variations
        return total_count