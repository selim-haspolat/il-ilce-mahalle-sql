import pandas as pd

# Excel dosyanızın yolunu ve adını belirtin
excel_dosya_yolu = './il-ilce-mahalle.xlsx'

# Excel verilerini bir DataFrame'e yükleyin ve PK sütunundaki 0 ile başlayanları düzeltin
df = pd.read_excel(excel_dosya_yolu)

# PK sütununu düzenleyerek 4 haneli olacak şekilde 0'larla tamamlayın
df['PK'] = df['PK'].apply(lambda x: str(x).zfill(5))

# Value'ların yanındaki boşlukları kaldırın
df['il'] = df['il'].str.strip()
df['ilçe'] = df['ilçe'].str.strip()
df['Mahalle'] = df['Mahalle'].str.strip()

# .sql dosyaları için dosya yollarını belirtin
il_sql_dosya = './il.sql'
ilce_sql_dosya = './ilce.sql'
mahalle_sql_dosya = './mahalle.sql'

# İl tablosu için .sql dosyasını oluşturun ve verileri yazın
with open(il_sql_dosya, 'w') as f:
    f.write("CREATE TABLE IF NOT EXISTS il (id SERIAL PRIMARY KEY, il VARCHAR);\n")
    f.write("INSERT INTO il (il) VALUES\n")
    for il_ad in df['il'].unique():
        f.write(f"('{il_ad}'),\n")
    f.write(";\n")

# İlçe tablosu için .sql dosyasını oluşturun ve verileri yazın
with open(ilce_sql_dosya, 'w') as f:
    f.write("CREATE TABLE IF NOT EXISTS ilce (id SERIAL PRIMARY KEY, ilce VARCHAR, il_id INTEGER REFERENCES il(id));\n")
    f.write("INSERT INTO ilce (ilce, il_id) VALUES\n")
    for index, row in df[['ilçe', 'il']].drop_duplicates().iterrows():
        ilce_ad, il_ad = row
        f.write(f"('{ilce_ad}', (SELECT id FROM il WHERE il = '{il_ad}')),\n")
    f.write(";\n")

# Mahalle tablosu için .sql dosyasını oluşturun ve verileri yazın
with open(mahalle_sql_dosya, 'w') as f:
    f.write("CREATE TABLE IF NOT EXISTS mahalle (id SERIAL PRIMARY KEY, mahalle VARCHAR, ilce_id INTEGER REFERENCES ilce(id), PK VARCHAR);\n")
    f.write("INSERT INTO mahalle (mahalle, ilce_id, PK) VALUES\n")
    for index, row in df[['Mahalle', 'ilçe', 'PK']].drop_duplicates().iterrows():
        mahalle_ad, ilce_ad, PK = row
        f.write(f"('{mahalle_ad}', (SELECT id FROM ilce WHERE ilce = '{ilce_ad}'), '{PK}'),\n")
    f.write(";\n")
