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

banner = r"""
   ______  __  __  ____    ____    ___ 
  / ____/ / / / / / __ \  / __ \  |__ \
 / /     / / / / / /_/ / / /_/ /  __/ /
/ /___  / /_/ / / ____/ / ____/  / __/ 
\____/  \____/ /_/     /_/      /____/ 
    """