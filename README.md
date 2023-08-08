# ptt-il-ilce-mahalle-sql

Güncel verileri almak için excel dosyasını burdan indirebilirsiniz https://postakodu.ptt.gov.tr/ 

# Repo clone
```console
git clone https://github.com/selim-haspolat/ptt-il-ilce-mahalle-sql.git
```
```console
cd ptt-il-ilce-mahalle-sql
```

# Kurulum
Local e kurmak istemeyenler indirmeye işlemine geçebilir
```console
python -m venv env
```
```console
source env/Scripts/activate 
```

Gerekli paketleri indirme
```console
pip install -r requirements.txt
```
# Kullanım
Bir database oluşturup save_to_postgresql.py dosyasındaki postgresql bilgilerini doldurun

### Örnek
```py
db_host = '127.0.0.1'
db_name = 'il_ilce_mahalle' 
db_user = 'postgres'
db_password = 'şifrem'
```

Kodu Çalıştır
```console
python save_to_postgresql.py
```


