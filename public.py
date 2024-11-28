import re

def fix_prolog_file(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        lines = file.readlines()
    
    fixed_lines = []
    for line in lines:
        # Sadece publication predicate'lerini hedef alıyoruz
        if line.strip().startswith("publication"):
            # Tek tırnak hatalarını düzelt
            line = re.sub(r"(?<=\w)'(?=\w)", r"\\'", line)  # Kelimeler arasında geçen ' işaretlerini kaçış yap
        fixed_lines.append(line)
    
    # Düzeltmeleri yeni dosyaya yaz
    with open(file_path, 'w', encoding='utf-8') as file:
        file.writelines(fixed_lines)
    print(f"Düzeltmeler tamamlandı: {file_path}")

# Prolog dosyasını düzenleyin
file_path = "prolog-academician/publication_facts.pro"
fix_prolog_file(file_path)
