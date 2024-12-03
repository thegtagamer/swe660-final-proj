import { io } from "socket.io-client";

const SOCKET_URL = "ws://localhost:9080"; // Backend WebSocket URL

const socket = io(SOCKET_URL, {
  transports: ["websocket"], // Ensure WebSocket is used
  reconnection: true, // Reconnect if the connection is lost
});

export default socket;
