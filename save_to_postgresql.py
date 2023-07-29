import psycopg2
import pandas as pd

# Excel dosyanızın yolunu ve adını belirtin
excel_dosya_yolu = './il-ilce-mahalle.xlsx'

# Excel verilerini bir DataFrame'e yükleyin ve PK sütunundaki 0 ile başlayanları düzeltin
df = pd.read_excel(excel_dosya_yolu)

# Format PK values to be 5 characters long with leading zeros
df['PK'] = df['PK'].apply(lambda x: str(x).zfill(5))

# PostgreSQL veritabanı bağlantısı için gerekli bilgiler
db_host = 'db_host'
db_name = 'db_name'
db_user = 'db_user'
db_password = 'db_password'

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
cursor.execute('CREATE TABLE IF NOT EXISTS il (id SERIAL PRIMARY KEY, name VARCHAR)')
for il in df['il'].unique():
    cursor.execute('INSERT INTO il (name) VALUES (%s)', (il,))

# İlçe tablosunu oluşturun ve verileri aktarın
cursor.execute('CREATE TABLE IF NOT EXISTS ilce (id SERIAL PRIMARY KEY, name VARCHAR, il_id INTEGER)')
for index, row in df[['ilçe', 'il']].drop_duplicates().iterrows():
    ilce, il = row
    cursor.execute('SELECT id FROM il WHERE name = %s', (il,))
    il_id = cursor.fetchone()[0]
    cursor.execute('INSERT INTO ilce (name, il_id) VALUES (%s, %s)', (ilce, il_id))

# Mahalle tablosunu oluşturun ve verileri aktarın
cursor.execute('CREATE TABLE IF NOT EXISTS mahalle (id SERIAL PRIMARY KEY, name VARCHAR, ilce_id INTEGER, PK VARCHAR)')
for index, row in df[['Mahalle', 'ilçe', 'PK']].drop_duplicates().iterrows():
    mahalle, ilce, PK = row
    cursor.execute('SELECT id FROM ilce WHERE name = %s', (ilce,))
    ilce_id = cursor.fetchone()[0]
    cursor.execute('INSERT INTO mahalle (name, ilce_id, PK) VALUES (%s, %s, %s)', (mahalle, ilce_id, PK))

# Veritabanı değişikliklerini kaydedin ve bağlantıyı kapatın
conn.commit()
cursor.close()
conn.close()
