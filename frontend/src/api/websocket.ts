export function createWs(): WebSocket {
    const url = `ws://${location.hostname}:8000/ws/chat`
    const ws = new WebSocket(url)
    return ws
  }
  