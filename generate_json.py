import os
import json
import dropbox

ACCESS_TOKEN = os.getenv("DROPBOX_TOKEN")
BASE_PATH = ""
OUTPUT_FILE = "facelibrary18.json"

dbx = dropbox.Dropbox(ACCESS_TOKEN)

def get_or_create_shared_link(path):
    try:
        links = dbx.sharing_list_shared_links(path=path).links
        if links:
            return links[0].url.replace("dl=0", "dl=1")
    except:
        pass

    try:
        link = dbx.sharing_create_shared_link_with_settings(path)
        return link.url.replace("dl=0", "dl=1")
    except Exception as e:
        print(f"❌ Gagal share: {path} | {e}")
        return ""

def parse_folder(name):
    parts = name.split("_")
    if len(parts) < 3:
        return None

    player_id = parts[0]
    if not player_id.isdigit():
        return None

    name = parts[1]
    club = " ".join(parts[2:])

    return player_id, name, club

def main():
    players = []

    result = dbx.files_list_folder(BASE_PATH)

    for entry in result.entries:
        if not isinstance(entry, dropbox.files.FolderMetadata):
            continue

        folder_name = entry.name
        folder_path = entry.path_lower

        parsed = parse_folder(folder_name)
        if not parsed:
            print(f"⚠️ Skip: {folder_name}")
            continue

        player_id, name, club = parsed

        files = dbx.files_list_folder(folder_path).entries

        image_url = ""
        zip_url = ""

        for f in files:
            if isinstance(f, dropbox.files.FileMetadata):
                if f.name.lower().endswith(".png"):
                    image_url = get_or_create_shared_link(f.path_lower)
                elif f.name.lower().endswith(".zip"):
                    zip_url = get_or_create_shared_link(f.path_lower)

        if not image_url or not zip_url:
            print(f"⚠️ File kurang: {folder_name}")
            continue

        players.append({
            "id": player_id,
            "version": "v1",
            "name": name,
            "club": club,
            "image": image_url,
            "zip_url": zip_url
        })

        print(f"✅ {player_id} - {name}")

    players.sort(key=lambda x: int(x["id"]))

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(players, f, indent=4, ensure_ascii=False)

    print("\n🚀 DONE AUTO DROPBOX SYNC!")

if __name__ == "__main__":
    main()
