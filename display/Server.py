import asyncio
import json
import logging
from typing import Set
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse
import uvicorn

logger = logging.getLogger(__name__)


class DisplayServer:
    """
    WebSocket server that:
    1. Serves the display page at /display
    2. Accepts WebSocket connections from display screens
    3. Broadcasts scripture data to all connected screens
    """

    def __init__(self, host: str = "0.0.0.0", port: int = 8000):
        self.host = host
        self.port = port
        self.app = FastAPI(title="ScriptureAI Display Server")
        self.connected_screens: Set[WebSocket] = set()
        self._setup_routes()

    def _setup_routes(self):
        """Set up FastAPI routes"""

        @self.app.get("/", response_class=HTMLResponse)
        async def root():
            """Redirect to display page"""
            return '<meta http-equiv="refresh" content="0;url=/display">'

        @self.app.get("/display", response_class=HTMLResponse)
        async def display_screen():
            """Serve the projector display page"""
            return self._get_display_html()

        @self.app.websocket("/ws")
        async def websocket_endpoint(websocket: WebSocket):
            """Handle WebSocket connections from display screens"""
            await websocket.accept()
            self.connected_screens.add(websocket)
            logger.info(
                f"Display screen connected "
                f"({len(self.connected_screens)} total)"
            )

            try:
                while True:
                    # Keep connection alive, receive heartbeat from client
                    await websocket.receive_text()
            except WebSocketDisconnect:
                self.connected_screens.discard(websocket)
                logger.info(
                    f"Display screen disconnected "
                    f"({len(self.connected_screens)} remaining)"
                )

        @self.app.get("/health")
        async def health():
            """Health check endpoint"""
            return {
                "status": "running",
                "connected_screens": len(self.connected_screens),
                "uptime": "ok"
            }

    async def broadcast(self, scripture: dict):
        """
        Broadcast scripture data to all connected display screens.

        Args:
            scripture: Dict containing book, chapter, verse, text
        """
        if not self.connected_screens:
            logger.warning("No display screens connected — scripture not displayed")
            return

        message = json.dumps({
            "type": "scripture",
            "book": scripture.get("book", ""),
            "chapter": scripture.get("chapter", ""),
            "verse": scripture.get("verse", ""),
            "text": scripture.get("text", ""),
            "reference": (
                f"{scripture.get('book', '')} "
                f"{scripture.get('chapter', '')}:"
                f"{scripture.get('verse', '')}"
            )
        })

        # Send to all connected screens
        disconnected = set()
        for screen in self.connected_screens:
            try:
                await screen.send_text(message)
                logger.debug(f"Scripture broadcast to screen")
            except Exception as e:
                logger.error(f"Failed to send to screen: {e}")
                disconnected.add(screen)

        # Clean up disconnected screens
        self.connected_screens -= disconnected
        if disconnected:
            logger.info(f"Removed {len(disconnected)} disconnected screen(s)")

    def start(self):
        """Start the server — runs in a background thread"""
        logger.info(f"Starting Display Server on {self.host}:{self.port}")
        uvicorn.run(
            self.app,
            host=self.host,
            port=self.port,
            log_level="info"
        )

    def _get_display_html(self) -> str:
        """Generate the projector display HTML page"""
        return """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>ScriptureAI Display</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }

        body {
            background: linear-gradient(135deg, #0a0e27 0%, #1a1a3e 100%);
            color: #fff;
            font-family: 'Georgia', serif;
            height: 100vh;
            display: flex;
            align-items: center;
            justify-content: center;
            overflow: hidden;
        }

        #waiting {
            text-align: center;
            opacity: 0.5;
            font-size: 1.2rem;
        }

        #waiting p:first-child {
            font-size: 2.5rem;
            margin-bottom: 20px;
        }

        #scripture-display {
            display: none;
            text-align: center;
            padding: 60px;
            max-width: 90%;
            animation: fadeIn 0.8s ease;
        }

        @keyframes fadeIn {
            from { opacity: 0; transform: translateY(20px); }
            to   { opacity: 1; transform: translateY(0); }
        }

        #reference {
            font-size: 1.8rem;
            color: #f0c040;
            font-weight: bold;
            margin-bottom: 30px;
            letter-spacing: 0.05em;
            text-transform: uppercase;
        }

        #verse-text {
            font-size: 2.4rem;
            line-height: 1.6;
            color: #ffffff;
            font-style: italic;
            text-shadow: 0 2px 20px rgba(255,255,255,0.1);
        }

        #divider {
            width: 100px;
            height: 3px;
            background: #f0c040;
            margin: 25px auto;
            border-radius: 2px;
        }

        /* Connection status indicator */
        #status {
            position: fixed;
            bottom: 20px;
            right: 20px;
            font-size: 0.8rem;
            opacity: 0.5;
            font-family: monospace;
            padding: 8px 12px;
            border-radius: 4px;
            background: rgba(0,0,0,0.3);
        }

        #status.connected { 
            color: #00ff00;
            border: 1px solid #00ff00;
        }
        
        #status.disconnected { 
            color: #ff4444;
            border: 1px solid #ff4444;
        }

        /* Logo in top left */
        #logo {
            position: fixed;
            top: 20px;
            left: 20px;
            font-size: 0.9rem;
            opacity: 0.3;
            font-family: monospace;
        }
    </style>
</head>
<body>

    <div id="logo">ScriptureAI v1.0</div>

    <div id="waiting">
        <p>📖</p>
        <p style="margin-top:10px; font-size:0.9rem">Waiting for sermon to begin...</p>
    </div>

    <div id="scripture-display">
        <div id="reference">—</div>
        <div id="divider"></div>
        <div id="verse-text">—</div>
    </div>

    <div id="status" class="disconnected">⬤ connecting...</div>

    <script>
        const waiting = document.getElementById('waiting');
        const display = document.getElementById('scripture-display');
        const referenceEl = document.getElementById('reference');
        const verseEl = document.getElementById('verse-text');
        const statusEl = document.getElementById('status');

        // Auto-hide scripture after 30 seconds
        let hideTimer = null;

        function showScripture(data) {
            // Update content
            referenceEl.textContent = data.reference;
            verseEl.textContent = '"' + data.text + '"';

            // Show display, hide waiting
            waiting.style.display = 'none';
            display.style.display = 'block';

            // Reset animation
            display.style.animation = 'none';
            display.offsetHeight; // Trigger reflow
            display.style.animation = 'fadeIn 0.8s ease';

            // Auto-hide after 30 seconds
            if (hideTimer) clearTimeout(hideTimer);
            hideTimer = setTimeout(() => {
                display.style.display = 'none';
                waiting.style.display = 'block';
            }, 30000);
        }

        // Connect to WebSocket
        function connect() {
            const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
            const ws = new WebSocket(protocol + '//' + window.location.host + '/ws');

            ws.onopen = () => {
                statusEl.textContent = '⬤ connected';
                statusEl.className = 'connected';
                // Send heartbeat every 30 seconds
                setInterval(() => {
                    if (ws.readyState === WebSocket.OPEN) {
                        ws.send('ping');
                    }
                }, 30000);
            };

            ws.onmessage = (event) => {
                try {
                    const data = JSON.parse(event.data);
                    if (data.type === 'scripture') {
                        showScripture(data);
                    }
                } catch (e) {
                    console.error('Failed to parse message:', e);
                }
            };

            ws.onclose = () => {
                statusEl.textContent = '⬭ reconnecting...';
                statusEl.className = 'disconnected';
                // Reconnect after 2 seconds
                setTimeout(connect, 2000);
            };

            ws.onerror = (error) => {
                console.error('WebSocket error:', error);
                statusEl.textContent = '⬭ error';
                statusEl.className = 'disconnected';
            };
        }

        // Connect on page load
        connect();
    </script>
</body>
</html>"""


if __name__ == "__main__":
    import sys
    server = DisplayServer(
        host="0.0.0.0",
        port=8000
    )
    logger.basicConfig(level=logging.INFO)
    server.start()
