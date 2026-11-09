# 😀 Eva_test

Web interface for the volleyball blocking robot, running on an Arduino UNO Q.

## How it fits together

- `python/` runs on the UNO Q's Linux side. `main.py` starts the Flask website (`app.py`, `templates/index.html`) on port 5000.
- `sketch/` runs on the MCU and controls the robot.
- The two talk over the Arduino Bridge: the website calls `command` on the sketch (`PON`, `POFF`, `HOMEL`, `HOMER`, `KILL`, `MOVE,<height>,<length>,<speed>`, and `STATE` once a second for the Current state section), and the sketch reports speed readings with `Bridge.notify("speed", value)`.

## The page

1. **Function:** Power On, Power Off, Home Left, Home Right.
2. **Current state:** home side, height and length, as reported by the sketch's `STATE` reply.
3. **Position:** drag the arm block (or use the arrow keys) within the dashed limits, set the speed (0 to 1 ft/s), then Enter to send it or Save as drill. Limits live in `python/app.py` (`VERTICAL_MAX`, `HORIZONTAL_MAX`, `SPEED_MAX`).
4. **Drill:** saved positions. Select loads one into section 3 without moving the robot; Delete removes it.

## Run it

1. Open the app in Arduino App Lab and press Run.
2. On a device on the same network, open `http://<board-ip>:5000`.

Drills and speed records are stored in `python/data.db`, created on first start.

## Status

`sketch/sketch.ino` is a stub: it acknowledges every command but does not drive the robot yet. Replace the `TODO` markers with the motor and speed-sensor code.
