from pathlib import Path
import platform
def standardfile_prefix():
    prefix = "std_"
    return prefix
def get_std_save_path():
    system = platform.system()
    if system == "Windows":
        return Path("C:/tmp/standardfile.txt")
    else:
        # Op Linux/macOS wordt de map in de thuismap gezet
        return Path.home() / "tmp/standardfile.txt"
