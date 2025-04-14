from rasa_sdk import Action
from rasa_sdk.events import SlotSet
import psycopg2
from fuzzywuzzy import fuzz  # Untuk mencocokkan teks secara fuzzy

class ActionInformasiDesa(Action):
    def name(self):
        return "action_informasi_desa"

    def run(self, dispatcher, tracker, domain):
        try:
            # Koneksi ke database
            conn = psycopg2.connect(
                dbname="new_bot",
                user="postgres",
                password="texas123",
                host="localhost",
                port="5432"
            )
            cursor = conn.cursor()

            # Ambil intent dan teks pengguna
            intent = tracker.latest_message['intent'].get('name')
            user_text = tracker.latest_message.get('text')

            # Query database untuk semua data terkait intent
            cursor.execute(
                "SELECT text, response, keywords FROM rasa_data WHERE intent = %s",
                (intent,)
            )
            results = cursor.fetchall()

            # Variabel untuk menyimpan hasil terbaik
            best_match = None
            highest_similarity = 0

            # Cari kecocokan teks pengguna dengan teks dan keyword di database
            for db_text, response, db_keyword in results:
                # Cek kecocokan berdasarkan teks
                similarity_text = fuzz.ratio(user_text.lower(), db_text.lower())
                
                # Cek kecocokan berdasarkan keyword (menggunakan substring)
                similarity_keyword = fuzz.partial_ratio(user_text.lower(), db_keyword.lower()) if db_keyword else 0

                # Pilih hasil dengan kecocokan tertinggi
                if similarity_text > highest_similarity or similarity_keyword > highest_similarity:
                    highest_similarity = max(similarity_text, similarity_keyword)
                    best_match = response

            # Tentukan threshold similarity
            if best_match and highest_similarity > 70:  # 70% kecocokan
                dispatcher.utter_message(text=best_match)
            else:
                dispatcher.utter_message(text="Maaf, saya tidak memiliki informasi tentang itu.")

        except Exception as e:
            print(f"Error: {e}")
            dispatcher.utter_message(text="Terjadi kesalahan saat mengambil data.")

        finally:
            # Tutup koneksi ke database
            if 'cursor' in locals():
                cursor.close()
            if 'conn' in locals():
                conn.close()

        return []
