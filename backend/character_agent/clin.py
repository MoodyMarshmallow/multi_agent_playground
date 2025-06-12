from kani import Kani

class LogMessagesKani(Kani):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.log_file = open("kani-log.jsonl", "w")
    

    async def meta_memory(self):
        pass


    async def add_to_history(self, message, *args, **kwargs):
        await super().add_to_history(message, *args, **kwargs)
        self.log_file.write(message.model_dump_json())
        self.log_file.write("\n")
    