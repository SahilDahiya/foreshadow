import { Server, type Connection } from "partyserver";

// One Durable Object per show: the room every phone connects to.
// Skeleton only: it tracks who is connected and relays pings.
export class ShowRoom extends Server<Env> {
  static options = { hibernate: true };

  onConnect() {
    this.broadcastPresence();
  }

  onClose() {
    this.broadcastPresence();
  }

  onMessage(sender: Connection, message: string) {
    if (message === "ping") {
      this.broadcast(JSON.stringify({ type: "ping", from: sender.id }));
    }
  }

  private broadcastPresence() {
    // A closing connection can still be listed while onClose runs.
    const count = [...this.getConnections()].filter(
      (c) => c.readyState === WebSocket.OPEN,
    ).length;
    this.broadcast(JSON.stringify({ type: "presence", count }));
  }
}
