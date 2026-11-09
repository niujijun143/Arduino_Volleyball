// Volleyball blocking robot - MCU side.
//
// The website (python/app.py) sends one text command per Bridge call and
// expects a short text reply. Commands:
//   PING                          -> "PONG"
//   HOME | PON | POFF | KILL      -> "OK <cmd>"
//   MOVE,<vertical>,<horizontal>,<speed>   (ft, ft, ft/s) -> "OK MOVE ..."
//
// Speed-sensor readings go the other way: Bridge.notify("speed", value).
//
// This is a STUB: it parses and acknowledges commands but does not drive any
// hardware yet. Look for the TODO markers.

#include <Arduino_RouterBridge.h>

float targetVertical = 0, targetHorizontal = 0, targetSpeed = 0;
bool powered = false;

String handleCommand(String cmd) {
  cmd.trim();

  if (cmd == "PING") return "PONG";

  if (cmd == "HOME") {
    // TODO: run the homing routine
    return "OK HOME";
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
    targetVertical   = cmd.substring(a + 1, b).toFloat();
    targetHorizontal = cmd.substring(b + 1, c).toFloat();
    targetSpeed      = cmd.substring(c + 1).toFloat();
    // TODO: command the motors to (targetVertical, targetHorizontal) at targetSpeed
    return "OK MOVE " + String(targetVertical, 2) + " " + String(targetHorizontal, 2) + " " + String(targetSpeed, 2);
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
