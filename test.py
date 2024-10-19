import unittest
from var22 import ShellEmulator

class TestShell(unittest.TestCase):
    def setUp(self):
        self.ShellEmulator = ShellEmulator("config.toml")
    def returnPathCd(self, command):
        self.ShellEmulator.execute(command)
        return self.ShellEmulator.current_path
    def test_cd(self):
        self.assertEqual(self.returnPathCd("cd test"), "/test")
    def test_ls(self):
        a = "test"
        self.assertMultiLineEqual(self.ShellEmulator.ls(), a)
    def test_whoami(self):
        self.assertEqual(self.ShellEmulator.whoami(), "admin")
    def test_head(self):
        check = "All day\nAlways\nI have to go somewhere\nAll day\nAlways\nI have to go somewhere\nHello, hello\nHello, hello\nI'll walk away\nI'll walk away"
        self.assertMultiLineEqual(self.ShellEmulator.head("/test/1/A Fool Moon Night.txt"), check)
if __name__ == "__main__":
    unittest.main()