import os

# Dosya yolu
input_file_path = "prolog-academician/researcher_facts.pro"
output_file_path = "prolog-academician/researcher_facts_titlecase.pro"

# Dosyayı oku
with open(input_file_path, "r", encoding="utf-8") as file:
    lines = file.readlines()

# Her satırı düzenle
updated_lines = []
for line in lines:
    # researcher('Prof. Dr. Melike AFŞAR', 'Astronomi Ve Uzay Bilimleri Bölümü', 'Astrofizik Anabilim Dalı').
    parts = line.split("'")
    updated_parts = []
    for i, part in enumerate(parts):
        if i % 2 == 1:  # Tırnak içinde olan kısımları kontrol et
            part = ' '.join(word.capitalize() for word in part.split())
        updated_parts.append(part)
    updated_line = "'".join(updated_parts)
    updated_lines.append(updated_line)

# Yeni dosyaya yaz
os.makedirs(os.path.dirname(output_file_path), exist_ok=True)
with open(output_file_path, "w", encoding="utf-8") as file:
    file.write("".join(updated_lines))

print(f"Dosya başarıyla düzenlendi ve {output_file_path} konumuna kaydedildi.")
