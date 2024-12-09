# doom-game

## Description:
Using pygame, I've created an FPS game similar to Doom. The game generates maze-like maps and uses a raycasting algorithm to render walls based on the player's FOV. Players can move around the map and turn around to shoot enemies, which can be taken down with a few shots. They are dynamically spawned using a circular queue. The game displays walls, a sky background, and enemies, with the player moving and acting using keyboard controls. The goal is to explore the maze and eliminate the enemies.


## Simple Controls:
- W and S to move (W forward & S backward)
- A and D to rotate (A left & D right)
- Space to shoot!

## To run:

Clone using the web URL (https://github.com/Swarsin/doom-game.git)
```javascript
git clone https://github.com/Swarsin/doom-game.git
```

Change directory into Connect-4-Game folder
```javascript
cd doom-game/
```
(In a virtual environment) install the libraries in requirements.txt
```javascript
pip install -r requirements.txt
```
Run game.py
```javascript
python main.py
```
