import sys
import requests
import collections
import base64

import PySimpleGUI as gui

gui.theme("Default1")

layout = [
    [gui.Text("SCP Battles Updater", font = ("Arial",20, "bold"))],
    [gui.Text("")],
    [gui.Text("Update File: ", size = (8,1), font = ("Arial",10)), gui.Input("", size = (20,1), key = "-UPDATE_PATH-"), gui.FileBrowse(font = ("Arial",10), size = (6,1))],
    [gui.Text("Version: ", size = (8,1), font = ("Arial",10)), gui.Input("", size = (20,1), key = "-VERSION-")],
    [gui.Text("Note: ", size = (8,1), font = ("Arial",10)), gui.Input("", size = (20,1), key = "-NOTES-")],
    [gui.Text()],
    [gui.Button("Push Update", font = ("Arial",14), key = "-PUSH_UPDATE-")]
]
window = gui.Window("SCP Battles Updater", layout, resizable = False)

while True:
    event, values = window.read()

    if event == None:
        sys.exit()

    if event == "-PUSH_UPDATE-":

        update_path = values["-UPDATE_PATH-"]
        notes = values["-NOTES-"]
        version = values["-VERSION-"]

        with open(update_path, "rb") as file:
            data = file.read()

        encoded_data = base64.b64encode(data).decode("utf-8")

        update = {
            "notes": notes,
            "version": version,
            "update_data": encoded_data
        }

        response = requests.put("http://voxany.io/updates/latest", json = update)

        if response.status_code == 201:
            window["-PUSH_UPDATE-"].update("Success!", text_color = "green")
