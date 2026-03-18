import dropbox
import os
import json

dbx = dropbox.Dropbox(os.environ["DROPBOX_TOKEN"])

ROOT_FOLDER = "/Face Library 18"
result = []

def get_or_create_shared_link(path):
    try:
        links = dbx.sharing_list_shared_links(path=path).links
        if links:
            return links[0].url
        else:
            return dbx.sharing_create_shared_link_with_settings(path).url
    except Exception as e:
        print("Error:", e)
        return None

def fix_image(url):
    return url.replace("?dl=0", "?raw=1")

def fix_zip(url):
    return url.replace("?dl=0", "?dl=1")

# ambil semua folder player
res = dbx.files_list_folder(ROOT_FOLDER)

for folder in res.entries:
    if isinstance(folder, dropbox.files.FolderMetadata):

        parts = folder.name.split("_")

        # validasi format nama
        if len(parts) < 2:
            continue

        player_id = parts[0]
        player_name = parts[1]
        club = parts[2] if len(parts) > 2 else "Unknown"

        folder_path = f"{ROOT_FOLDER}/{folder.name}"
        files = dbx.files_list_folder(folder_path)

        image_link = None
        zip_link = None

        for f in files.entries:
            if isinstance(f, dropbox.files.FileMetadata):

                link = get_or_create_shared_link(f.path_lower)

                if f.name.lower().endswith(".png"):
                    image_link = fix_image(link)

                elif f.name.lower().endswith(".zip"):
                    zip_link = fix_zip(link)

        if image_link and zip_link:
            result.append({
                "id": player_id,
                "version": "v1",
                "name": player_name,
                "club": club,
                "image": image_link,
                "zip_url": zip_link
            })

# simpan JSON
with open("facelibrary18.json", "w") as f:
    json.dump(result, f, indent=2)
