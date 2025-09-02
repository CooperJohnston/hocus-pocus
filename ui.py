import tkinter as tk
from tkinter import font
import os

def initialize_interface():

    def last_instructions():
        for widget in root.winfo_children():
            widget.destroy()

        # Header
        lbl = tk.Label(root, text="Before you start...", font=header_font, fg="#f9cb52", bg="#1c1c2c")
        lbl.pack(pady=(30, 10))

        subtext = tk.Label(root, text="Once you click this button, the calibration process will begin.\nPLEASE MAKE SURE TO KEEP YOUR EYES LOCKED ON THE MOUSE CURSOR AT ALL TIMES DURING CALIBRATION.\nYou will be asked to move your cursor through a maze that starts in the top left corner and ends in the bottom right corner.\nKeeping your eyes on the cursor as you move through the maze will allow the program to calibrate.\nThe Screenmate will appear shortly after calibration is finished.\nThank you and enjoy your time with Focus Pocus!", font=body_font, fg="#baacd4", bg="#1c1c2c")
        subtext.pack(pady=(0, 15))

        lst_bttn = tk.Button(root, text="🚀 Continue!", font=body_font, bg="#9470ea", fg="white",
                       activebackground="#503c80", activeforeground="white", relief="raised", bd=4)

        lst_bttn.pack(pady=20)
        lst_bttn.config(command=root.quit)

    def show_username_entry(is_new_user):
        # Clear the window
        for widget in root.winfo_children():
            widget.destroy()

        # Header
        label = tk.Label(root, text="Welcome to FocusPocus!", font=header_font, fg="#f9cb52", bg="#1c1c2c")
        label.pack(pady=(30, 10))

        if is_new_user:
            subtext = tk.Label(root, text="Please enter a new random noun.", font=body_font, fg="#baacd4", bg="#1c1c2c")
        else:
            subtext = tk.Label(root, text="Please enter your returning username.", font=body_font, fg="#baacd4", bg="#1c1c2c")
        subtext.pack(pady=(0, 15))

        entry = tk.Entry(root, font=body_font, width=30, justify='center', fg="#301279", bg="#baacd4",
                     insertbackground="#301279", relief="flat")
        error_label = tk.Label(root, text="", font=body_font, fg="red", bg="#1c1c2c")
        button = tk.Button(root, text="🚀 Continue!", font=body_font, bg="#9470ea", fg="white",
                       activebackground="#503c80", activeforeground="white", relief="raised", bd=4)

        entry.pack(pady=5)
        error_label.pack(pady=(0, 10))
        button.pack(pady=20)

        def submit_new():
            username = entry.get().strip()
            username_var.set(username)
            userTextFile = f'User_Data/{username_var.get()}_EXTRA_DATA.txt'
            user_csv = f"User_Data/{username_var.get().lower()}_data.csv"
            if os.path.exists(userTextFile) or os.path.exists(user_csv):
                error_label.config(text="Oops! That word has already been chosen. Please try another.")
            else:
                # root.quit()
                last_instructions()

        def submit_returning():
            username = entry.get().strip()
            username_var.set(username)
            userTextFile = f'User_Data/{username_var.get()}_EXTRA_DATA.txt'
            user_csv = f"User_Data/{username_var.get().lower()}_data.csv"
            if not (os.path.exists(userTextFile) or os.path.exists(user_csv)):
                error_label.config(text="Username not found. Please try again or register as a new user.")
            else:
                # root.quit()
                last_instructions()

        # Change the submit function for returning users
        if is_new_user:
            button.config(command=submit_new)
        else:
            button.config(command=submit_returning)

    root = tk.Tk()
    username_var = tk.StringVar()
    root.title("✨ Welcome to FocusPocus ✨")
    root.geometry("2400x1200")
    # root.geometry("600x300")
    root.configure(bg="#1c1c2c")

    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()
    x = (screen_width // 2) - (2400 // 2)
    y = (screen_height // 2) - (1200 // 2)
    # x = (screen_width // 2) - (600 // 2)
    # y = (screen_height // 2) - (300 // 2)
    root.geometry(f"+{x}+{y}")

    try:
        header_font = font.Font(family="Comic Sans MS", size=20, weight="bold")
        body_font = font.Font(family="Comic Sans MS", size=14)
    except:
        header_font = ("Helvetica", 20, "bold")
        body_font = ("Helvetica", 14)

    # Initial welcome screen with New/Returning buttons
    label = tk.Label(root, text="Welcome to FocusPocus!", font=header_font, fg="#f9cb52", bg="#1c1c2c")
    label.pack(pady=(100, 20))
    prompt = tk.Label(root, text="Are you a new or returning user?", font=body_font, fg="#baacd4", bg="#1c1c2c")
    prompt.pack(pady=(0, 30))

    new_btn = tk.Button(root, text="New User", font=body_font, bg="#4caf50", fg="white",
                        command=lambda: show_username_entry(True))
    new_btn.pack(pady=10)

    returning_btn = tk.Button(root, text="Returning User", font=body_font, bg="#2196f3", fg="white",
                              command=lambda: show_username_entry(False))
    returning_btn.pack(pady=10)

    root.mainloop()
    root.destroy()
    return username_var.get()

