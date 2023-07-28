import psycopg2
import pandas as pd

# Excel dosyanızın yolunu ve adını belirtin
excel_dosya_yolu = './il-ilce-mahalle.xlsx'

# Excel verilerini bir DataFrame'e yükleyin ve PK sütunundaki 0 ile başlayanları düzeltin
df = pd.read_excel(excel_dosya_yolu)
df['PK'] = df['PK'].apply(lambda x: str(x).lstrip('0') if str(x).startswith('0') else x)

# PostgreSQL veritabanı bağlantısı için gerekli bilgiler
db_host = 'host'
db_name = 'name'
db_user = 'user'
db_password = 'password'

# PostgreSQL veritabanına bağlanın
conn = psycopg2.connect(
    host=db_host,
    database=db_name,
    user=db_user,
    password=db_password
)

# Veritabanı üzerinde işlemler yapmak için bir cursor oluşturun
cursor = conn.cursor()

# İl tablosunu oluşturun ve verileri aktarın
cursor.execute('CREATE TABLE IF NOT EXISTS il (id SERIAL PRIMARY KEY, il_ad VARCHAR)')
for il_ad in df['il'].unique():
    cursor.execute('INSERT INTO il (il_ad) VALUES (%s)', (il_ad,))

# İlçe tablosunu oluşturun ve verileri aktarın
cursor.execute('CREATE TABLE IF NOT EXISTS ilce (id SERIAL PRIMARY KEY, ilce_ad VARCHAR, il_id INTEGER)')
for index, row in df[['ilçe', 'il']].drop_duplicates().iterrows():
    ilce_ad, il_ad = row
    cursor.execute('SELECT id FROM il WHERE il_ad = %s', (il_ad,))
    il_id = cursor.fetchone()[0]
    cursor.execute('INSERT INTO ilce (ilce_ad, il_id) VALUES (%s, %s)', (ilce_ad, il_id))

# Mahalle tablosunu oluşturun ve verileri aktarın
cursor.execute('CREATE TABLE IF NOT EXISTS mahalle (id SERIAL PRIMARY KEY, mahalle_ad VARCHAR, ilce_id INTEGER, PK VARCHAR)')
for index, row in df[['Mahalle', 'ilçe', 'PK']].drop_duplicates().iterrows():
    mahalle_ad, ilce_ad, PK = row
    cursor.execute('SELECT id FROM ilce WHERE ilce_ad = %s', (ilce_ad,))
    ilce_id = cursor.fetchone()[0]
    cursor.execute('INSERT INTO mahalle (mahalle_ad, ilce_id, PK) VALUES (%s, %s, %s)', (mahalle_ad, ilce_id, PK))

# Veritabanı değişikliklerini kaydedin ve bağlantıyı kapatın
conn.commit()
cursor.close()
conn.close()
