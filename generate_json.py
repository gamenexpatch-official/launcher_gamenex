import os
import json
import dropbox
import subprocess
from datetime import datetime

# =========================
# DROPBOX CONFIG
# =========================
APP_KEY = os.getenv("DROPBOX_APP_KEY")
APP_SECRET = os.getenv("DROPBOX_APP_SECRET")
REFRESH_TOKEN = os.getenv("DROPBOX_REFRESH_TOKEN")

dbx = dropbox.Dropbox(
    oauth2_refresh_token=REFRESH_TOKEN,
    app_key=APP_KEY,
    app_secret=APP_SECRET
)

# =========================
# CONFIG
# =========================
# Jika app Dropbox menggunakan "App Folder",
# biarkan kosong ""
BASE_PATH = ""

OUTPUT_FILE = "facelibrary18.json"

# =========================
# CREATE / GET SHARE LINK
# =========================
def get_or_create_shared_link(path):

    try:
        links = dbx.sharing_list_shared_links(path=path).links

        if links:
            return links[0].url.replace("?dl=0", "?dl=1")

    except Exception as e:
        print(f"⚠️ Shared link check failed: {e}")

    try:
        link = dbx.sharing_create_shared_link_with_settings(path)

        return link.url.replace("?dl=0", "?dl=1")

    except Exception as e:
        print(f"❌ Failed create shared link: {path}")
        print(e)

        return ""

# =========================
# PARSE FOLDER NAME
# FORMAT:
# 47787_Joao Cancelo_Barcelona
# =========================
def parse_folder(folder_name):

    parts = folder_name.split("_")

    if len(parts) < 3:
        return None

    player_id = parts[0].strip()

    if not player_id.isdigit():
        return None

    player_name = parts[1].replace("_", " ").strip()
    club_name = " ".join(parts[2:]).replace("_", " ").strip()

    return player_id, player_name, club_name

# =========================
# GET ALL ENTRIES
# =========================
def get_all_entries(path=""):

    entries = []

    try:
        result = dbx.files_list_folder(path)

        entries.extend(result.entries)

        while result.has_more:
            result = dbx.files_list_folder_continue(result.cursor)
            entries.extend(result.entries)

    except Exception as e:
        print(f"❌ Failed read Dropbox folder: {e}")

    return entries

# =========================
# AUTO GIT COMMIT PUSH
# =========================
def git_commit_push():

    try:

        print("\n🚀 START AUTO GITHUB PUSH...")

        # CONFIG GIT BOT
        subprocess.run(
            ["git", "config", "user.name", "gamenex-bot"],
            check=True
        )

        subprocess.run(
            ["git", "config", "user.email", "bot@gamenex.com"],
            check=True
        )

        # GIT ADD
        subprocess.run(
            ["git", "add", OUTPUT_FILE],
            check=True
        )

        # CHECK CHANGES
        result = subprocess.run(
            ["git", "diff", "--cached", "--quiet"]
        )

        # NO CHANGES
        if result.returncode == 0:
            print("ℹ️ No changes detected")
            return

        # COMMIT MESSAGE
        commit_msg = (
            f"auto update facelibrary18 "
            f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        )

        # COMMIT
        subprocess.run(
            ["git", "commit", "-m", commit_msg],
            check=True
        )

        # PUSH
        subprocess.run(
            ["git", "push"],
            check=True
        )

        print("✅ GITHUB PUSH SUCCESS!")

    except subprocess.CalledProcessError as e:

        print("❌ GITHUB PUSH FAILED")
        print(e)

# =========================
# MAIN
# =========================
def main():

    players = []
    existing_ids = set()

    print("🚀 START SCAN DROPBOX...\n")

    entries = get_all_entries(BASE_PATH)

    print(f"📂 Total entries found: {len(entries)}\n")

    for entry in entries:

        # HANYA FOLDER
        if not isinstance(entry, dropbox.files.FolderMetadata):
            continue

        folder_name = entry.name
        folder_path = entry.path_lower

        print(f"📂 FOUND: {folder_name}")

        parsed = parse_folder(folder_name)

        if not parsed:
            print(f"⚠️ Skip invalid folder format: {folder_name}\n")
            continue

        player_id, player_name, club_name = parsed

        # DUPLICATE CHECK
        if player_id in existing_ids:
            print(f"⚠️ Duplicate ID: {player_id}")
            continue

        existing_ids.add(player_id)

        # =========================
        # GET FILES INSIDE FOLDER
        # =========================
        try:
            files = get_all_entries(folder_path)

        except Exception as e:
            print(f"❌ Failed open folder: {folder_name}")
            print(e)
            continue

        image_url = ""
        zip_url = ""

        for f in files:

            if not isinstance(f, dropbox.files.FileMetadata):
                continue

            file_name = f.name.lower()

            print(f"   📄 {file_name}")

            # IMAGE
            if (
                file_name.endswith(".png")
                or file_name.endswith(".jpg")
                or file_name.endswith(".jpeg")
            ):

                image_url = get_or_create_shared_link(f.path_lower)

            # ZIP
            elif file_name.endswith(".zip"):

                zip_url = get_or_create_shared_link(f.path_lower)

        # =========================
        # VALIDATION
        # =========================
        if not image_url:
            print(f"⚠️ Missing image file in: {folder_name}")

        if not zip_url:
            print(f"⚠️ Missing zip file in: {folder_name}")

        if not image_url or not zip_url:
            print("⏭️ Skip folder\n")
            continue

        # =========================
        # ADD PLAYER
        # =========================
        players.append({
            "id": player_id,
            "version": "v1",
            "name": player_name,
            "club": club_name,
            "image": image_url,
            "zip_url": zip_url
        })

        print(f"✅ SUCCESS: {player_id} - {player_name}\n")

    # =========================
    # SORT DATA
    # =========================
    players.sort(key=lambda x: int(x["id"]))

    # =========================
    # SAVE JSON
    # =========================
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:

        json.dump(
            players,
            f,
            indent=4,
            ensure_ascii=False
        )

    print("\n===================================")
    print(f"✅ TOTAL PLAYER: {len(players)}")
    print(f"✅ JSON SAVED: {OUTPUT_FILE}")
    print("🚀 AUTO DROPBOX SYNC COMPLETE!")
    print("===================================")

    # =========================
    # AUTO PUSH GITHUB
    # =========================
    git_commit_push()

# =========================
# RUN
# =========================
if __name__ == "__main__":
    main()
