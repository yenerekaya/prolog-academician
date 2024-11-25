import json
import os

json_file_path = "academic_data.json"
with open(json_file_path, "r", encoding="utf-8") as file:
    data = json.load(file)

researcher_facts = []
department_facts = []
publication_facts = []

department_academics = {}

for researcher in data:
    researcher_fact = f"researcher('{researcher['name']}', '{researcher['department']}', '{researcher['discipline']}')."
    researcher_facts.append(researcher_fact)
    
    department = researcher['department']
    if department not in department_academics:
        department_academics[department] = []
    department_academics[department].append(researcher['name'])

    for publication in researcher['publications']:
        title = publication.split('-')[0].strip()
        publication_fact = f"publication('{title}', '{researcher['name']}')."
        publication_facts.append(publication_fact)

for department, academics in department_academics.items():
    academics_list = ", ".join([f"'{name}'" for name in academics])
    department_fact = f"department('{department}', [{academics_list}])."
    department_facts.append(department_fact)

output_dir = "prolog-academician"
os.makedirs(output_dir, exist_ok=True)

with open(os.path.join(output_dir, "researcher_facts.pro"), "w", encoding="utf-8") as file:
    file.write("\n".join(researcher_facts))

with open(os.path.join(output_dir, "department_facts.pro"), "w", encoding="utf-8") as file:
    file.write("\n".join(department_facts))

with open(os.path.join(output_dir, "publication_facts.pro"), "w", encoding="utf-8") as file:
    file.write("\n".join(publication_facts))

print("Akademisyen, departman ve yayın bilgileri Proton formatında dosyalara yazıldı.")
