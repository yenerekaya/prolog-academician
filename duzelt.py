import re

# Dosya adını belirleyin
input_file = 'prolog-academician/publication_facts.pro'
output_file = 'prolog-academician/publication_facts_fixed.pro'


# Tırnakları doğru kurallara göre değiştiren fonksiyon
def fix_line(line):
    # İlk parantezden sonra ve son parantezden önceki tırnakları koru
    fixed_line = re.sub(r"(?<=\()\s*'", "<<<KEEP_THIS>>>", line)  # İlk parantezden sonraki tırnakları işaretle
    fixed_line = re.sub(r"'\s*(?=\))", "<<<KEEP_THIS>>>", fixed_line)  # Son parantezden önceki tırnakları işaretle

    # Virgülün sağındaki veya solundaki tırnakları koru
    fixed_line = re.sub(r"(?<=, )'", "<<<KEEP_THIS>>>", fixed_line)  # Virgülden sonra gelen düz tırnağı işaretle
    fixed_line = re.sub(r"'(?=,)", "<<<KEEP_THIS>>>", fixed_line)  # Virgülden önce gelen düz tırnağı işaretle

    # Kelime içindeki tırnakları eğik tırnağa çevir
    fixed_line = re.sub(r"(?<=\w)'(?=\w)", "’", fixed_line)  # Kelime içindeki tırnaklar

    # Diğer durumlarda kalan düz tırnakları eğik tırnağa çevir
    fixed_line = re.sub(r"(?<!<<<KEEP_THIS>>>)'(?!<<<KEEP_THIS>>>)", "’", fixed_line)

    # İşaretlenen tırnakları geri yükle
    fixed_line = fixed_line.replace("<<<KEEP_THIS>>>", "'")

    return fixed_line

# Dosyayı satır satır işle
with open(input_file, 'r', encoding='utf-8') as infile, open(output_file, 'w', encoding='utf-8') as outfile:
    for line in infile:
        # Her satırı düzenle ve yeni dosyaya yaz
        fixed_line = fix_line(line)
        outfile.write(fixed_line)

print(f"Düzenleme tamamlandı. Çıkış dosyası: {output_file}")
