import os
import yaml
import requests
from rich.console import Console


class DelphiBot:
    BASE_ENDPOINT = "https://api.openai.com/v1"

    def __init__(self, config:str):
        self.console = Console()
        self.message_history = []
        self.is_running = False
        self.model = "gpt-3.5-turbo"

        try:
            self.config = self.read_config_file(config)
        except FileNotFoundError:
            self.console.print("Configuration file not found", style="red bold")
            exit()

        self.console.print("ChatGPT CLI", style="bold")
        self.headers = {
            "Content-Type": "application/json",
            "Authorization": f'Bearer {self.config["api_key"]}'
        }

    def __repr__(self):
        return f'<DelphiBot object at {hex(id(self))}>'

    @staticmethod
    def read_config_file(filename: str) -> dict:
        """
        Read a YAML configuration file and convert to Python dictionary.

        Args:
            filename (str): File path of YAML configuration file

        Returns:
            dict: Parsed YAML configuration dictionary
        """
        config_file = os.path.join(os.path.dirname(__file__), filename)
        if not os.path.exists(config_file):
            raise FileNotFoundError(f'Config file \"{filename}\" does not exists at {config_file}')

        if not (filename.endswith(".yml") or filename.endswith(".yaml")):
            file_type = filename.split(".")[-1]
            raise ValueError(f'Config file must be a YAML file format, but {file_type.upper()} was given.')

        # Open the YAML config file
        with open(config_file, "r") as file:
            configs = yaml.load(file, Loader=yaml.FullLoader)

        print(f'Read config file from: {config_file}')
        return configs

    def respond(self, inquiry:str) -> str:
        if not isinstance(inquiry, str):
            raise ValueError("Inquiry must be string input.")

        self.message_history.append({
            "role": "user",
            "content": inquiry
        })

        body = {
            "model": self.model,
            "messages": self.message_history
        }

        get_response = requests.post(f"{self.BASE_ENDPOINT}/chat/completions", headers=self.headers, json=body)

        response = get_response.json()["choices"][0]["message"]["content"].strip()
        self.console.print(f'Delphi: {response}')
        self.message_history.append(response)

    def run(self) -> None:
        self.is_running = True
        while self.is_running:
            try:
                message = self.console.input("[bold]>>> [/bold]")
                if message.lower() in ("q", "quit"):
                    print("Shutdown signal detected! Ending processes...")
                    self.is_running = False
                    break
                else:
                    self.respond(message)

            except requests.ConnectionError:
                self.console.print("Connection error, try again...", style="red bold")
                self.message_history.pop()
                continue

            except requests.Timeout:
                self.console.print("Connection timed out, try again...", style="red bold")
                self.message_history.pop()
                continue

            except KeyboardInterrupt:
                self.console.print("Keyboard interrupt detected, shutting down...", style="red bold")
                self.is_running = False
                break

            except Exception as e:
                print(f'Error during main run: {e}')
                continue
