import sys
import requests
import collections
import base64
import shutil
import os

import PySimpleGUI as gui

gui.theme("Default1")

layout = [
    [gui.Text("SCP Battles Updater", font = ("Arial",20, "bold"))],
    [gui.Text("")],
    [gui.Button("Fetch Latest Update", font = ("Arial",14), key = "-FETCH_LATEST-")],
    #[gui.Text("")],
    [gui.Text("Version: N/A", font = ("Arial",10), key = "-VERSION-")],
    [gui.Text("Notes: N/A", font = ("Arial",10), key = "-NOTES-")],
    [gui.Text("")],
    [gui.Button("Install Update", disabled = True, font = ("Arial",14), key = "-INSTALL_UPDATE-")]
]

window = gui.Window("SCP Battles Updater", layout, resizable = False)

while True:
    event, values = window.read()

    if event == None:
        sys.exit()

    if event == "-FETCH_LATEST-":
        response = requests.get("http://voxany.io/updates/latest")

        update = collections.defaultdict(lambda: "N/A", response.json())

        version = update["version"]
        notes = update["notes"]
        update_data = update["update_data"]

        window["-VERSION-"].update(f"Version: {version}")
        window["-NOTES-"].update(f"Notes: {notes}")
        window["-INSTALL_UPDATE-"].update(disabled = False)

    if event == "-INSTALL_UPDATE-":

        update_data_decoded = base64.b64decode(update_data)

        with open("update.zip", "wb") as file:
            file.write(update_data_decoded)

        shutil.unpack_archive("update.zip")

        os.remove("update.zip")

        window["-INSTALL_UPDATE-"].update("Success!")
