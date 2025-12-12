from datetime import date
from typing import List


class DateUtils:
    @staticmethod
    def get_permutations(d: date) -> List[str]:
        if not d:
            return []
        return [
            str(d.year),                                    # 1990 (yyyy)
            str(d.year)[-2:],                               # 90 (yy)
            f"{d.day:02d}{d.month:02d}{d.year}",            # 15051990 (ddmmyyyy)
            f"{d.month:02d}{d.day:02d}{d.year}",            # 05151990 (US (mmddyyyy)) 
            f"{d.day:02d}{d.month:02d}{str(d.year)[-2:]}",  # 150590 (ddmmyy)
            f"{d.month:02d}{d.day:02d}{str(d.year)[-2:]}",  # 051590 (mmddyy)
            f"{d.day:02d}{d.month:02d}",                    # 1505 (ddmm)
            f"{d.month:02d}{d.day:02d}",                    # 0515 (mmdd)
            #room for more (ideas: dd.mm, dd-mm, mm/dd, etc.)
        ]
    

def estimate_file_size(password_count: int, min_len: int, max_len: int) -> str:
    if password_count == 0:
        return "0 KB"

    avg_length = (min_len + max_len) / 2
    
    total_bytes = password_count * (avg_length + 1)

    
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if total_bytes < 1024.0:
            return f"{total_bytes:.2f} {unit}"
        total_bytes /= 1024.0
    
    return f"{total_bytes:.2f} PB"

def number_to_human_readable(n: int) -> str:
    if n < 1_000:
        return str(n)
    elif n < 1_000_000:
        return f"{n / 1_000:.2f}K"
    elif n < 1_000_000_000:
        return f"{n / 1_000_000:.2f}M"
    else:
        return f"{n / 1_000_000_000:.2f}B"
        


banner = r"""
   ______  __  __  ____    ____    ___ 
  / ____/ / / / / / __ \  / __ \  |__ \
 / /     / / / / / /_/ / / /_/ /  __/ /
/ /___  / /_/ / / ____/ / ____/  / __/ 
\____/  \____/ /_/     /_/      /____/ 
    """