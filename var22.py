import os
import xml.etree.ElementTree as ET
import zipfile
from datetime import datetime
import toml

class ShellEmulator:
    def __init__(self, config_path):
        """
        Initializing all required data for proper work
        """
        self.config = self.load_config(config_path)
        self.username = self.config["user"]["name"]
        self.computer_name = self.config["user"]["computer"]
        self.fs_zip_path = self.config["paths"]["vfs"]
        self.log_file = self.config["paths"]["log"]
        self.start_script = self.config["paths"]["start_script"]
        self.parameter = self.config["user"]["parameter"]
        self.current_path = "/"
        self.vfs = {}
        self.load_vfs()
        self.create_log_file()
        self.run_start_script()
        
        
    def load_config (self, config_path: str) -> dict:
        
        #Loads the configuration from the given file path.
        
        with open(config_path, "r") as f:
            return toml.load(f)
        
        
    def load_vfs (self):
        """
        Loading virtual file system from zip file at the given path.
        Trying to decode it as UTF-8. If cannot, then read it as binary.
        """
        with zipfile.ZipFile (self.fs_zip_path, "r") as zip_ref:
            for file in zip_ref.namelist():
                normalized_path = os.path.join("/", file)
                try:
                    self.vfs[normalized_path] = zip_ref.read(file).decode("UTF-8")
                except UnicodeDecodeError:
                    print(f"Warning! Unable to decode {file}. Storing as binary.")
                    self.vfs[normalized_path] = zip_ref.read(file)
     
     
    def create_log_file(self):
        root = ET.Element("session")
        self.log_tree = ET.ElementTree(root)
        self.log_action("session_start")
        
                    
    def log_action(self, action, user=None):
        if user is None:
            user = self.username
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        root = self.log_tree.getroot()
        entry = ET.SubElement(root, "action")
        ET.SubElement(entry, "user").text=user
        ET.SubElement(entry, "timestamp").text=timestamp
        ET.SubElement(entry, "command").text = action
        
        
    def save_log(self):
        self.log_tree.write(self.log_file)
        

    def cd (self, path):
        if path in self.vfs:
            self.current_path = path
        else:
            print(f"No such directory: {path}")
            
            
    def ls(self):
        contents = set()
        path_prefix = (
            self.current_path
            if self.current_path.endswith("/")
            else self.current_path + "/"
        )
        
        for file in self.vfs:
            if file.startswith(path_prefix):
                sub_path = file[len(path_prefix):].split("/")[0]
                contents.add(sub_path)
                
        print("\n".join(sorted(contents)))
        
    
    def whoami(self):
        print(self.username)
        
        
    def head(self, file_path):
        file_location = self.current_path + file_path
        if file_location in self.vfs:
            with open(file_location, "r") as f:
                head = [head(f) for i in range(10)]
            print(head)
        else:
            print(f"No such file in directory: {file_location}")
                
    
    def exit_shell(self):
        self.log_action("session_end")
        self.save_log()
        print("Exiting...")
        exit()
        
    
    def run_start_script(self):
        if os.path.exists(self.start_script) and self.start_script.endswith(".sh"):
            print(f"Running start script: {self.start_script}")
            with open(self.start_script, "r") as f:
                commands = f.readlines();
            for command in commands:
                command = command.strip()
                if command and not command.startswith("#"):
                    print(f"Executing command from script: {command}")
                    self.execute(command)
                    
    
    def execute(self, command):
        if command.startswith("cd "):
            self.cd(command[3:])
        elif command == "ls":
            self.ls()
        elif command == "exit":
            self.exit_shell()
        elif command == "whoami":
            self.whoami()
        elif command == "head ":
            self.head(command[5:])
        else:
            print(f"Command not found: {command}")
        self.log_action(command)                 
                    
    
    def run(self):
        while True:
            command = input(f"{self.username}@{self.computer_name}:{self.current_path}$ ")
            self.execute(command)

if __name__ == "__main__":
    import sys

    if len(sys.argv) != 2:
        print("Usage: python shell_emulator.py <config.toml>")
        sys.exit(1)

    config_path = sys.argv[1]
    shell = ShellEmulator(config_path)
    shell.run()