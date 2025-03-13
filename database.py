# -*- coding: utf-8 -*-
import psycopg2
import json
import threading
def save_to_database(data):
    conn = psycopg2.connect(
        dbname="postgres",
        user="postgres",
        password="159753Mert.",
        host="localhost",
        port="5432"
    )
    cursor = conn.cursor()
    for record in data:
        try:
            # imgurl listesini JSON string'e çevir
            imgurl_json = json.dumps(record.get("imgurl", [])) if isinstance(record.get("imgurl"), list) else record.get("imgurl")

            cursor.execute(
                """
                INSERT INTO scraped_data (
                    offerid, game, platform, country, server, region, race, faction,
                    rank, level, class, title, description, price, imgurl
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (offerid) DO NOTHING
                """,
                (
                    record.get("offerid"), record.get("game"), record.get("platform"),
                    record.get("country"), record.get("server"), record.get("region"),
                    record.get("race"), record.get("faction"), record.get("rank"),
                    record.get("level"), record.get("class"), record.get("title"), record.get("description"),
                    record.get("price"), imgurl_json  
                )
            )
        except Exception as e:
            print(f"Veri kaydedilirken hata: {e}")
        except Exception as e:
            print(f"Veri kaydedilirken hata: {e}")

    conn.commit()
    cursor.close()
    conn.close()

# database.py

def delete_old_offers(game_name, current_offerids):
    conn = psycopg2.connect(
        dbname="postgres",
        user="postgres",
        password="159753Mert.",
        host="localhost",
        port="5432"
    )
    cursor = conn.cursor()

    try:
        if not current_offerids:
            print(f"{game_name} icin current_offerids bos oldugu icin silme islemi yapilmadi.")
            return

        # Silinecek offerid ve title bilgilerini al
        cursor.execute(
            """
            SELECT offerid, title
            FROM scraped_data
            WHERE game = %s AND offerid NOT IN %s
            """,
            (game_name, tuple(current_offerids))
        )
        rows_to_backup = cursor.fetchall()  # Silinecek offerid ve title bilgilerini al

       

        # Silme islemini gerceklestir
        cursor.execute(
            """
            DELETE FROM scraped_data
            WHERE game = %s AND offerid NOT IN %s
            """,
            (game_name, tuple(current_offerids))
        )
        conn.commit()

        print(f"{len(rows_to_backup)} eski ilan kopyalanarak silindi: {game_name}")

    except Exception as e:
        print(f"Eski ilanlar silinirken hata olustu: {e}")
    finally:
        cursor.close()
        conn.close()

def is_offerid_in_database(offerid):
    conn = psycopg2.connect(
        dbname="postgres",
        user="postgres",
        password="159753Mert.",
        host="localhost",
        port="5432"
    )
    cursor = conn.cursor()
    try:
        cursor.execute(
            """
            SELECT EXISTS (
                SELECT 1 FROM scraped_data WHERE offerid = %s
            )
            """,
            (offerid,)
        )
        exists = cursor.fetchone()[0]
    except Exception as e:
        print(f"Veritabani kontrol hatasi: {e}")
        exists = False
    finally:
        cursor.close()
        conn.close()
    return exists




class Database:
    _lock = threading.Lock()
    _instance = None

    def __new__(cls):
        with cls._lock:
            if cls._instance is None:
                cls._instance = super(Database, cls).__new__(cls)
                cls._instance.init_db()
        return cls._instance

    def init_db(self):
        self.conn = psycopg2.connect(
            dbname="postgres",
            user="postgres",
            password="159753Mert.",
            host="localhost",
            port="5432"
        )
        self.cursor = self.conn.cursor()

    def fetch_next_unprocessed_record(self):
        with self.conn:
            # En son işlenmemiş ilanı seç
            self.cursor.execute("""
                SELECT * FROM (SELECT offerid, game, platform, country, server, region, race, faction,
                   rank, level, class, title, description, price, imgurl
            FROM scraped_data
            WHERE processed = FALSE
            ORDER BY offerid
            FOR UPDATE SKIP LOCKED
            LIMIT 1) sub;
            """)
            record = self.cursor.fetchone()
            if record:
                # İlanı işlenmiş olarak işaretle
                self.cursor.execute("""
                    UPDATE scraped_data SET processed = TRUE WHERE offerid = %s;
                """, (record[0],))
                self.conn.commit()
                return {
                "offerid": record[0] or "Default Offer ID",
                "game": record[1] or "Default Game",
                "platform": record[2] or "PC",
                "country": record[3] or "United States",
                "server": (record[4] or "A").replace("(", "").replace(")", "").strip(),
                "region": record[5] or "EU",
                "race": record[6] or "Orc",
                "faction": record[7] or "EU",
                "rank": record[8] or "Unranked",
                "level": record[9] or "10",
                "class": record[10] or "Rogue",
                "title": record[11] or "Default Title",
                "description": (record[12] or "Please Contact Before Buy For More Information").replace("https://", "link:"),
                "price": record[13] or 0,
                "imgurl": record[14] or "Default URL"
            }
            return None  # Eğer tüm kayıtlar işlenmişse None döner

    def is_processed(self, offerid):
        """
        Veritabanında offerid'nin processed durumunu kontrol eder.
        """
        self.cursor.execute(
            """
            SELECT processed FROM scraped_data WHERE offerid = %s;
            """,
            (offerid,)
        )
        result = self.cursor.fetchone()
        return result[0] if result else True  # Eğer kayıt yoksa işlenmiş varsayılır

    def close(self):
        self.cursor.close()
        self.conn.close()
