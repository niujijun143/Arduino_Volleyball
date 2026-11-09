import threading
import time

from arduino.app_utils import App, Bridge

from app import app as flask_app, init_db, link

PORT = 5000  # must match "ports" in app.yaml

# Website: database, Bridge link to the sketch, then Flask in a background thread.
init_db()
link.attach(Bridge)
threading.Thread(
    target=lambda: flask_app.run(host="0.0.0.0", port=PORT, threaded=True),
    daemon=True,
).start()
print(f"Volleyball blocker web interface on port {PORT}")


def loop():
    """This function is called repeatedly by the App framework."""
    # The website runs in its own thread, so there is nothing to do here.
    time.sleep(10)


# See: https://docs.arduino.cc/software/app-lab/tutorials/getting-started/#app-run
App.run(user_loop=loop)
