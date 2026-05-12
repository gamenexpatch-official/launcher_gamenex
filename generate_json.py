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
BASE_PATH = ""

OUTPUT_FILE = "facelibrary18.json"

# =========================
# FIX DROPBOX DIRECT LINK
# =========================
def fix_dropbox_link(url):

    # ubah dl=0 jadi dl=1
    if "dl=0" in url:
        url = url.replace("dl=0", "dl=1")

    # jika belum ada dl parameter
    elif "dl=1" not in url:

        if "?" in url:
            url += "&dl=1"
        else:
            url += "?dl=1"

    return url

# =========================
# CREATE / GET SHARE LINK
# =========================
def get_or_create_shared_link(path):

    try:

        links = dbx.sharing_list_shared_links(
            path=path
        ).links

        if links:

            return fix_dropbox_link(
                links[0].url
            )

    except Exception as e:

        print(f"⚠️ Shared link check failed: {e}")

    try:

        link = dbx.sharing_create_shared_link_with_settings(
            path
        )

        return fix_dropbox_link(
            link.url
        )

    except Exception as e:

        print(f"❌ Failed create shared link: {path}")
        print(e)

        return ""

# =========================
# GET ALL ENTRIES
# =========================
def get_all_entries(path=""):

    entries = []

    try:

        result = dbx.files_list_folder(path)

        entries.extend(result.entries)

        while result.has_more:

            result = dbx.files_list_folder_continue(
                result.cursor
            )

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

        subprocess.run(
            ["git", "config", "user.name", "gamenex-bot"],
            check=True
        )

        subprocess.run(
            ["git", "config", "user.email", "bot@gamenex.com"],
            check=True
        )

        subprocess.run(
            ["git", "add", OUTPUT_FILE],
            check=True
        )

        result = subprocess.run(
            ["git", "diff", "--cached", "--quiet"]
        )

        # tidak ada perubahan
        if result.returncode == 0:

            print("ℹ️ No changes detected")
            return

        commit_msg = (
            f"auto update facelibrary18 "
            f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        )

        subprocess.run(
            ["git", "commit", "-m", commit_msg],
            check=True
        )

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

    print("🚀 START SCAN DROPBOX...\n")

    # =========================
    # LOAD OLD JSON
    # =========================
    old_players = {}

    if os.path.exists(OUTPUT_FILE):

        with open(
            OUTPUT_FILE,
            "r",
            encoding="utf-8"
        ) as f:

            try:

                data = json.load(f)

                for item in data:

                    old_players[item["id"]] = item

            except:

                pass

    print(f"📦 OLD DATA: {len(old_players)}")

    # =========================
    # SCAN DROPBOX
    # =========================
    entries = get_all_entries(BASE_PATH)

    print(
        f"📂 TOTAL DROPBOX FOLDERS: {len(entries)}\n"
    )

    for entry in entries:

        # hanya folder
        if not isinstance(
            entry,
            dropbox.files.FolderMetadata
        ):
            continue

        folder_name = entry.name
        folder_path = entry.path_lower

        print(f"📂 FOUND: {folder_name}")

        # =========================
        # FLEXIBLE PARSE
        # =========================
        parts = folder_name.split("_")

        if len(parts) < 2:

            print("⚠️ INVALID FOLDER")
            continue

        player_id = parts[0].strip()

        if not player_id.isdigit():

            print("⚠️ INVALID ID")
            continue

        player_name = parts[1].strip()

        club_name = ""

        if len(parts) >= 3:

            club_name = " ".join(
                parts[2:]
            ).strip()

        # =========================
        # READ FILES
        # =========================
        files = get_all_entries(folder_path)

        image_url = ""
        zip_url = ""

        for f in files:

            if not isinstance(
                f,
                dropbox.files.FileMetadata
            ):
                continue

            file_name = f.name.lower()

            print(f"   📄 {file_name}")

            # IMAGE
            if (
                file_name.endswith(".png")
                or file_name.endswith(".jpg")
                or file_name.endswith(".jpeg")
            ):

                image_url = get_or_create_shared_link(
                    f.path_lower
                )

            # ZIP
            elif file_name.endswith(".zip"):

                zip_url = get_or_create_shared_link(
                    f.path_lower
                )

        # =========================
        # SKIP INVALID
        # =========================
        if not image_url or not zip_url:

            print("⏭️ Missing image/zip")
            continue

        # =========================
        # UPDATE / ADD
        # =========================
        old_players[player_id] = {

            "id": player_id,
            "version": "v1",
            "name": player_name,
            "club": club_name,
            "image": image_url,
            "zip_url": zip_url,
            "updated_at": datetime.now().strftime(
                "%Y-%m-%d %H:%M:%S"
            )
        }

        print(f"✅ UPDATED: {player_id}")

    # =========================
    # CONVERT TO LIST
    # =========================
    players = list(
        old_players.values()
    )

    # SORT
    players.sort(
        key=lambda x: int(x["id"])
    )

    # =========================
    # SAVE JSON
    # =========================
    with open(
        OUTPUT_FILE,
        "w",
        encoding="utf-8"
    ) as f:

        json.dump(
            players,
            f,
            indent=4,
            ensure_ascii=False
        )

    print("\n===================================")
    print(f"✅ TOTAL PLAYER: {len(players)}")
    print(f"✅ JSON SAVED: {OUTPUT_FILE}")
    print("🚀 UPDATE COMPLETE!")
    print("===================================")

    # =========================
    # AUTO PUSH
    # =========================
    git_commit_push()

# =========================
# RUN
# =========================
if __name__ == "__main__":
    main()
