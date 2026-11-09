// Volleyball blocking robot - MCU side.
//
// The website (python/app.py) sends one text command per Bridge call and
// expects a short text reply. Commands:
//   STATE                         -> "STATE,<L|R|N>,<height>,<length>"
//                                    home side (L, R or N = not set), then feet
//   HOMEL | HOMER                 -> "OK HOMEL" / "OK HOMER"
//   PON | POFF | KILL             -> "OK <cmd>"
//   MOVE,<height>,<length>,<speed>   (ft, ft, ft/s) -> "OK MOVE ..."
//   PING                          -> "PONG"
//
// Speed-sensor readings go the other way: Bridge.notify("speed", value).
//
// This is a STUB: it parses and acknowledges commands and reports the
// commanded position back as the "current" one, but does not drive any
// hardware yet. Look for the TODO markers.

#include <Arduino_RouterBridge.h>

const float LENGTH_MAX_FT = 12.0;  // keep in sync with HORIZONTAL_MAX in python/app.py

char  homeSide = 'N';  // 'L', 'R' or 'N' (not set)
float curHeight = 0, curLength = 0;  // TODO: report real positions (encoders / limit switches)
bool  powered = false;

String handleCommand(String cmd) {
  cmd.trim();

  if (cmd == "STATE") {
    return "STATE," + String(homeSide) + "," + String(curHeight, 2) + "," + String(curLength, 2);
  }
  if (cmd == "PING") return "PONG";

  if (cmd == "HOMEL") {
    homeSide = 'L';
    curLength = 0;
    // TODO: run the homing routine toward the left end
    return "OK HOMEL";
  }
  if (cmd == "HOMER") {
    homeSide = 'R';
    curLength = LENGTH_MAX_FT;
    // TODO: run the homing routine toward the right end
    return "OK HOMER";
  }
  if (cmd == "PON") {
    powered = true;
    // TODO: enable motor drivers
    return "OK PON";
  }
  if (cmd == "POFF") {
    powered = false;
    // TODO: disable motor drivers
    return "OK POFF";
  }
  if (cmd == "KILL") {
    powered = false;
    // TODO: emergency stop - cut motor power immediately
    return "OK KILL";
  }

  if (cmd.startsWith("MOVE,")) {
    int a = cmd.indexOf(',');
    int b = cmd.indexOf(',', a + 1);
    int c = cmd.indexOf(',', b + 1);
    if (a < 0 || b < 0 || c < 0) return "ERR MOVE format";
    float height = cmd.substring(a + 1, b).toFloat();
    float length = cmd.substring(b + 1, c).toFloat();
    float speed  = cmd.substring(c + 1).toFloat();
    // TODO: command the motors to (height, length) at speed, then let curHeight/curLength
    // follow the real position. The stub just pretends it arrived.
    curHeight = height;
    curLength = length;
    return "OK MOVE " + String(height, 2) + " " + String(length, 2) + " " + String(speed, 2);
  }

  return "ERR unknown command";
}

void setup() {
  Bridge.begin();
  Bridge.provide("command", handleCommand);
  // Note: handlers registered with provide() run on the Bridge thread. When you
  // add motor/pin control, consider Bridge.provide_safe() so they run in loop().
}

void loop() {
  // TODO: read the speed sensor and report each reading to the website:
  //   Bridge.notify("speed", speedValue);
}
