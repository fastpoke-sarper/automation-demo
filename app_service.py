import subprocess

def open_zoom(url: str, zoom_bin: str) -> bool:
    
    subprocess.Popen([zoom_bin, '--url=' + url])


def open_meet(url: str, browser_bin: str) -> bool:
    
    subprocess.Popen([browser_bin, url])


