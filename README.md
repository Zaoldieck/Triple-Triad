# Triple Triad

An unofficial recreation of the Triple Triad card game from Final Fantasy VIII, developed in Python with Pygame.

This project was created for educational purposes as a way to learn Python, game development, interface design, animations, save systems, and project organization.

## Download

A ready-to-play Windows build is available from the latest release.

### Windows installation

1. Download Triple-Triad-v1.0.0-Windows.zip.
2. Extract the entire archive.
3. Open the extracted Triple Triad folder.
4. Run Triple Triad.exe.

Python and Pygame are not required when using the Windows build.

## Features

- Complete Free Match mode
- Player deck and persistent card collection
- Card quantities and permanent card discovery
- Progressive card unlocking based on rarity
- Opponent hands balanced around the player's selected cards
- Automatic save system
- Keyboard and mouse support
- In-game Guide and Credits
- Animated menus, panels, card captures, and trades

## Match Rules

The game includes configurable rules such as:

- Open
- Random Hand
- Sudden Death
- Elemental
- Same
- Plus
- Wall
- Random Start

## Trade Rules

- One — The winner takes one selected card.
- Difference — The number of cards taken depends on the final score.
- Direct — Cards are exchanged according to their ownership when the match ends.
- All — The winner takes every opposing card.

## Card Progression

Rarity 1 cards are always available in unlimited quantities.

Cards of higher rarity must be obtained by playing Free Match. The opponent introduces missing cards progressively, requiring the player to complete the previous rarity before advancing to the next one.

Cards that are missing from the collection are displayed in blue with quantity x0 during the trade selection screen.

## Controls

- Arrow keys: Navigate
- Mouse wheel: Scroll
- Enter: Confirm
- Left mouse button: Confirm
- Escape: Go back
- Right mouse button: Go back

## Running from Source

### Requirements

Python 3.11 or newer
Pygame 2.6.1

Clone the repository:

git clone https://github.com/Zaoldieck/Triple-Triad.git
cd Triple-Triad

Create and activate a virtual environment:

python -m venv .venv

On Windows PowerShell:

.\.venv\Scripts\Activate.ps1

Install the required packages:

pip install -r requirements.txt

Run the game:

python main.py
## Save Data

Player progress is stored locally in:

saves/player_save.zao

The save file records owned card quantities and permanently discovered cards. Local save files are excluded from the repository.

## Project Status

Version v1.0.0 completes the planned Free Match experience, including gameplay rules, trade rules, card progression, collection management, animations, and a downloadable Windows build.

## Disclaimer

This is an unofficial, non-commercial fan recreation created for educational purposes.

This project is not affiliated with or endorsed by Square Enix.

FINAL FANTASY, TRIPLE TRIAD, and related names are trademarks of Square Enix.