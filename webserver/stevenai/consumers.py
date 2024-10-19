import json
import threading
from channels.generic.websocket import WebsocketConsumer

from . import models

CLOSE_WITHOUT_CONNECT = -1
CLOSE_WITH_CONNECT = 1


class ChatConsumer(WebsocketConsumer):
    is_connected = False
    model_agent = models.StevenAIBot()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.timeout_timer = None  # Initialize the timer for connection timeout
        self.timeout_interval = 60  # Timeout interval in seconds

    def connect(self):
        # Check if a connection is already active
        if ChatConsumer.is_connected:
            self.close(CLOSE_WITHOUT_CONNECT)
            return
        # Accept the connection
        self.accept()
        ChatConsumer.is_connected = True
        self.send(
            text_data=json.dumps(
                {
                    "code": "CA",  # Connection Accepted
                    "message": "Connection established successfully – Please allow 5-20 seconds for the model to load!",
                }
            )
        )
        # Load the model
        success = ChatConsumer.model_agent.load_model()
        # Handle Failure
        if not success:
            self.close(CLOSE_WITH_CONNECT)
            return
        # Handle Success
        self.send(
            text_data=json.dumps(
                {
                    "code": "ML",  # Model Loaded
                    "message": "Model loaded successfully - Feel free to send me some messages!",
                }
            )
        )
        # Start the timer after connection is established
        self.start_timeout_timer()

    def disconnect(self, close_code):
        if close_code == CLOSE_WITH_CONNECT:
            # Reset the connection flag and stop the timer when this connection closes
            ChatConsumer.model_agent.unload_model()
            ChatConsumer.is_connected = False
            # Stop the timer if the connection closes
            self.stop_timeout_timer()
        return super().disconnect(close_code)

    def receive(self, text_data):
        # Pause the timer
        self.stop_timeout_timer()

        # Handle incoming messages and echo them back to the client
        input = json.loads(text_data).get("message", "")
        print("Receives message ", input)

        response = ChatConsumer.model_agent.generate_response(input)

        # Echo the message back to the client
        self.send(
            text_data=json.dumps({"code": "MR", "message": response})  # Model Response
        )
        # Restart Timer
        self.start_timeout_timer()

    # Function to start the timeout timer
    def start_timeout_timer(self):
        self.stop_timeout_timer()
        self.timeout_timer = threading.Timer(
            self.timeout_interval, self.close_due_to_timeout
        )
        self.timeout_timer.start()

    # Function to stop the timeout timer
    def stop_timeout_timer(self):
        if self.timeout_timer is not None:
            self.timeout_timer.cancel()
            self.timeout_timer = None

    # Function to close the connection due to timeout
    def close_due_to_timeout(self):
        self.send(
            text_data=json.dumps(
                {
                    "code": "TO",  # Timeout
                    "message": "Connection closed due to inactivity.",
                }
            )
        )
        self.close(CLOSE_WITH_CONNECT)
