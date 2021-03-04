from backupImporter_VKRC import VKRCImport
from collisionReader import CollisionReader
import tkinter as tk
from tkinter import filedialog

if __name__ == '__main__':
    root = tk.Tk()
    root.withdraw()
    files = filedialog.askopenfilenames(initialdir="/", title="Select file",
                                        filetypes=(("zip files", "*.zip"), ("all files", "*.*")))

    CollisionReader(VKRCImport, files)
