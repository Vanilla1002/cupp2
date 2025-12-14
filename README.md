# CUPP 2 - Common User Passwords Profiler
```
   ______  __  __  ____    ____    ___ 
  / ____/ / / / / / __ \  / __ \  |__ \
 / /     / / / / / /_/ / / /_/ /  __/ /
/ /___  / /_/ / / ____/ / ____/  / __/ 
\____/  \____/ /_/     /_/      /____/ 
```

**An enhanced, modular version of the classic [CUPP](https://github.com/Mebus/cupp) tool.**

This project builds upon the original concept of profiling users to generate password lists but has been completely refactored to be easier to maintain, fork, and edit. It also introduces more powerful algorithms for generating possible password combinations.

## Key Improvements

- **Modular Architecture:** The code has been split into logical components (`engine.py`, `profile_models.py`, `utils.py`), making it much easier for developers to understand and extend.
-  **Enhanced Generation Logic:**
      * **Multi-Word Combinations:** Supports combining keywords (e.g., `PartnerName` + `PetName`) with configurable depth.
      * **Smart Suffixing:** Intelligently appends dates and separators based on profile data.
      * **Estimated Output:** Calculates the estimated file size and password count *before* generation to prevent disk overflow.
- **Modern Configuration:** Replaced the old `.cfg` format with a standard `config.json` for easier settings management.
- **Developer Friendly:** Built specifically to be forked and customized.

## About

The most common form of authentication is the combination of a username and a password or passphrase. A weak password often relates to the user's personal information, such as birthdays, nicknames, addresses, names of pets or relatives, or common words.

CUPP 2 allows you to profile a target interactively and generate a wordlist tailored specifically to them, which is often far more effective than generic dictionary attacks.

## Requirements

- Python 3.x

## Installation

```bash
git clone https://github.com/Vanilla1002/cupp2.git
cd cupp2
```

## Usage

Run the main script to see the available options:

```bash
python3 cupp.py -h
```

### Interactive Mode
To start an interactive session to profile a target:

```bash
python3 cupp.py -i
```

## Project Structure

- **`cupp.py`**: The main entry point and CLI handler.
- **`engine.py`**: Core logic for password generation algorithms.
- **`profile_models.py`**: Data structures defining how user profiles are stored.
- **`utils.py`**: Helper functions.
- **`config.json`**: Configuration settings for the tool.
- **`run_pool.py`**: Multiprocessing/threading helpers.

## License

This program is free software; you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation; either version 3 of the License, or any later version.

## Credits & Acknowledgements

This project is a improvement of [Mebus/cupp](https://github.com/Mebus/cupp).

**Original Authors:**
- Muris Kurgas aka j0rgan
- Mebus
