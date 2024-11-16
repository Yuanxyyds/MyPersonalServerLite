import json
import threading
from channels.generic.websocket import WebsocketConsumer

from . import models

CLOSE_WITHOUT_CONNECT = 1006
CLOSE_WITH_CONNECT = 1000


class ChatConsumer(WebsocketConsumer):
    timeout_timer = None  # Initialize the timer for connection timeout
    timeout_interval = 60  # Timeout interval in seconds
    is_connected = False
    model_agent = models.StevenAIBot()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def connect(self):
        # Check if a connection is already active
        if ChatConsumer.is_connected:
            # This will return code 1006
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
            self.close(code=CLOSE_WITH_CONNECT)
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
        print("RECEIVE CLOSE CODE: ", close_code)
        if close_code != CLOSE_WITHOUT_CONNECT:
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
        ChatConsumer.timeout_timer = threading.Timer(
            ChatConsumer.timeout_interval, self.close_due_to_timeout
        )
        ChatConsumer.timeout_timer.start()

    # Function to stop the timeout timer
    def stop_timeout_timer(self):
        if ChatConsumer.timeout_timer is not None:
            ChatConsumer.timeout_timer.cancel()
            ChatConsumer.timeout_timer = None

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
        # Force Timeout reset to prevent socket close issues
        print("Timeout received. Reset forcely")
        ChatConsumer.model_agent.unload_model()
        ChatConsumer.is_connected = False
        self.close(code=CLOSE_WITH_CONNECT)
