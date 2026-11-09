# 😀 Eva_test

Web interface for the volleyball blocking robot, running on an Arduino UNO Q.

## How it fits together

- `python/` runs on the UNO Q's Linux side. `main.py` starts the Flask website (`app.py`, `templates/index.html`) on port 5000.
- `sketch/` runs on the MCU and controls the robot.
- The two talk over the Arduino Bridge: the website calls `command` on the sketch (`HOME`, `PON`, `POFF`, `KILL`, `PING`, `MOVE,<v>,<h>,<speed>`), and the sketch reports speed readings with `Bridge.notify("speed", value)`.

## Run it

1. Open the app in Arduino App Lab and press Run.
2. On a device on the same network, open `http://<board-ip>:5000`.

Drills and speed records are stored in `python/data.db`, created on first start.

## Status

`sketch/sketch.ino` is a stub: it acknowledges every command but does not drive the robot yet. Replace the `TODO` markers with the motor and speed-sensor code.
