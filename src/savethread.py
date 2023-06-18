import os
import pickle
import time

import dill

save_files_dir = "saves"


def save_list_to_pickle(timestamp, data):
    filename = f"data_{timestamp}.pickle"
    with open(filename, "wb") as file:
        pickle.dump(data, file)
    print(f"Saved data to {filename}")


def save_list_to_dill(timestamp, objects):
    filename = f"{os.path.join(save_files_dir, str(timestamp))}.pickle"
    with open(filename, "wb") as file:
        dill.dump(objects, file)
    print(f"Saved game objects to {filename}")


def save_game_periodically(data_list):
    while True:
        current_timestamp = int(time.time())
        save_list_to_dill(current_timestamp, data_list)
        time.sleep(10)

        # Delete all files except for the most recent 5
        print(save_files_dir)
        files = sorted(
            os.listdir(save_files_dir),
            key=lambda x: os.path.getctime(os.path.join(save_files_dir, x)),
        )
        if len(files) > 5:
            for file in files[:-5]:
                print(file)
                os.remove(f"{os.path.join(save_files_dir, file)}")


def load_most_recent_game():
    while True:
        files = os.listdir(save_files_dir)
        files = [file for file in files if file.endswith(".pickle")]
        files = sorted(
            files,
            key=lambda x: os.path.getctime(os.path.join(save_files_dir, x)),
            reverse=True,
        )

        if files:
            most_recent_file = os.path.join(save_files_dir, files[0])
            try:
                with open(most_recent_file, "rb") as file:
                    data = dill.load(file)
            except (dill.UnpicklingError, EOFError) as e:
                os.remove(most_recent_file)
                continue
            return data
        else:
            print("No pickle files found in the directory.")
            return None
