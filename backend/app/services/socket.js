class SocketService {
  constructor() {
    this.socket = null;
  }

  connect(onMessage) {
    this.socket = new WebSocket("ws://localhost:8000/ws/alerts");

    this.socket.onopen = () => {
      console.log("WebSocket connected");
    };

    this.socket.onmessage = (event) => {
      const data = JSON.parse(event.data);
      onMessage(data);
    };

    this.socket.onclose = () => {
      console.log("WebSocket disconnected");
    };
  }

  disconnect() {
    if (this.socket) {
      this.socket.close();
    }
  }
}

export default new SocketService();