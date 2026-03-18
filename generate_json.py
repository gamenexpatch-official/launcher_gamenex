import dropbox
import os
import json

# Inisialisasi Dropbox
dbx = dropbox.Dropbox(DROPBOX_TOKEN)

# Ganti dengan path folder jika menggunakan aplikasi tipe "Full Dropbox" (misal: "/Apps/FaceLibrary18").
# Jika menggunakan tipe "App Folder", biarkan "" (string kosong).
ROOT_FOLDER = ""
result = []

def get_or_create_shared_link(path):
    try:
        links = dbx.sharing_list_shared_links(path=path).links
        if links:
            return links[0].url
        else:
            return dbx.sharing_create_shared_link_with_settings(path).url
    except Exception as e:
        print(f"Error getting link for {path}:", e)
        return None

def fix_image(url):
    return url.replace("?dl=0", "?raw=1")

def fix_zip(url):
    return url.replace("?dl=0", "?dl=1")

# ambil semua folder di direktori root yang dituju
try:
    print(f"Mengakses Dropbox folder: '{ROOT_FOLDER if ROOT_FOLDER else '/'}'...")
    res = dbx.files_list_folder(ROOT_FOLDER)
except Exception as e:
    print(f"Error mengakses root folder: {e}")
    res = None

if res:
    for folder in res.entries:
        if isinstance(folder, dropbox.files.FolderMetadata):
            parts = folder.name.split("_")

            # validasi format nama folder (contoh: 47787_Joao Cancelo_Barcelona)
            if len(parts) < 2:
                continue

            player_id = parts[0]
            player_name = parts[1]
            club = parts[2] if len(parts) > 2 else "Unknown"

            # folder.path_lower otomatis mengarah ke absolute path yang benar di Dropbox
            try:
                files = dbx.files_list_folder(folder.path_lower)
            except Exception as e:
                print(f"Error mengakses isi folder {folder.name}: {e}")
                continue

            image_link = None
            zip_link = None

            for f in files.entries:
                if isinstance(f, dropbox.files.FileMetadata):
                    
                    # Jika itu adalah file PNG/JPG - ambil metadata link
                    if f.name.lower().endswith((".png", ".jpg", ".jpeg")):
                        print(f"Mendapatkan link gambar untuk: {f.name}")
                        link = get_or_create_shared_link(f.path_lower)
                        if link:
                            image_link = fix_image(link)
                            
                    # Jika itu adalah file ZIP - ambil metadata link
                    elif f.name.lower().endswith(".zip"):
                        print(f"Mendapatkan link zip untuk: {f.name}")
                        link = get_or_create_shared_link(f.path_lower)
                        if link:
                            zip_link = fix_zip(link)

            # Memasukkan data ke list result
            if image_link and zip_link:
                result.append({
                    "id": player_id,
                    "version": "v1",
                    "name": player_name,
                    "club": club,
                    "image": image_link,
                    "zip": zip_link  # Diubah menjadi "zip" dari sebelumnya "zip_url"
                })
                print(f"✅ Berhasil memproses: {player_name}\n")
            else:
                print(f"⚠️ Melewati {player_name}: Gambar atau ZIP tidak ditemukan secara lengkap.\n")

# simpan JSON output
output_file = "facelibrary18.json"
with open(output_file, "w") as f:
    json.dump(result, f, indent=4)

print(f"Selesai! Data diekstrak ke dalam '{output_file}'")
