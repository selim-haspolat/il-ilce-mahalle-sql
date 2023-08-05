import psycopg2
import pandas as pd

# Excel dosyanızın yolunu ve adını belirtin
excel_dosya_yolu = './il-ilce-mahalle.xlsx'

# Excel verilerini bir DataFrame'e yükleyin ve PK sütunundaki 0 ile başlayanları düzeltin
df = pd.read_excel(excel_dosya_yolu)

# Format PK values to be 5 characters long with leading zeros
df['PK'] = df['PK'].apply(lambda x: str(x).zfill(5))

# PostgreSQL veritabanı bağlantısı için gerekli bilgiler
db_host = 'db_host'  # örnek 127.0.0.1
db_name = 'db_name'  # data base e verdiğiniz isim
db_user = 'postgres'
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
cursor.execute('CREATE TABLE IF NOT EXISTS il (id SERIAL PRIMARY KEY, name VARCHAR)')
for il in df['il'].unique():
    name = il.strip()
    cursor.execute('INSERT INTO il (name) VALUES (%s)', (name,))

# İlçe tablosunu oluşturun ve verileri aktarın
cursor.execute('CREATE TABLE IF NOT EXISTS ilce (id SERIAL PRIMARY KEY, name VARCHAR, il_id INTEGER)')
for index, row in df[['ilçe', 'il']].drop_duplicates().iterrows():
    ilce, il = row
    cursor.execute('SELECT id FROM il WHERE name = %s', (il.strip(),))
    il_id = cursor.fetchone()[0]
    name = ilce.strip()
    cursor.execute('INSERT INTO ilce (name, il_id) VALUES (%s, %s)', (name, il_id))

# Mahalle tablosunu oluşturun ve verileri aktarın
cursor.execute('CREATE TABLE IF NOT EXISTS mahalle (id SERIAL PRIMARY KEY, name VARCHAR, ilce_id INTEGER, il_id INTEGER, posta_kodu VARCHAR)')
for index, row in df[['Mahalle', 'ilçe', 'il', 'PK']].iterrows():
    mahalle, ilce, il, PK = row
    cursor.execute('SELECT id FROM il WHERE name = %s', (il.strip(),))
    il_id = cursor.fetchone()
    
    # If il does not exist in the il table, insert it
    if il_id is None:
        cursor.execute('INSERT INTO il (name) VALUES (%s) RETURNING id', (il.strip(),))
        il_id = cursor.fetchone()[0]
    else:
        il_id = il_id[0]

    # Check if the ilçe exists in the ilce table for the given il_id
    cursor.execute('SELECT id FROM ilce WHERE name = %s AND il_id = %s', (ilce.strip(), il_id))
    ilce_id = cursor.fetchone()
    
    # If ilçe does not exist in the ilce table for the given il_id, insert it
    if ilce_id is None:
        cursor.execute('INSERT INTO ilce (name, il_id) VALUES (%s, %s) RETURNING id', (ilce.strip(), il_id))
        ilce_id = cursor.fetchone()[0]
    else:
        ilce_id = ilce_id[0]

    name = mahalle.strip()

    # cursor.execute('INSERT INTO mahalle (name, il_id, ilce_id, posta_kodu) VALUES (%s, %s, %s, %s)', (mahalle, il_id, ilce_id, PK))
    cursor.execute('INSERT INTO mahalle (name, ilce_id, il_id, posta_kodu) VALUES (%s, %s, %s, %s)', (name, ilce_id,il_id, PK))

# Veritabanı değişikliklerini kaydedin ve bağlantıyı kapatın
conn.commit()
cursor.close()
conn.close()
