import requests
import time
import json
from termcolor import colored
import threading
import sys

# Membaca token dari file data.txt
def load_tokens(file_name="data.txt"):
    with open(file_name, 'r') as file:
        tokens = [line.strip() for line in file.readlines()]
    return tokens

# Mengambil dan menyelesaikan tugas
def process_tasks(token):
    headers = {
        "authorization": f"Bearer {token}",
        "accept": "*/*",
        "accept-encoding": "gzip, deflate, br, zstd",
        "user-agent": "Mozilla/5.0"
    }

    try:
        # Mengambil daftar tugas
        response_tasks = requests.get("https://api.chaingn.org/sub_tasks", headers=headers)
        if response_tasks.status_code == 200:
            tasks = response_tasks.json()
            print(colored(f"Ditemukan {len(tasks)} tugas yang perlu diproses.", "yellow"))

            for task in tasks:
                # Cek apakah tugas sudah selesai (done == true)
                if not task["done"]:
                    print(colored(f"Menyelesaikan Tugas: {task['title']}", "yellow"))

                    # Selesaikan tugas
                    task_payload = {"recourceId": task["recourceId"]}
                    response_complete_task = requests.post("https://api.chaingn.org/sub_task", headers=headers, json=task_payload)

                    if response_complete_task.status_code == 200:
                        print(colored(f"Tugas {task['title']} berhasil diselesaikan!", "green"))
                    else:
                        print(colored(f"Gagal menyelesaikan tugas: {response_complete_task.text}", "red"))

                # Jika tugas sudah selesai (done == true) tetapi belum diambil hadiahnya (claimed == false)
                elif task["done"] and not task["claimed"]:
                    print(colored(f"Mengambil hadiah untuk Tugas: {task['title']}", "yellow"))

                    # Ambil hadiah tugas menggunakan 'id'
                    reward_payload = {"id": task["id"]}  # Menggunakan 'id' tugas yang telah selesai untuk klaim
                    response_claim_task = requests.put("https://api.chaingn.org/sub_task/claim", headers=headers, json=reward_payload)

                    if response_claim_task.status_code == 200:
                        print(colored(f"Hadiah untuk tugas {task['title']} berhasil diambil.", "green"))
                    else:
                        print(colored(f"Gagal mengambil hadiah: {response_claim_task.text}", "red"))

                # Tugas sudah selesai dan hadiah sudah diambil
                elif task["claimed"]:
                    print(colored(f"Hadiah untuk Tugas: {task['title']} sudah diambil.", "green"))

        else:
            print(colored(f"Kesalahan saat mengambil tugas: {response_tasks.text}", "red"))

    except requests.exceptions.RequestException as e:
        print(colored(f"Kesalahan permintaan: {str(e)}", "red"))

# Mengirim request dan mendapatkan data dari akun
def process_account(token):
    headers = {
        "authorization": f"Bearer {token}",
        "accept": "*/*",
        "accept-encoding": "gzip, deflate, br, zstd",
        "user-agent": "Mozilla/5.0"
    }

    try:
        # Request informasi akun
        response_user = requests.get("https://api.chaingn.org/user", headers=headers)
        if response_user.status_code == 200:
            user_data = response_user.json()
            print(colored(f"Memproses Akun: {user_data['username']} (ID: {user_data['id']})", "green"))

            # Request informasi wallet
            response_wallet = requests.get("https://api.chaingn.org/wallets", headers=headers)
            wallet_data = response_wallet.json()
            print(colored(f"Info Wallet: Saldo: {wallet_data[0]['balance']} {wallet_data[0]['type']}", "yellow"))


            # Lakukan tugas farming
            farm_payload = {"id": wallet_data[0]['id']}
            response_farm = requests.post("https://api.chaingn.org/wallet/farm", headers=headers, json=farm_payload)
            if response_farm.status_code == 200:
                print(colored(f"Tugas farming untuk akun {user_data['username']} selesai.", "green"))
            else:
                print(colored(f"Kesalahan saat farming: {response_farm.text}", "red"))
            
            # Proses semua tugas
            process_tasks(token)
        else:
            print(colored(f"Kesalahan saat mengambil informasi akun: {response_user.text}", "red"))
    except requests.exceptions.RequestException as e:
        print(colored(f"Kesalahan permintaan: {str(e)}", "red"))

# Hitung mundur 6 jam
def countdown_6_hours():
    total_seconds = 6 * 60 * 60  # 6 jam dalam detik
    while total_seconds > 0:
        hours, remainder = divmod(total_seconds, 3600)
        minutes, seconds = divmod(remainder, 60)
        sys.stdout.write(f"\rHitung mundur: {hours:02} jam {minutes:02} menit {seconds:02} detik")
        sys.stdout.flush()
        time.sleep(1)
        total_seconds -= 1

    print("\n6 jam telah selesai, memulai ulang proses...\n")

# Fungsi utama untuk memproses semua akun
def main():
    tokens = load_tokens()  # Baca semua token dari data.txt
    total_accounts = len(tokens)

    print(colored(f"Total akun yang akan diproses: {total_accounts}", "blue"))

    for i, token in enumerate(tokens, start=1):
        print(colored(f"Memproses akun {i} dari {total_accounts}...", "yellow"))
        process_account(token)
        print(colored("Menunggu 5 detik sebelum memproses akun berikutnya...\n", "yellow"))
        time.sleep(5)

    print(colored("Semua akun telah diproses, memulai hitung mundur 6 jam...\n", "blue"))
    countdown_6_hours()  # Mulai hitung mundur 6 jam

# Jalankan dalam thread terpisah agar tidak berhenti meskipun ada error
def run_in_thread():
    while True:
        try:
            main()  # Jalankan proses utama
        except Exception as e:
            print(colored(f"Kesalahan: {str(e)}, melanjutkan proses...", "red"))
        time.sleep(5)  # Tambahkan jeda sebelum restart

# Jalankan kode
if __name__ == "__main__":
    run_in_thread()
