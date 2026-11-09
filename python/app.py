"""Volleyball blocking robot - web interface (Flask).

Runs on the UNO Q's Linux side and talks to the robot sketch on the MCU
through the Arduino Bridge. main.py wires the Bridge in with link.attach().

Bridge contract with sketch/sketch.ino:
  Python -> MCU   Bridge.call("command", "<text>")   returns the MCU's reply string
                    PON | POFF | HOMEL | HOMER | KILL
                    MOVE,<height>,<length>,<speed>
                    STATE  ->  "STATE,<L|R|N>,<height>,<length>"
                              (home side L/R or N = not set; feet)
  MCU -> Python   Bridge.notify("speed", <float>)    one speed-sensor reading
"""
import sqlite3
import threading
import time
from pathlib import Path

from flask import Flask, jsonify, render_template, request

DB = str(Path(__file__).resolve().parent / "data.db")  # created on first start
POLL_EVERY = 1.0  # seconds between state/link checks

# Travel limits. The page maps the drag area onto these (most down / most left = 0).
VERTICAL_MAX = 11.0    # ft, height of the arm block
HORIZONTAL_MAX = 12.0  # ft, length along the rail
SPEED_MAX = 1.0        # ft/s

COMMANDS = {
    "on": "PON",
    "off": "POFF",
    "home-left": "HOMEL",
    "home-right": "HOMER",
    "kill": "KILL",
}

app = Flask(__name__)


def db():
    con = sqlite3.connect(DB)
    con.row_factory = sqlite3.Row
    return con


def init_db():
    with db() as con:
        con.execute("""CREATE TABLE IF NOT EXISTS drills (
            id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT NOT NULL,
            vertical REAL, horizontal REAL, speed REAL)""")
        con.execute("""CREATE TABLE IF NOT EXISTS speed_records (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            ts TEXT DEFAULT (datetime('now','localtime')), speed REAL)""")


class McuLink:
    """Talks to the sketch over the Bridge, stores speed readings, tracks the robot state.

    A background thread asks the MCU for its state every POLL_EVERY seconds, which also
    tells us whether the MCU is reachable.
    """

    def __init__(self):
        self.bridge = None
        self.connected = False
        self.last_reply = "no data yet"
        self.state = {"home": None, "height": None, "length": None}
        self.lock = threading.Lock()  # one Bridge call at a time

    def attach(self, bridge):
        """Register for speed readings from the MCU and start the state polling."""
        self.bridge = bridge
        bridge.provide("speed", self.on_speed)
        threading.Thread(target=self._poll_loop, daemon=True).start()

    def on_speed(self, value):
        try:
            value = float(value)
        except (TypeError, ValueError):
            return
        with db() as con:
            con.execute("INSERT INTO speed_records (speed) VALUES (?)", (value,))

    def _call(self, cmd):
        """Send one command. Returns (answered, reply)."""
        if self.bridge is None:
            return False, None
        with self.lock:
            try:
                reply = self.bridge.call("command", cmd)
            except Exception as e:  # Bridge raises on timeout / MCU not running
                self.connected = False
                self.last_reply = f"bridge error: {e}"
                return False, None
        self.connected = True
        if cmd == "STATE":
            self._parse_state(reply)
        else:
            self.last_reply = str(reply)
        return True, reply

    def _parse_state(self, reply):
        parts = str(reply).split(",")
        if len(parts) != 4 or parts[0] != "STATE":
            return
        try:
            height, length = float(parts[2]), float(parts[3])
        except ValueError:
            return
        self.state = {"home": {"L": "left", "R": "right"}.get(parts[1]),
                      "height": height, "length": length}

    def _poll_loop(self):
        while True:
            self._call("STATE")
            time.sleep(POLL_EVERY)

    def send(self, cmd):
        return self._call(cmd)[0]


link = McuLink()


def valid_move(d):
    try:
        v, h, s = float(d["vertical"]), float(d["horizontal"]), float(d["speed"])
    except (KeyError, TypeError, ValueError):
        return None
    if not (0 <= v <= VERTICAL_MAX and 0 <= h <= HORIZONTAL_MAX and 0 <= s <= SPEED_MAX):
        return None
    return v, h, s


@app.route("/")
def index():
    return render_template("index.html")


@app.get("/api/config")
def config():
    return jsonify(vertical_max=VERTICAL_MAX, horizontal_max=HORIZONTAL_MAX, speed_max=SPEED_MAX)


@app.post("/api/cmd/<name>")
def cmd(name):
    if name not in COMMANDS:
        return jsonify(ok=False, error="bad command"), 400
    return jsonify(ok=link.send(COMMANDS[name]))


@app.post("/api/move")
def move():
    mv = valid_move(request.get_json(force=True))
    if not mv:
        return jsonify(ok=False, error="out of range"), 400
    return jsonify(ok=link.send("MOVE,%.2f,%.2f,%.2f" % mv))


@app.get("/api/status")
def status():
    return jsonify(reply=link.last_reply, connected=link.connected, **link.state)


@app.get("/api/drills")
def drills():
    with db() as con:
        return jsonify([dict(r) for r in con.execute("SELECT * FROM drills ORDER BY id DESC")])


@app.post("/api/drills")
def save_drill():
    d = request.get_json(force=True)
    mv = valid_move(d)
    name = (d.get("name") or "").strip()
    if not mv or not name:
        return jsonify(ok=False, error="name or values invalid"), 400
    with db() as con:
        con.execute("INSERT INTO drills (name,vertical,horizontal,speed) VALUES (?,?,?,?)",
                    (name, *mv))
    return jsonify(ok=True)


@app.post("/api/drills/<int:did>/enter")
def enter_drill(did):
    with db() as con:
        r = con.execute("SELECT * FROM drills WHERE id=?", (did,)).fetchone()
    if not r:
        return jsonify(ok=False, error="not found"), 404
    return jsonify(ok=link.send("MOVE,%.2f,%.2f,%.2f" % (r["vertical"], r["horizontal"], r["speed"])))


@app.delete("/api/drills/<int:did>")
def delete_drill(did):
    with db() as con:
        con.execute("DELETE FROM drills WHERE id=?", (did,))
    return jsonify(ok=True)


@app.get("/api/speed")
def speed():
    with db() as con:
        rows = con.execute("SELECT ts, speed FROM speed_records ORDER BY id DESC LIMIT 30")
        return jsonify([dict(r) for r in rows])
