import PySimpleGUI as sg

def simple_debugging_gui():
    layout = [
        [sg.Text("PDF 1:"), sg.Input(), sg.FileBrowse(key="PDF1")],
        [sg.Text("PDF 2:"), sg.Input(), sg.FileBrowse(key="PDF2")],
        [sg.Text("Output PDF:"), sg.Input(), sg.FileSaveAs(key="Output")],
        [sg.Button("Compare"), sg.Button("Cancel")]
    ]

    window = sg.Window("PDF Comparison Tool Debugging", layout)

    while True:
        event, values = window.read()
        if event == sg.WIN_CLOSED or event == "Cancel":
            break
        if event == "Compare":
            print(values["PDF1"], values["PDF2"], values["Output"])  # Just print paths for debugging
            sg.popup("Path Info", f"PDF 1: {values['PDF1']}\nPDF 2: {values['PDF2']}\nOutput: {values['Output']}")

    window.close()

# Call the simplified debugging GUI function
simple_debugging_gui()
