import json
import os
import subprocess
import shutil
import requests
import gdown
import time
import re
import mediafire
from zipfile import ZipFile 

def mediafireDL(folder_link, dest_folder):
    dest_folder_abs = os.path.abspath(dest_folder)
    folder_or_file = re.findall(r"mediafire\.com/(folder|file|file_premium)\/([a-zA-Z0-9]+)", folder_link)
    t, key = folder_or_file[0]
    mediafire.get_file(key, dest_folder)
    zip_files = [f for f in os.listdir(dest_folder_abs) if f.endswith('.zip')]
    for zip_file in zip_files:
        zip_path = os.path.join(dest_folder_abs, zip_file)
        with ZipFile(zip_path, 'r') as zObject:
            zObject.extractall(dest_folder_abs)
        os.remove(zip_path)
        move_contents_up_until_arc_file(dest_folder_abs)
        os.chdir(os.path.dirname(dest_folder_abs))
        input("Press Enter to continue...")

def dropboxDL(folder_link, dest_folder):
    r = requests.get(folder_link, allow_redirects=True)
    open(dest_folder + "/zip", 'wb').write(r.content)
    with ZipFile(dest_folder + "/zip", 'r') as zObject: 
        zObject.extractall(dest_folder)
        zObject.close()
        os.remove(dest_folder + "/zip")
        input("Press Enter to continue...")

def driveDL(folder_link, dest_folder):
    gdown.download(folder_link, dest_folder + "/zip", fuzzy=True)
    with ZipFile(dest_folder + "/zip", 'r') as zObject: 
        zObject.extractall(dest_folder)
        zObject.close()
        os.remove(dest_folder + "/zip")
        move_contents_up_until_arc_file(dest_folder)
        input("Press Enter to continue...")

def megaDL(folder_link, dest_folder):
    megacmd_path = os.path.join(os.getenv("LOCALAPPDATA"), "MEGAcmd", "MegaClient.exe")
    command = [megacmd_path, "get", folder_link, dest_folder]
    process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    stdout, stderr = process.communicate()
    if process.returncode != 0:
        print(f"Download failed: {stderr}")
    else:
        print(f"Download successful for {folder_link}.")
        try:
            move_contents_up_until_arc_file(dest_folder)
        except: # prob a zip file
            zip_files = [f for f in os.listdir(dest_folder) if f.endswith('.zip')]
            for zip_file in zip_files:
                zip_path = os.path.join(dest_folder, zip_file)
                with ZipFile(zip_path, 'r') as zObject:
                    zObject.extractall(dest_folder)
                os.remove(zip_path)
                move_contents_up_until_arc_file(dest_folder)
                os.chdir(os.path.dirname(dest_folder))
        input("Press Enter to continue...")


def move_contents_up_until_arc_file(folder_path):
    while True:
        items = os.listdir(folder_path)
        arc_files = [item for item in items if item.endswith('.arc')]
        if arc_files:
            print(f"Found arc file(s): {arc_files}. Stopping move.")
            break
        subdirs = [item for item in items if os.path.isdir(os.path.join(folder_path, item))]
        if not subdirs:
            print("No subdirectories to move.")
            break
        subdir_path = os.path.join(folder_path, subdirs[0])
        # Check if the destination folder has the same name as the sub-item
        if os.path.basename(folder_path) == subdirs[0]:
            print(f"Skipping move. Destination folder '{folder_path}' has the same name as the sub-item '{subdirs[0]}'.")
            break
        for sub_item in os.listdir(subdir_path):
            sub_item_path = os.path.join(subdir_path, sub_item)
            try:
                shutil.move(sub_item_path, folder_path)
            except shutil.Error as e:
                print(f"Error: {e}")
        os.rmdir(subdir_path)
        print(f"Moved contents from {subdir_path} up to {folder_path}.")


def convert_track_id(trackID, cupID):
    # Dictionary to map input track IDs to output track IDs
    track_id_mapping = {
        'A': ['A01', 'A02', 'A03', 'A04'],
        'B': ['A05', 'A06', 'A07', 'A08'],
        'C': ['A09', 'A10', 'A11', 'A12'],
        'D': ['A13', 'A14', 'A15', 'A16'],
        'E': ['B01', 'B02', 'B03', 'B04'],
        'F': ['B05', 'B06', 'B07', 'B08'],
        'G': ['B09', 'B10', 'B11', 'B12'],
        'H': ['B13', 'B14', 'B15', 'B16'],
        'I': ['C01', 'C02', 'C03', 'C04'],
        'J': ['C05', 'C06', 'C07', 'C08'],
        'K': ['C09', 'C10', 'C11', 'C12'],
        'L': ['C13', 'C14', 'C15', 'C16'],
        'M': ['D01', 'D02', 'D03', 'D04'],
        'N': ['D05', 'D06', 'D07', 'D08'],
        'O': ['D09', 'D10', 'D11', 'D12'],
        'P': ['D13', 'D14', 'D15', 'D16'],
        'Q': ['E01', 'E02', 'E03', 'E04'],
        'R': ['E05', 'E06', 'E07', 'E08'],
        'S': ['E09', 'E10', 'E11', 'E12'],
        'T': ['E13', 'E14', 'E15', 'E16'],
        'U': ['F01', 'F02', 'F03', 'F04'],
        'V': ['F05', 'F06', 'F07', 'F08'],
        'W': ['F09', 'F10', 'F11', 'F12'],
        'X': ['F13', 'F14', 'F15', 'F16'],
        'Y': ['G01', 'G02', 'G03', 'G04'],
        'Z': ['G05', 'G06', 'G07', 'G08'],
        'AA': ['G09', 'G10', 'G11', 'G12'],
        'AB': ['G13', 'G14', 'G15', 'G16']
    }
    
    # Extract the letter and digit from the input track ID
    letter = cupID
    digit = int(trackID)
    
    # Convert the input track ID to the output track ID
    if letter in track_id_mapping and 1 <= digit <= len(track_id_mapping[letter]):
        return track_id_mapping[letter][digit - 1]
    else:
        raise ValueError(f"Invalid track ID: {track_id}")

with open("../tracks.json", "r") as file:
    data = json.load(file)

downloadList = [entry["downloadLink"] for entry in data]
trackList = [entry["trackName"] for entry in data]
authorList = [entry["author"] for entry in data]
versionList = [entry["version"] for entry in data]
trackIDList = [entry["track"] for entry in data]
cupList = [entry["cup"] for entry in data]

for folder_link, track, author, version, trackID, cup in zip(downloadList, trackList, authorList, versionList, trackIDList, cupList):
    try:
        parsed_trackID = convert_track_id(trackID, cup)
    except ValueError as e:
        print(f"Error parsing track ID for {trackList}: {e}")
        continue
    dest_folder = os.path.join("../tracks/", parsed_trackID + "_" + track + " [" + author + "] (" + version + ")")
    if os.path.exists(dest_folder):
        print(f"Folder already exists: {dest_folder}. Skipping download.")
        continue
    os.makedirs(dest_folder, exist_ok=True)
    if "mega" in folder_link.lower():
        megaDL(folder_link, dest_folder)
    elif "drive.google" in folder_link.lower():
        driveDL(folder_link, dest_folder)
    elif "dropbox" in folder_link.lower() or "github" in folder_link.lower():
        dropboxDL(folder_link, dest_folder)
    elif "mediafire" in folder_link.lower():
        mediafireDL(folder_link, dest_folder)
    trackinfo_path = os.path.join(dest_folder, "trackinfo.ini")
    if os.path.exists(trackinfo_path):
        with open(trackinfo_path, "r") as trackinfo_file:
            trackinfo_content = trackinfo_file.readlines()
        for i in range(len(trackinfo_content)):
            if trackinfo_content[i].startswith("trackname"):
                trackinfo_content[i] = f"trackname = {track}\n"
        with open(trackinfo_path, "w") as trackinfo_file:
            trackinfo_file.writelines(trackinfo_content)