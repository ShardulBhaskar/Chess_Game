♟ Chess vs AI (Tkinter + Stockfish)

A fully interactive Chess GUI application built using Python’s Tkinter library, featuring AI gameplay powered by the Stockfish engine.

This project allows users to play chess against an AI with multiple difficulty levels, clean UI design, and essential gameplay features like undo/redo and move tracking.

🚀 Features

🎮 Play against AI (Stockfish integration)
🎚 Multiple difficulty levels:
Beginner
Easy
Intermediate
Advanced
Expert

⚪ Choose to play as:
White
Black
Random

🔄 Undo / Redo moves
📜 Move history panel (SAN notation)
🎯 Legal move highlighting
♟ Pawn promotion (auto to Queen)
🔁 New game with settings selector
🏳 Resign / Offer draw options
🔍 Board flip (based on player color)
⚡ Fallback to random AI if Stockfish is unavailable

🖥 Tech Stack
Python
Tkinter (GUI)
python-chess
Stockfish Engine

⚙️ Installation

1. Clone the repository
git clone [https://github.com/your-username/chess-ai-tkinter.git](https://github.com/ShardulBhaskar/Chess_Game/blob/main/chess_game.py)
cd Chess_Game

2. Install dependencies
pip install python-chess

3. Install Stockfish (Recommended)
Download from: https://stockfishchess.org/download/

Add it to:
System PATH OR
Update path in code:

STOCKFISH_PATHS = ["stockfish","path_to_your_stockfish.exe"]

▶️ How to Run
python main.py

| Action       | Description                     |
| ------------ | ------------------------------- |
| Click piece  | Select piece                    |
| Click square | Move piece                      |
| Undo         | Undo last 2 moves (player + AI) |
| Redo         | Redo moves                      |
| New Game     | Restart with settings           |
| Resign       | End game                        |
| Draw         | Offer draw                      |

🧠 AI Logic
Uses Stockfish engine when available
Falls back to random move selection if engine fails
Difficulty is controlled via:
Search depth
Time per move

📌 Known Limitations
No advanced UI animations
Pawn promotion limited to Queen
No online multiplayer
Engine path may require manual setup

💡 Future Improvements
Add drag-and-drop movement
Multiple promotion choices
Sound effects & animations
Game save/load feature
Online multiplayer (WebSocket/Server)
Opening book integration

🤝 Contributing
Pull requests are welcome. For major changes, open an issue first.

📜 License
This project is open-source and available under the MIT License.
