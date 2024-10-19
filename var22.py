import os
import xml.etree.ElementTree as ET
import zipfile
from datetime import datetime
import toml
import sys

class ShellEmulator:
    def __init__(self, config_path):
        self.config = self.load_config(config_path)
        self.username = self.config["user"]["name"]
        self.computer_name = self.config["user"]["computer"]
        self.fs_zip_path = self.config["paths"]["vfs"]
        self.log_file = self.config["paths"]["log"]
        self.start_script = self.config["paths"]["start_script"]
        self.parameter = self.config["user"]["parameter"]
        self.current_path = ""
        self.previous_path = ""
        self.vfs = {}
        self.load_vfs()
        self.create_log_file()
        self.run_start_script()
        
        
    def load_config (self, config_path: str) -> dict:
        with open(config_path, "r") as f:
            return toml.load(f)
        
        
    def load_vfs (self):
        with zipfile.ZipFile (self.fs_zip_path, "r") as zip_ref:
            for file in zip_ref.namelist():
                if file.endswith("/"):
                    normalized_path = os.path.join("/", file[:-1])
                else:
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
        if (path.startswith("/")):
            self.current_path = ""
            if path == "/":
                return
            path = path[1:]
        path = self.current_path + "/" + path
        if path in self.vfs:
            self.current_path = path
            return
        else:
            return (f"No such directory: {path}")
            
            
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
                
        return ("\n".join(sorted(contents)))
        
    
    def whoami(self):
        return(self.username)
        
        
    def head(self, file_path):
        stri = ""
        if file_path.startswith("/"):
            file_location = file_path
        else:
            file_location = self.current_path + "/" + file_path
        if file_location in self.vfs:
            data = str(zipfile.ZipFile(self.fs_zip_path, 'r').read(file_location[1:]))
            arr = data[2:-2].split('\\n')[:-1]
            if len(arr) < 10:
                for i in range(len(arr)-1):
                    stri = stri + arr[i] + "\n"
                stri = stri + arr[len(arr)-1]
            else:
                for i in range(9):
                    stri = stri + arr[i] + "\n"
                stri = stri + arr[9]
            return stri;
        else:
            return (f"No such file in directory: {file_location}")
                
    
    def exit_shell(self):
        self.log_action("session_end")
        self.save_log()
        return("Exiting...")
        
    
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
            (self.cd(command[3:]))
        elif command == "ls":
            print(self.ls())
        elif command == "exit":
            print(self.exit_shell())
            exit()
        elif command == "whoami":
            print(self.whoami())
        elif command.startswith("head "):
            print(self.head(command[5:]))
        else:
            print(f"Command not found: {command}")
        self.log_action(command)                 
                    
    
    def run(self):
        while True:
            command = input(f"{self.username}@{self.computer_name}:{self.current_path}$ ")
            self.execute(command)

if __name__ == "__main__":
    shell = ShellEmulator("config.toml")
    shell.run()
