import tkinter as tk

window = tk.Tk(screenName="BAaudio GUI")


def getText() :
    text = selectText.get("1.0", tk.END).strip()
    stdList = []
    for i in range(1, 5):
        linespaceIndex = text.find("\n")
        print(linespaceIndex)
        if linespaceIndex == -1: break

        stdList.append(text[0:linespaceIndex])
        text = text[linespaceIndex:]
        print(text)

    print(stdList)

lab = tk.Label(text="hello")

selectText = tk.Text()

getButton = tk.Button(text="send", command=getText)



lab.pack()
selectText.pack()
getButton.pack()
window.mainloop()