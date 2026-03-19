import dropbox
import os
import json

# Mengambil token dari Environment Variables SECRETS Github Actions Anda
DROPBOX_TOKEN = os.environ["DROPBOX_TOKEN"]

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
    return url.replace("?dl=0", "?dl=1").replace("&dl=0", "&dl=1")

def fix_zip(url):
    return url.replace("?dl=0", "?dl=1").replace("&dl=0", "&dl=1")

# Coba temukan direktori root secara otomatis (App Folder vs Full Dropbox)
def find_root_folder(dbx):
    try:
        res = dbx.files_list_folder("")
        for e in res.entries:
            if isinstance(e, dropbox.files.FolderMetadata) and len(e.name.split("_")) >= 2:
                print("Terdeteksi tipe App Folder (folder pemain ada di root).")
                return ""
                
        try:
            dbx.files_get_metadata("/Apps/FaceLibrary18")
            print("Terdeteksi tipe Full Dropbox. Menggunakan '/Apps/FaceLibrary18'.")
            return "/Apps/FaceLibrary18"
        except:
            pass

        try:
            dbx.files_get_metadata("/FaceLibrary18")
            return "/FaceLibrary18"
        except:
            pass
    except Exception as e:
        pass
    return ""

ROOT_FOLDER = find_root_folder(dbx)

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

            player_id = None
            player_name = folder.name
            club = "Unknown"

            # validasi format nama folder (contoh: 47787_Joao Cancelo_Barcelona)
            if len(parts) >= 2:
                player_id = parts[0]
                player_name = parts[1]
                club = parts[2] if len(parts) > 2 else "Unknown"

            # folder.path_lower otomatis mengarah ke absolute path yang benar di Dropbox
            try:
                # Gunakan recursive=True agar bisa mencari di dalam folder ID juga
                files = dbx.files_list_folder(folder.path_lower, recursive=True)
            except Exception as e:
                print(f"Error mengakses isi folder {folder.name}: {e}")
                continue

            image_link = None
            zip_link = None

            for f in files.entries:
                if isinstance(f, dropbox.files.FolderMetadata):
                    # Jika menggunakan format folder "Nama Pemain", ID bisa diambil dari nama subfolder (angka)
                    if f.name.isdigit():
                        player_id = f.name
                elif isinstance(f, dropbox.files.FileMetadata):
                    
                    # Jika itu adalah file PNG/JPG - ambil metadata link
                    if f.name.lower().endswith((".png", ".jpg", ".jpeg", ".webp")):
                        print(f"Mendapatkan link gambar untuk: {f.name}")
                        link = get_or_create_shared_link(f.path_lower)
                        if link:
                            image_link = fix_image(link)
                            
                    # Jika itu adalah file ZIP/RAR/7z - ambil metadata link
                    elif f.name.lower().endswith((".zip", ".rar", ".7z")):
                        print(f"Mendapatkan link zip/rar untuk: {f.name}")
                        link = get_or_create_shared_link(f.path_lower)
                        if link:
                            zip_link = fix_zip(link)
                        else:
                            print(f"❌ Gagal mendapatkan link untuk file: {f.name}")
                    else:
                        print(f"ℹ️ Mengabaikan file dengan ekstensi yang tidak dikenali: {f.name}")

            # Memasukkan data ke list result
            if player_id and image_link and zip_link:
                result.append({
                    "id": player_id,
                    "version": "v1",
                    "name": player_name,
                    "club": club,
                    "image": image_link,
                    "zip_url": zip_link
                })
                print(f"✅ Berhasil memproses: {player_name}\n")
            else:
                missing = []
                if not player_id: missing.append("ID Pemain")
                if not image_link: missing.append("Gambar")
                if not zip_link: missing.append("ZIP")
                
                # Masukkan debug info ke JSON agar terlihat di GitHub hasil commit-nya
                result.append({
                    "_error": "Data tidak lengkap",
                    "_missing": missing,
                    "name": player_name,
                    "found_id": player_id,
                    "found_image": image_link if image_link else None,
                    "found_zip": zip_link if zip_link else None
                })
                print(f"⚠️ Melewati {player_name}: Data tidak lengkap ({', '.join(missing)}).\n")

# simpan JSON output
output_file = "facelibrary18.json"
with open(output_file, "w") as f:
    json.dump(result, f, indent=4)

print(f"Selesai! Data diekstrak ke dalam '{output_file}'")
