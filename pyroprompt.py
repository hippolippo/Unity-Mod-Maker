# This module is created completely by hippolippo to have a prompt in the style of pyro
from tkinter import *
from functools import partial


def create_prompt(title, questions: tuple, fallback, cancel_fallback, defaults=None, warning=None):
    root = Tk()
    root.configure(background="#00062A")
    root.title(title)
    root.iconbitmap("resources/unitymodmaker.ico")
    Frame(root, width=250, background="#00062A").pack()
    frame = Frame(root, width=250, background="#00062A")
    frame.pack()
    heading = Label(frame, text=title, font=("Arial", 18), background="#00062A", fg="#b4d9f9")
    heading.pack(fill="x")
    if warning is None:
        error = Label(frame, background="#00062A", fg="red")
    else:
        error = Label(frame, text=warning, background="#00062A", fg="red")
    error.pack()
    answers = list()
    for question in enumerate(questions):
        Label(frame, text=question[1], font=("Arial", 12), background="#00062A", fg="#acc5dc").pack(fill="x")
        answers.append(Entry(frame, background="#4A3EAB", font=("Arial", 12)))
        answers[-1].pack(fill="x")
        if defaults is not None:
            answers.insert(1.0, defaults[question[0]])
        Frame(frame, background="#00062A").pack(pady=10)
    buttons = Frame(root, background="#00062A")
    buttons.pack()
    Button(buttons, text="Cancel", bg="#4A3EAB", command=partial(cancel, root, cancel_fallback)).grid(row=0, column=0, padx=10, pady=(10,10))
    Button(buttons, text="Done", bg="#4A3EAB", command=partial(done, root, fallback, answers, error)).grid(row=0, column=1, padx=10, pady=(10,10))
    root.mainloop()


def cancel(root, fallback):
    root.destroy()
    if fallback is None:
        return
    fallback(None)


def done(root, fallback, answers, error):
    if fallback is not None:
        x = fallback([i.get() for i in answers])s
    if x is not None:
        error.configure(text=x)
    else:
        root.destroy()


if __name__ == "__main__":
    def x(x):
        return "hi"
    create_prompt("Test Prompt", ("Question 1", "Question 2", "Question 3"), x, print)
