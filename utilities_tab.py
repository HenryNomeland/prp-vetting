import flet as ft
import os
import re
from db_updates import get_directorypath, make_conn
import shutil
import random
import csv
from db_initialization import init_db
import pandas as pd
from add_silence import add_silence
import filecmp
from datetime import datetime
import pytz
central_timezone = pytz.timezone('America/Chicago')

utility_text = "Utility Outputs:"
timestamp_paths = os.path.join(get_directorypath("X:\\CHILD TD RSCH\\PRP"), "timestamps.txt")
try:
    if os.path.exists(timestamp_paths):
        with open(timestamp_paths, "r") as file:
            lines = file.readlines()
            ava_data_time_stamp = lines[0].strip()
            vetted_data_time_stamp = lines[1].strip()
    else:
        with open(timestamp_paths, "x") as file:
            file.write("Unknown\nUnknown")
        ava_data_time_stamp = "Unknown"
        vetted_data_time_stamp = "Unknown"
except:
    ava_data_time_stamp = "Unknown"
    vetted_data_time_stamp = "Unknown"

def create_utilities_tab(page: ft.Page):

    def update_output(text, replace=False):
        global utility_text
        if replace:
            utility_text = "Utility Outputs:"
        utility_text += text
        util_tab.controls[1].content.controls[0].value = utility_text
        page.update()

    def backup_database():
        basepath = get_directorypath("X:\\CHILD TD RSCH\\PRP")
        og_path = os.path.join(basepath, "audio.db")
        new_path = os.path.join(basepath, "Utils", "audio.db")
        update_output("\nCreating database backup.\nCopying audio.db to Util...")
        shutil.copy2(og_path, new_path)
        update_output("\nDatabase copy and backup completed!")

    def updateDataClick(e):
        def handle_close(e):
            lines = []
            current_time_central = datetime.now(central_timezone)
            ava_data_time_stamp = current_time_central.strftime("%m-%d-%y")
            lines.append(ava_data_time_stamp + "\n")
            lines.append(vetted_data_time_stamp)
            with open(timestamp_paths, "w") as f:
                f.writelines(lines)
            page.close(dataClickDialog)

        def create_directories(
            source_directory, target_directory, longitudinal_manual=False
        ):
            if len(re.findall("SEALS", os.path.basename(source_directory))) > 0:
                longitudinal_manual = True
                seals = True
            else:
                seals = False
            ## step 1 - make sure that all children top-level directories are synced
            sourcedirs = next(os.walk(source_directory))[1]
            targetdirs = next(os.walk(target_directory))[1]
            for directory in sourcedirs:
                if (
                    len(
                        re.findall(
                            r"cp", os.path.basename(source_directory), re.IGNORECASE
                        )
                    )
                    > 0
                ) or (longitudinal_manual):
                    if (
                        re.fullmatch(r"^[A-Za-z()]+$", directory)
                        and len(re.findall(r"[A-Z]", directory)) >= 2
                    ) or (re.fullmatch(r"c-\d{2}", directory)):
                        if directory not in targetdirs:
                            update_output(f"\n{directory} copied!")
                            os.makedirs(os.path.join(target_directory, directory))
                        else:
                            update_output(f"\n{directory} already exists")
                else:
                    if re.search(r"^\d{4}_.*_", directory):
                        if directory not in targetdirs:
                            update_output(f"\n{directory} copied!")
                            os.makedirs(os.path.join(target_directory, directory))
                        else:
                            update_output(f"\n{directory} already exists")
            ## step 2 - make sure that any visits are synced and have all 3 necessary folders
            dircount = 0
            target_subdirs = os.listdir(target_directory)
            if (
                len(
                    re.findall(r"cp", os.path.basename(source_directory), re.IGNORECASE)
                )
                > 0
            ) or (longitudinal_manual):
                for child in next(os.walk(source_directory))[1]:
                    childpath = os.path.join(source_directory, child)
                    if child in target_subdirs:
                        if seals:
                            to_create = [
                                visit
                                for visit in next(os.walk(childpath))[1]
                                if re.findall("v", visit)
                            ]
                        else:
                            to_create = [
                                visit
                                for visit in next(os.walk(childpath))[1]
                                if re.findall("Visit|visit", visit)
                            ]
                        for visit in to_create:
                            visit = re.sub("v", "V", visit)
                            long_dir = os.path.join(
                                target_directory, child, visit, "Long STOCS"
                            )
                            short_dir = os.path.join(
                                target_directory, child, visit, "Short STOCS"
                            )
                            sss_dir = os.path.join(
                                target_directory, child, visit, "SSS"
                            )
                            if not os.path.exists(long_dir):
                                update_output(f"\n{child}, {visit}, copied!")
                                dircount += 1
                                os.makedirs(long_dir)
                            if not os.path.exists(short_dir):
                                os.makedirs(short_dir)
                            if not os.path.exists(sss_dir):
                                os.makedirs(sss_dir)
                            else:
                                update_output(f"\n{child}, {visit}, already exists")
            else:
                for child in next(os.walk(source_directory))[1]:
                    childpath = os.path.join(source_directory, child)
                    if child in target_subdirs:
                        long_dir = os.path.join(
                            target_directory, child, "Visit 01", "Long STOCS"
                        )
                        short_dir = os.path.join(
                            target_directory, child, "Visit 01", "Short STOCS"
                        )
                        sss_dir = os.path.join(
                            target_directory, child, "Visit 01", "SSS"
                        )
                        if not os.path.exists(long_dir):
                            update_output(f"\n{child} copied!")
                            dircount += 1
                            os.makedirs(long_dir)
                        if not os.path.exists(short_dir):
                            os.makedirs(short_dir)
                        if not os.path.exists(sss_dir):
                            os.makedirs(sss_dir)
                        else:
                            update_output(f"\n{child} already exists")
            return dircount

        def create_files(
            original_directory,
            stocs_directory,
            new_directory,
            longitudinal_manual=False,
        ):
            if len(re.findall("SEALS", os.path.basename(original_directory))) > 0:
                longitudinal_manual = True
                seals = True
            else:
                seals = False
            child_dict = {}
            with open(
                os.path.join(
                    get_directorypath(r"Y:\CHILD TD RSCH\PRP"), "child_dict.csv"
                ),
                encoding="utf-8",
            ) as file:
                reader = csv.reader(file)
                for row in reader:
                    if row:
                        key = row[0]
                        values = row[1:]
                        child_dict[key] = values
            filecount = 0
            # Handling the CP folder case
            if (len(re.findall("CP", os.path.basename(original_directory))) > 0) or (
                longitudinal_manual
            ):
                for child in next(os.walk(new_directory))[1]:
                    if (seals) and (child[:2] != "c-"):
                        continue
                    childpath = os.path.join(new_directory, child)
                    for visit in next(os.walk(childpath))[1]:
                        long_path = os.path.join(childpath, visit, "Long STOCS")
                        short_path = os.path.join(childpath, visit, "Short STOCS")
                        sss_path = os.path.join(childpath, visit, "SSS")
                        if os.path.isdir(
                            os.path.join(original_directory, child, visit)
                        ):
                            og_stocsvisitpath = os.path.join(
                                stocs_directory, child, visit
                            )
                            og_visitpath = os.path.join(
                                original_directory, child, visit
                            )
                        elif os.path.isdir(
                            os.path.join(original_directory, child, visit.lower())
                        ):
                            og_stocsvisitpath = os.path.join(
                                stocs_directory, child, visit.lower()
                            )
                            og_visitpath = os.path.join(
                                original_directory, child, visit.lower()
                            )
                        else:
                            continue
                        sss_list = [
                            directory
                            for directory in next(os.walk(og_visitpath))[1]
                            if re.findall("SSS|sss", directory)
                        ]
                        if seals:
                            visitnum = visit.split("v")[-1]
                        else:
                            visitnum = visit.split(" ")[-1]
                        child_list = child_dict[child]
                        if not (os.path.isdir(og_stocsvisitpath)):
                            temp_visit = child_list[0] + "v" + visitnum
                            og_stocsvisitpath = os.path.join(
                                stocs_directory, child, temp_visit
                            )
                        if (not os.path.isdir(og_stocsvisitpath)) and (
                            len(child_list) > 1
                        ):
                            temp_visit = child_list[1] + "v" + visitnum
                            og_stocsvisitpath = os.path.join(
                                stocs_directory, child, temp_visit
                            )
                        if (not os.path.isdir(og_stocsvisitpath)) and (
                            len(child_list) > 2
                        ):
                            temp_visit = child_list[2] + "v" + visitnum
                            og_stocsvisitpath = os.path.join(
                                stocs_directory, child, temp_visit
                            )
                        if (os.path.isdir(og_visitpath)) and (
                            os.path.isdir(og_stocsvisitpath)
                        ):
                            if len(sss_list) != 0:
                                og_ssspath = os.path.join(og_visitpath, sss_list[0])
                                for wav in os.listdir(og_ssspath):
                                    if os.path.isfile(os.path.join(sss_path, wav)):
                                        update_output(
                                            f"\n{child}, {wav}, file already exists"
                                        )
                                        continue
                                    if len(os.listdir(sss_path)) > 2:
                                        update_output(
                                            f"\n{child}, {wav}, uncopied, sufficient files"
                                        )
                                        continue
                                    update_output(f"\n{child}, {wav}, copied!")
                                    shutil.copy(os.path.join(og_ssspath, wav), sss_path)
                                    filecount += 1
                            stocs_list = [
                                directory
                                for directory in next(os.walk(og_stocsvisitpath))[1]
                                if re.findall("STOCS|stocs|TOCSS|stocss", directory)
                            ]
                            if len(stocs_list) == 0:
                                continue
                            og_stocspath = os.path.join(
                                og_stocsvisitpath, stocs_list[0]
                            )
                            if len(stocs_list) != 0:
                                stoc_dict = {2: [], 3: [], 4: [], 5: [], 6: [], 7: []}
                                for wav in os.listdir(og_stocspath):
                                    wavnum = wav.split("s")[-1][0]
                                    try:
                                        if wavnum.isdigit():
                                            if int(wavnum) == 0:
                                                wavnum = wav.split("S")[-1][0]
                                            stoc_dict[int(wavnum)].append(wav)
                                    except ValueError:
                                        continue
                                stoc_dict_copy = stoc_dict.copy()
                                for key, value in stoc_dict_copy.items():
                                    last_key = list(stoc_dict.keys())[-1]
                                    last_len = len(stoc_dict[last_key])
                                    if last_len < 7:
                                        del stoc_dict[last_key]
                                if len(list(stoc_dict.keys())) > 1:
                                    try:
                                        longest_wavs = random.sample(
                                            stoc_dict[list(stoc_dict.keys())[-1]], 7
                                        )
                                        second_longest_wavs = random.sample(
                                            stoc_dict[list(stoc_dict.keys())[-2]], 5
                                        )
                                        for selwav in longest_wavs:
                                            if os.path.isfile(
                                                os.path.join(long_path, selwav)
                                            ):
                                                update_output(
                                                    f"\n{child}, {selwav}, file already exists"
                                                )
                                                continue
                                            if len(os.listdir(long_path)) > 6:
                                                update_output(
                                                    f"\n{child}, {selwav}, uncopied, sufficient files"
                                                )
                                                continue
                                            update_output(
                                                f"\n{child}, {selwav}, copied!"
                                            )
                                            shutil.copy(
                                                os.path.join(og_stocspath, selwav),
                                                long_path,
                                            )
                                            filecount += 1
                                        for selwav in second_longest_wavs:
                                            if os.path.isfile(
                                                os.path.join(short_path, selwav)
                                            ):
                                                update_output(
                                                    f"\n{child}, {selwav}, file already exists"
                                                )
                                                continue
                                            if len(os.listdir(short_path)) > 4:
                                                update_output(
                                                    f"\n{child}, {selwav}, uncopied, sufficient files"
                                                )
                                                continue
                                            update_output(
                                                f"\n{child}, {selwav}, copied!"
                                            )
                                            shutil.copy(
                                                os.path.join(og_stocspath, selwav),
                                                short_path,
                                            )
                                            filecount += 1
                                    except ValueError:
                                        update_output(
                                            f"\n{child}, {visit}, Value Error in Sampling"
                                        )
                                        continue
                        else:
                            continue
            else:
                # Handling the TD Data Case
                for child in next(os.walk(new_directory))[1]:
                    childpath = os.path.join(new_directory, child)
                    long_path = os.path.join(childpath, "Visit 01", "Long STOCS")
                    short_path = os.path.join(childpath, "Visit 01", "Short STOCS")
                    sss_path = os.path.join(childpath, "Visit 01", "SSS")
                    og_childpath = os.path.join(original_directory, child)
                    og_stocschildpath = os.path.join(stocs_directory, child)
                    if (os.path.isdir(og_childpath)) and (
                        os.path.isdir(og_stocschildpath)
                    ):
                        sss_list = [
                            directory
                            for directory in next(os.walk(og_childpath))[1]
                            if re.findall("SSS|sss", directory)
                        ]
                        if len(sss_list) != 0:
                            og_ssspath = os.path.join(og_childpath, sss_list[0])
                            for wav in os.listdir(og_ssspath):
                                if os.path.isfile(os.path.join(sss_path, wav)):
                                    update_output(
                                        f"\n{child}, {wav}, file already exists"
                                    )
                                    continue
                                if len(os.listdir(sss_path)) > 2:
                                    update_output(
                                        f"\n{child}, {wav}, uncopied, sufficient files"
                                    )
                                    continue
                                update_output(f"\n{child}, {wav}, copied!")
                                shutil.copy(os.path.join(og_ssspath, wav), sss_path)
                                filecount += 1
                        stocs_list = [
                            directory
                            for directory in next(os.walk(og_stocschildpath))[1]
                            if re.findall("STOCS|stocs|TOCSS|stocss", directory)
                        ]
                        if len(stocs_list) == 0:
                            continue
                        og_stocspath = os.path.join(og_stocschildpath, stocs_list[0])
                        if len(stocs_list) != 0:
                            stoc_dict = {2: [], 3: [], 4: [], 5: [], 6: [], 7: []}
                            for wav in os.listdir(og_stocspath):
                                wavnum = wav.split("s")[-1][0]
                                try:
                                    if wavnum.isdigit():
                                        if int(wavnum) == 0:
                                            wavnum = wav.split("S")[-1][0]
                                        stoc_dict[int(wavnum)].append(wav)
                                except ValueError:
                                    continue
                            stoc_dict_copy = stoc_dict.copy()
                            for key, value in stoc_dict_copy.items():
                                last_key = list(stoc_dict.keys())[-1]
                                last_len = len(stoc_dict[last_key])
                                if last_len < 7:
                                    del stoc_dict[last_key]
                            if len(list(stoc_dict.keys())) > 1:
                                longest_wavs = random.sample(
                                    stoc_dict[list(stoc_dict.keys())[-1]], 7
                                )
                                second_longest_wavs = random.sample(
                                    stoc_dict[list(stoc_dict.keys())[-2]], 5
                                )
                                for selwav in longest_wavs:
                                    if os.path.isfile(os.path.join(long_path, selwav)):
                                        update_output(
                                            f"\n{child}, {selwav}, file already exists"
                                        )
                                        continue
                                    if len(os.listdir(long_path)) > 6:
                                        update_output(
                                            f"\n{child}, {selwav}, uncopied, sufficient files"
                                        )
                                        continue
                                    update_output(f"\n{child}, {selwav}, copied!")
                                    shutil.copy(
                                        os.path.join(og_stocspath, selwav), long_path
                                    )
                                    filecount += 1
                                for selwav in second_longest_wavs:
                                    if os.path.isfile(os.path.join(short_path, selwav)):
                                        update_output(
                                            f"\n{child}, {selwav}, file already exists"
                                        )
                                        continue
                                    if len(os.listdir(short_path)) > 4:
                                        update_output(
                                            f"\n{child}, {selwav}, uncopied, sufficient files"
                                        )
                                        continue
                                    update_output(f"\n{child}, {selwav}, copied!")
                                    shutil.copy(
                                        os.path.join(og_stocspath, selwav), short_path
                                    )
                                    filecount += 1
                    else:
                        continue
            return filecount

        def handle_dataclick(e):
            update_output("\nInitiating folder sync with AVA.", replace=True)
            page.close(dataClickDialog)
            ### Syncing directories
            update_output("\nSyncing directories in speech_data-CP1 to AVA...")
            dircount_cp1 = create_directories(
                get_directorypath(r"Y:\CHILD CP RSCH\SESSION SPEECH RECORDINGS\CP.1"),
                get_directorypath(r"Y:\CHILD TD RSCH\PRP\Data\CP"),
            )
            update_output("\nSyncing directories in speech_data-CP2 to AVA...")
            dircount_cp2 = create_directories(
                get_directorypath(r"Y:\CHILD CP RSCH\SESSION SPEECH RECORDINGS\CP.2"),
                get_directorypath(r"Y:\CHILD TD RSCH\PRP\Data\CP"),
            )
            update_output("\nSyncing directories in speech_data-SEALS to AVA...")
            dircount_seals = create_directories(
                get_directorypath(r"Y:\CHILD CP RSCH\SESSION SPEECH RECORDINGS\SEALS"),
                get_directorypath(r"Y:\CHILD TD RSCH\PRP\Data\CP"),
            )
            update_output("\nSyncing directories in speech_data-TD to AVA...")
            dircount_td = create_directories(
                get_directorypath(
                    r"Y:\CHILD TD RSCH\SPEECH SAMPLES\Final perception experiment audio files"
                ),
                get_directorypath(r"Y:\CHILD TD RSCH\PRP\Data\TD"),
            )
            filecount_td = create_files(
                get_directorypath(
                    "Y:\\CHILD TD RSCH\\SPEECH SESSION RECORDINGS\\2 year olds"
                ),
                get_directorypath(
                    "Y:\\CHILD TD RSCH\\SPEECH SAMPLES\\Final perception experiment audio files"
                ),
                get_directorypath("Y:\\CHILD TD RSCH\\PRP\\Data\\TD"),
            )
            filecount_td += create_files(
                get_directorypath(
                    "Y:\\CHILD TD RSCH\\SPEECH SESSION RECORDINGS\\3 year olds"
                ),
                get_directorypath(
                    "Y:\\CHILD TD RSCH\\SPEECH SAMPLES\\Final perception experiment audio files"
                ),
                get_directorypath("Y:\\CHILD TD RSCH\\PRP\\Data\\TD"),
            )
            filecount_td += create_files(
                get_directorypath(
                    "Y:\\CHILD TD RSCH\\SPEECH SESSION RECORDINGS\\4 year olds"
                ),
                get_directorypath(
                    "Y:\\CHILD TD RSCH\\SPEECH SAMPLES\\Final perception experiment audio files"
                ),
                get_directorypath("Y:\\CHILD TD RSCH\\PRP\\Data\\TD"),
            )
            filecount_td += create_files(
                get_directorypath(
                    "Y:\\CHILD TD RSCH\\SPEECH SESSION RECORDINGS\\5 year olds"
                ),
                get_directorypath(
                    "Y:\\CHILD TD RSCH\\SPEECH SAMPLES\\Final perception experiment audio files"
                ),
                get_directorypath("Y:\\CHILD TD RSCH\\PRP\\Data\\TD"),
            )
            filecount_td += create_files(
                get_directorypath(
                    "Y:\\CHILD TD RSCH\\SPEECH SESSION RECORDINGS\\6 year olds"
                ),
                get_directorypath(
                    "Y:\\CHILD TD RSCH\\SPEECH SAMPLES\\Final perception experiment audio files"
                ),
                get_directorypath("Y:\\CHILD TD RSCH\\PRP\\Data\\TD"),
            )
            filecount_td += create_files(
                get_directorypath(
                    "Y:\\CHILD TD RSCH\\SPEECH SESSION RECORDINGS\\7 year olds"
                ),
                get_directorypath(
                    "Y:\\CHILD TD RSCH\\SPEECH SAMPLES\\Final perception experiment audio files"
                ),
                get_directorypath("Y:\\CHILD TD RSCH\\PRP\\Data\\TD"),
            )
            filecount_td += create_files(
                get_directorypath(
                    "Y:\\CHILD TD RSCH\\SPEECH SESSION RECORDINGS\\8 year olds"
                ),
                get_directorypath(
                    "Y:\\CHILD TD RSCH\\SPEECH SAMPLES\\Final perception experiment audio files"
                ),
                get_directorypath("Y:\\CHILD TD RSCH\\PRP\\Data\\TD"),
            )
            filecount_td += create_files(
                get_directorypath(
                    "Y:\\CHILD TD RSCH\\SPEECH SESSION RECORDINGS\\9 year olds"
                ),
                get_directorypath(
                    "Y:\\CHILD TD RSCH\\SPEECH SAMPLES\\Final perception experiment audio files"
                ),
                get_directorypath("Y:\\CHILD TD RSCH\\PRP\\Data\\TD"),
            )
            filecount_td += create_files(
                get_directorypath(
                    "Y:\\CHILD TD RSCH\\SPEECH SESSION RECORDINGS\\10 year olds"
                ),
                get_directorypath(
                    "Y:\\CHILD TD RSCH\\SPEECH SAMPLES\\Final perception experiment audio files"
                ),
                get_directorypath("Y:\\CHILD TD RSCH\\PRP\\Data\\TD"),
            )
            filecount_td += create_files(
                get_directorypath(
                    "Y:\\CHILD TD RSCH\\SPEECH SESSION RECORDINGS\\11 year olds"
                ),
                get_directorypath(
                    "Y:\\CHILD TD RSCH\\SPEECH SAMPLES\\Final perception experiment audio files"
                ),
                get_directorypath("Y:\\CHILD TD RSCH\\PRP\\Data\\TD"),
            )
            filecount_td += create_files(
                get_directorypath(
                    "Y:\\CHILD TD RSCH\\SPEECH SESSION RECORDINGS\\12 year olds"
                ),
                get_directorypath(
                    "Y:\\CHILD TD RSCH\\SPEECH SAMPLES\\Final perception experiment audio files"
                ),
                get_directorypath("Y:\\CHILD TD RSCH\\PRP\\Data\\TD"),
            )
            filecount_td += create_files(
                get_directorypath(
                    "Y:\\CHILD TD RSCH\\SPEECH SESSION RECORDINGS\\13 year olds"
                ),
                get_directorypath(
                    "Y:\\CHILD TD RSCH\\SPEECH SAMPLES\\Final perception experiment audio files"
                ),
                get_directorypath("Y:\\CHILD TD RSCH\\PRP\\Data\\TD"),
            )
            filecount_td += create_files(
                get_directorypath(
                    "Y:\\CHILD TD RSCH\\SPEECH SESSION RECORDINGS\\14 year olds"
                ),
                get_directorypath(
                    "Y:\\CHILD TD RSCH\\SPEECH SAMPLES\\Final perception experiment audio files"
                ),
                get_directorypath("Y:\\CHILD TD RSCH\\PRP\\Data\\TD"),
            )
            filecount_cp1 = create_files(
                get_directorypath("Y:\\CHILD CP RSCH\\SESSION SPEECH RECORDINGS\\CP.1"),
                get_directorypath(
                    "Y:\\CHILD CP RSCH\\SPEECH SAMPLES\\Final perception experiment audio files\\CP1"
                ),
                get_directorypath("Y:\\CHILD TD RSCH\\PRP\\Data\\CP"),
            )
            filecount_cp2 = create_files(
                get_directorypath("Y:\\CHILD CP RSCH\\SESSION SPEECH RECORDINGS\\CP.2"),
                get_directorypath(
                    "Y:\\CHILD CP RSCH\\SPEECH SAMPLES\\Final perception experiment audio files\\CP2"
                ),
                get_directorypath("Y:\\CHILD TD RSCH\\PRP\\Data\\CP"),
            )
            filecount_seals = create_files(
                get_directorypath("Y:\\CHILD CP RSCH\\SESSION SPEECH RECORDINGS\\SEALS"),
                get_directorypath(
                    "Y:\\CHILD CP RSCH\\SPEECH SAMPLES\\Final perception experiment audio files\\SEALS"
                ),
                get_directorypath("Y:\\CHILD TD RSCH\\PRP\\Data\\CP"),
            )
            update_output(f"\n{dircount_cp1} new directories from CP1 copied!")
            update_output(f"\n{dircount_cp2} new directories from CP2 copied!")
            update_output(f"\n{dircount_seals} new directories from SEALS copied!")
            update_output(f"\n{dircount_td} new directories from TD copied!")
            update_output(f"\n{filecount_cp1} new files from CP1 copied!")
            update_output(f"\n{filecount_cp2} new files from CP2 copied!")
            update_output(f"\n{filecount_seals} new files from SEALS copied!")
            update_output(f"\n{filecount_td} new files from TD copied!")
            update_output("\nSyncing database file to AVA file directories...")
            init_db(page, update_output, util_tab, "Data", False)
            update_output("\nDatabase sync complete!")
            # backup_database()
            page.open(
                ft.AlertDialog(
                    title=ft.Text("AVA data was successfully updated."),
                    content=ft.Text("Click anywhere to continue."),
                )
            )
            update_output("\nAVA data was successfully updated.")

        dataClickDialog = ft.AlertDialog(
            modal=True,
            title=ft.Text("AVA Data Update Confirmation"),
            content=ft.Text(
                "Running the following process may take a long amount of time. It will clear any existing outputs in the right output panel and may disrupt other workers. \n\
The process will sync AVA with any new SSS or TOCS files which have been added to the CP/TD data folders in speech_data. \n\
The backup of the AVA database (located in the utils folder) will also be updated. \n\
It is recommended to run this process only when you are sure others are not working with AVA."
            ),
            actions=[
                ft.TextButton("Continue", on_click=handle_dataclick),
                ft.TextButton("Cancel", on_click=handle_close),
            ],
            actions_alignment=ft.MainAxisAlignment.END,
            on_dismiss=handle_close,
        )
        page.open(dataClickDialog)
        page.update()

    def updateVettedClick(e):
        def handle_close(e):
            lines = []
            current_time_central = datetime.now(central_timezone)
            vetted_data_time_stamp = current_time_central.strftime("%m-%d-%y")
            lines.append(ava_data_time_stamp + "\n")
            lines.append(vetted_data_time_stamp)
            with open(timestamp_paths, "w") as f:
                f.writelines(lines)
            page.close(vettedClickDialog)

        def handle_vettedclick(e):
            update_output("\nInitiating vetted data folder sync.", replace=True)
            page.close(vettedClickDialog)
            conn = make_conn()
            count = 0
            ### Copy completed files to the Vetted Data directory
            update_output("\nCopying files to the vetted data directory...")
            df = pd.read_sql_query(
                """
                SELECT FilePath FROM Files
                WHERE FileStatus = 'Complete'
                """,
                conn,
            )
            vetted_path = get_directorypath("Y:\\CHILD TD RSCH\\PRP\\Vetted Data")
            
            child_dict = {}
            with open(
                os.path.join(
                    get_directorypath("Y:\\CHILD TD RSCH\\PRP"), "child_dict.csv"
                ),
                encoding="utf-8",
            ) as file:
                reader = csv.reader(file)
                for row in reader:
                    if row:
                        while row and row[-1] == "":
                            row.pop()
                        key = row[0]
                        value = row[-1]
                        child_dict[key] = value.strip()

            def convert_to_abbrev(pathlist):
                if pathlist[-5] == "TD":
                    return os.path.join(
                        vetted_path,
                        pathlist[-5],
                        pathlist[-4],
                        pathlist[-3],
                        pathlist[-2],
                    )
                else:
                    return os.path.join(
                        vetted_path,
                        pathlist[-5],
                        child_dict[pathlist[-4]],
                        pathlist[-3],
                        pathlist[-2],
                    )

            total = len(df["FilePath"].tolist())
            count = 0
            for path in reversed(df["FilePath"].tolist()):
                pathlist = path.split(os.sep)
                newdir = convert_to_abbrev(pathlist)
                if newdir == None:
                    continue
                if not os.path.exists(newdir):
                    base = os.path.basename(newdir)
                    if (base not in ["Long STOCS", "Short STOCS", "SSS"]):
                        if "Visit" in base:
                            update_output(f"\nCopying new directory - {newdir.split(os.sep)[-2]} - {base}")
                        else:
                            update_output(f"\nCopying new directory - {base}")
                    os.makedirs(newdir)
                try:
                    src = os.path.join(get_directorypath(os.path.dirname(path)), os.path.basename(path))
                    dst = os.path.join(newdir, pathlist[-1])
                    if not os.path.exists(dst):
                        shutil.copy(src, dst)
                    elif not filecmp.cmp(src, dst, shallow=False):
                        shutil.copy(src, dst)
                except TypeError:
                    update_output(f"\nFile not copied - {os.path.basename(path)}")
                count += 1
                update_output(f"\n{round((count/total)*100, 2)}% {count}/{total} {os.path.basename(path)}")
            ### Delete flagged files from the Vetted Data directory
            update_output("\nRemoving flagged files from the vetted data directory...")
            df = pd.read_sql_query(
                """
                SELECT FilePath FROM Files
                WHERE FileStatus = 'Flagged'
                """,
                conn,
            )
            for path in df["FilePath"].tolist():
                newdir = os.path.join(
                    vetted_path,
                    pathlist[-5],
                    pathlist[-4],
                    pathlist[-3],
                    pathlist[-2],
                )
                newpath = os.path.join(newdir, pathlist[-1])
                if os.path.exists(newpath):
                    os.remove(newpath)

            ### Remove visits from Vetted Data without the correct number of files
            update_output("\nDealing with folders with incorrect amounts of files...")
            for root, _, files in os.walk(vetted_path):
                root_list = root.split(os.sep)
                if "Visit" in root_list[-1]:
                    try:
                        longstocs_count = len(
                            os.listdir(os.path.join(root, "Long STOCS"))
                        )
                        shorstocs_count = len(
                            os.listdir(os.path.join(root, "Short STOCS"))
                        )
                        sss_count = len(os.listdir(os.path.join(root, "SSS")))
                        subdir_count = len(os.listdir(root))
                    except FileNotFoundError:
                        shutil.rmtree(root)
                        continue
                    if (
                        (longstocs_count != 7)
                        | (shorstocs_count != 5)
                        | (sss_count != 2)
                        | (subdir_count != 3)
                        | (root_list[-2] == "TD")
                        | (root_list[-2] == "CP")
                    ):
                        shutil.rmtree(root)
                    else:
                        update_output(
                            f"\n{root_list[-2]}, {root_list[-1]} confirmed vetted and in vetted folder."
                        )
                        count += 1
            ### Removes child folders without any visits in them
            update_output("\nDealing with child folders without subfolders...")
            for root, dirs, _ in os.walk(vetted_path):
                for dir_name in dirs:
                    dir_path = os.path.join(root, dir_name)
                    if not os.listdir(dir_path):  # Check if directory is empty
                        os.rmdir(dir_path)
            ### Adding silence to files that don't have silence yet
            update_output("\nAdding silence...")
            add_silence()
            backup_database()
            page.open(
                ft.AlertDialog(
                    title=ft.Text("Vetted data folder was successfully updated."),
                    content=ft.Text("Click anywhere to continue."),
                )
            )
            update_output(
                f"\nTotal number of vetted files - {count}."
            )
            update_output("\nVetted data folder was successfully updated.")

        vettedClickDialog = ft.AlertDialog(
            modal=True,
            title=ft.Text("Vetted Data Folder Update Confirmation"),
            content=ft.Text(
                "Running the following process may take a long amount of time. It will clear any existing outputs in the right output panel and may disrupt other workers. \n\
                The process will copy any newly vetted files from the Data folder (where all AVA files reside) to the Vetted Data folder (where only completed files reside). \n\
                The backup of the AVA database (located in the utils folder) will also be updated. \n\
                It is recommended to run this process only when you are sure others are not working with AVA."
            ),
            actions=[
                ft.TextButton("Continue", on_click=handle_vettedclick),
                ft.TextButton("Cancel", on_click=handle_close),
            ],
            actions_alignment=ft.MainAxisAlignment.END,
            on_dismiss=handle_close,
        )
        page.open(vettedClickDialog)
        page.update()

    def generateProgressReport(e):
        def handle_close(e):
            page.close(progressClickDialog)

        def handle_progressclick(e):
            conn = make_conn()
            update_output("\nPROGRESS REPORT:", replace=True)
            update_output("\nProcessing Report...")
            page.close(progressClickDialog)
            df = pd.read_sql_query(
                """
                SELECT * FROM Folders
                """,
                conn,
            )
            worker_df = pd.read_sql_query(
                """
                SELECT * FROM Files
                LEFT JOIN Workers
                ON Files.WorkerID = Workers.WorkerID
                WHERE Files.WorkerID IS NOT NULL
                """,
                conn,
            )
            file_df = pd.read_sql_query(
                """
                SELECT * FROM Files
                LEFT JOIN Folders
                ON Files.FolderID = Folders.FolderID
                WHERE TotalFiles = 14 OR TotalFiles = 15
                """,
                conn,
            )
            total_visits = len(df)
            visits0 = len(df[df["TotalFiles"] == 0])
            visits3 = len(df[df["TotalFiles"] == 3])
            visits12 = len(df[df["TotalFiles"] == 12])
            visits14 = len(df[df["TotalFiles"] == 14])
            visits15 = len(df[df["TotalFiles"] == 15])
            other = len(df[~df["TotalFiles"].isin([0, 3, 12, 14, 15])])
            update_output(f"\n\nVisit Report:")
            update_output(f"\nTotal number of visits - {total_visits}")
            update_output(f"\nVisits with 00 Files - {visits0} ({round((visits0/total_visits)*100, 2)}%)")
            update_output(f"\nVisits with 03 Files - {visits3} ({round((visits3/total_visits)*100, 2)}%)")
            update_output(f"\nVisits with 12 Files - {visits12} ({round((visits12/total_visits)*100, 2)}%)")
            update_output(f"\nVisits with 14 Files - {visits14} ({round((visits14/total_visits)*100, 2)}%)")
            update_output(f"\nVisits with 15 Files - {visits15} ({round((visits15/total_visits)*100, 2)}%)")
            update_output(f"\nVisits with Other Numbers of Files - {other} ({round((other/total_visits)*100, 2)}%)")
            update_output(f"\n\nWorker Report:")
            for worker in worker_df["WorkerName"].unique():
                workerlen = len(worker_df[worker_df["WorkerName"] == worker])
                completedlen = len(worker_df[(worker_df["WorkerName"] == worker) & (worker_df["FileStatus"] != "Incomplete")])
                if workerlen != 0:
                    update_output(f"\n{worker} - {completedlen}/{workerlen} files completed ({round((completedlen/workerlen)*100, 2)}%)")
            update_output(f"\n\nFile Report:")
            totalfiles = visits14*14 + visits15*15  
            update_output(f"\nTotal number of files (in visits with 14 or 15) - {totalfiles}")
            completedfiles = len(file_df[(file_df["TotalFiles"].isin([14, 15])) & (worker_df["FileStatus"] != "Incomplete")])
            update_output(f"\nTotal number of files completed - {completedfiles}/{totalfiles} ({round((completedfiles/totalfiles)*100, 2)}%)")
            update_output("\n")
            backup_database()
            page.open(
                ft.AlertDialog(
                    title=ft.Text("Progress report generation completed."),
                    content=ft.Text("Click anywhere to continue."),
                )
            )
            update_output("\nProgress report generation completed.")

        progressClickDialog = ft.AlertDialog(
            modal=True,
            title=ft.Text("Progress Report Generation Confirmation"),
            content=ft.Text(
                "Running the following process may take a long amount of time. It will clear any existing outputs in the right output panel and may disrupt other workers. \n\
The process will generate a report of AVA progress both in terms of which visits have which files and how many of the available files have been vetted. \n\
The backup of the AVA database (located in the utils folder) will also be updated. \n\
It is recommended to run this process only when you are sure others are not working with AVA."
            ),
            actions=[
                ft.TextButton("Continue", on_click=handle_progressclick),
                ft.TextButton("Cancel", on_click=handle_close),
            ],
            actions_alignment=ft.MainAxisAlignment.END,
            on_dismiss=handle_close,
        )
        page.open(progressClickDialog)
        page.update()

    def noOutput():
        page.open(
            ft.AlertDialog(
                title=ft.Text(
                    "File was not succesfully saved - maybe try a different file name."
                )
            )
        )

    def saveOutput(e: ft.FilePickerResultEvent):
        global utility_text
        filepath = e.path
        if os.path.exists(os.path.dirname(filepath)):
            if filepath[-4:] != ".txt":
                filepath = filepath + ".txt"
            if (filepath != "") and (filepath[-4:] == ".txt"):
                with open(filepath, "w", encoding="utf-8", errors="ignore") as file:
                    file.write(utility_text)
                    file.flush()
                if os.path.exists(filepath):
                    page.open(
                        ft.AlertDialog(title=ft.Text("File was successfully saved."))
                    )
                else:
                    page.open(ft.AlertDialog(title=ft.Text("Issue with file write.")))
                page.update()
            else:
                noOutput()
        else:
            noOutput()

    savePicker = ft.FilePicker(on_result=saveOutput)
    page.overlay.append(savePicker)

    util_buttons = ft.Column(
        [
            ft.Text(f"AVA Data Last Updated: {ava_data_time_stamp}", weight=ft.FontWeight.BOLD),
            ft.ElevatedButton(
                content=ft.Container(
                    ft.Text(value="Update AVA Data with New Files and Visits", size=16),
                    padding=ft.padding.all(20),
                ),
                on_click=updateDataClick,
                style=ft.ButtonStyle(
                    shape=ft.RoundedRectangleBorder(radius=5),
                    color=ft.colors.GREEN_900,
                    bgcolor=ft.colors.GREEN_50,
                ),
                width=450,
            ),
            ft.Text(f"Vetted Data Last Updated: {vetted_data_time_stamp}", weight=ft.FontWeight.BOLD),
            ft.ElevatedButton(
                content=ft.Container(
                    ft.Text(
                        value="Update Vetted Data Folder with Completed Files", size=16
                    ),
                    padding=ft.padding.all(20),
                ),
                on_click=updateVettedClick,
                style=ft.ButtonStyle(
                    shape=ft.RoundedRectangleBorder(radius=5),
                    color=ft.colors.GREEN_900,
                    bgcolor=ft.colors.GREEN_50,
                ),
                width=450,
            ),
            ft.ElevatedButton(
                content=ft.Container(
                    ft.Text(value="Generate New Progress Report", size=16),
                    padding=ft.padding.all(20),
                ),
                on_click=generateProgressReport,
                style=ft.ButtonStyle(
                    shape=ft.RoundedRectangleBorder(radius=5),
                    color=ft.colors.GREEN_900,
                    bgcolor=ft.colors.GREEN_50,
                ),
                width=450,
            ),
            ft.ElevatedButton(
                content=ft.Container(
                    ft.Text(value="Save Outputs as a Text File", size=16),
                    padding=ft.padding.all(20),
                ),
                on_click=lambda e: savePicker.save_file(
                    dialog_title="Select Save Location",
                    file_name="output.txt",
                    file_type=ft.FilePickerFileType.CUSTOM,
                    allowed_extensions=["txt"],
                ),
                style=ft.ButtonStyle(
                    shape=ft.RoundedRectangleBorder(radius=5),
                    color=ft.colors.INDIGO_900,
                    bgcolor=ft.colors.INDIGO_50,
                ),
                width=450,
            ),
        ],
        alignment=ft.MainAxisAlignment.CENTER,
        spacing=29,
    )

    util_text = ft.Text(utility_text, weight=ft.FontWeight.BOLD, size=12)

    util_controls = ft.Container(
        ft.Column(
            [util_buttons],
            scroll="auto",
            alignment=ft.MainAxisAlignment.CENTER,
            horizontal_alignment=ft.CrossAxisAlignment.START,
            spacing=20,
        ),
        padding=ft.Padding(100, 50, 50, 50),
    )

    util_output = ft.Container(
        ft.Column(
            [util_text],
            scroll="auto",
            alignment=ft.MainAxisAlignment.CENTER,
            horizontal_alignment=ft.CrossAxisAlignment.START,
            spacing=20,
            auto_scroll=True,
        ),
        padding=ft.Padding(20, 20, 20, 20),
        bgcolor=ft.colors.INDIGO_50,
        width=450,
        height=460,
    )

    util_tab = ft.Row(
        controls=[util_controls, util_output],
        alignment=ft.MainAxisAlignment.CENTER,
        vertical_alignment=ft.CrossAxisAlignment.START,
        spacing=30,
    )
    return util_tab
