class RetrivalError(Exception):
    def __init__(self, messages):
        super().__init__(messages)
        self.messages = messages
    
    def __str__(self):
        return f"The Error During the Retrival process in the Redis Vector DB : {self.messages}"

