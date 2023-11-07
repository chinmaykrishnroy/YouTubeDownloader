import tkinter as tk

# Create the main window
root = tk.Tk()

root.title("Registration Form")

# Create and place labels and entry fields for the form
name=tk.Label(root,text="Name")
name.pack()
entry_name=tk.Entry(root)
entry_name.pack()

label_username = tk.Label(root, text="Username:")
label_username.pack()
entry_username = tk.Entry(root)
entry_username.pack()

label_password = tk.Label(root, text="Password:")
label_password.pack()
entry_password = tk.Entry(root, show="*")  # Show asterisks instead of the actual password characters
entry_password.pack()

label_email = tk.Label(root, text="Email:")
label_email.pack()
entry_email = tk.Entry(root)
entry_email.pack()

# Create and place the submit button
btn_submit = tk.Button(root, text="Submit")
btn_submit.pack()
root.mainloop()
# Start the main event loop