import { Server, type Connection } from "partyserver";
import { DEMO_SCENE } from "../shared/demo-scene";
import {
  initialShowState,
  isShowState,
  type ClientMessage,
  type ServerMessage,
  type ShowState,
} from "../shared/protocol";

// One Durable Object per show: the room every phone connects to.
// The host device writes the show state; the room stores it, logs every change,
// and relays it to every phone. Higher sequence numbers win, so repeated or
// late messages can't move the show backwards.
export class ShowRoom extends Server<Env> {
  static options = { hibernate: true };

  onStart() {
    this.db.exec(
      "CREATE TABLE IF NOT EXISTS show_state (id INTEGER PRIMARY KEY CHECK (id = 1), state TEXT NOT NULL)",
    );
    this.db.exec(
      "CREATE TABLE IF NOT EXISTS events (seq INTEGER PRIMARY KEY, at INTEGER NOT NULL, state TEXT NOT NULL)",
    );
  }

  onConnect(connection: Connection) {
    this.send(connection, { type: "welcome", scene: DEMO_SCENE, state: this.load() });
  }

  onMessage(sender: Connection, raw: string) {
    let message: ClientMessage;
    try {
      message = JSON.parse(raw) as ClientMessage;
    } catch {
      return;
    }
    const current = this.load();

    if (message.type === "state" && isShowState(message.state)) {
      if (message.state.seq <= current.seq) {
        // Stale: tell the sender what the room has, so it can catch up.
        this.send(sender, { type: "state", state: current });
        return;
      }
      this.save(message.state);
      this.broadcast(JSON.stringify({ type: "state", state: message.state } satisfies ServerMessage), [
        sender.id,
      ]);
    }

    if (message.type === "reset") {
      const state = { ...initialShowState(), seq: current.seq + 1 };
      this.save(state);
      this.broadcast(JSON.stringify({ type: "state", state } satisfies ServerMessage));
    }
  }

  private get db() {
    return this.ctx.storage.sql;
  }

  private load(): ShowState {
    const row = this.db
      .exec<{ state: string }>("SELECT state FROM show_state WHERE id = 1")
      .toArray()[0];
    return row ? (JSON.parse(row.state) as ShowState) : initialShowState();
  }

  private save(state: ShowState) {
    const json = JSON.stringify(state);
    this.db.exec(
      "INSERT INTO show_state (id, state) VALUES (1, ?) ON CONFLICT(id) DO UPDATE SET state = excluded.state",
      json,
    );
    this.db.exec("INSERT OR REPLACE INTO events (seq, at, state) VALUES (?, ?, ?)", state.seq, Date.now(), json);
  }

  private send(connection: Connection, message: ServerMessage) {
    connection.send(JSON.stringify(message));
  }
}
