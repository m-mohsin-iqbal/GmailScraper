import os
chrome_path = r"C:/Users/LENOVO/AppData/Local/Google/Chrome/Application/chrome.exe"
os.system(f"start \"\" \"{chrome_path}\" --user-data-dir=\"%cd%\cd\" --window-position=0,0")