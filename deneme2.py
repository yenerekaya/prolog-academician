import openai
from pyswip import Prolog

# OpenAI API anahtarını ayarla
openai.api_key = "sk-xxx"

prolog = Prolog()

# Prolog Predicate yapıları
predicates = {
    "researcher": "researcher(Name, Department, Subfield).",
    "publication": "publication(Publication, Author).",
    "department": "department(DepartmentName, Researchers).",
}

def load_prolog_files(files):
    """Prolog dosyalarını yükler."""
    for file in files:
        try:
            prolog.consult(file)
            print(f"Yüklendi: {file}")
        except Exception as e:
            print(f"Prolog dosyası yüklenemedi: {file}. Hata: {e}")

def normalize_query(query, query_type):
    """Query'yi normalize ederek Prolog formatına uygun hale getirir."""
    if query_type == "publication":
        
        return query
    elif query_type == "researcher":
        
        predicate, args = query.split("(", 1)
        args = args.strip(").")  
        components = args.split(",")  
        
        
        def normalize_researcher_name(name):
            name = name.strip().lower()
            name = (
                name.replace("doç ", "Doç. ")
                    .replace("dr ", "Dr. ")
                    .replace("prof ", "Prof. ")
                    .replace("arş gör ", "Arş. Gör. ")
            )
            name = " ".join([word.capitalize() for word in name.split()])
            return f"'{name}'"

        normalized_components = []
        for component in components:
            component = component.strip()
            if component.startswith("'") and component.endswith("'"):  
                component = normalize_researcher_name(component[1:-1])  # Unvanları ve isimleri normalize et
            normalized_components.append(component)

        normalized_query = f"{predicate}({', '.join(normalized_components)})."
        return normalized_query
    else:
        
        predicate, args = query.split("(", 1)
        args = args.strip(").")
        components = args.split(",")
        
        normalized_components = []
        for component in components:
            component = component.strip()
            if component.startswith("'") and component.endswith("'"):
                component = component[0] + " ".join(
                    [word.capitalize() for word in component[1:-1].split()]
                ) + component[-1]
            normalized_components.append(component)
        
        normalized_query = f"{predicate}({', '.join(normalized_components)})."
        return normalized_query

def llm_to_prolog_query(question):
    """LLM'den Prolog sorgusu oluşturur."""
    try:
        response = openai.chat.completions.create(
            model="gpt-4",
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are an expert in Prolog query translation. "
                        "Use these predicates: researcher(Name, Department, Subfield), "
                        "publication(Publication, Author), department(DepartmentName, Researchers). "
                        "For `publication` queries, do NOT modify or normalize any part of the query. "
                        "Return the query exactly as provided in the question. "
                        "For other predicates, ensure the first letter of each word in strings is capitalized."
                    ),
                },
                {
                    "role": "user",
                    "content": f"Translate this question into a valid Prolog query: {question}. "
                               "Only return a valid Prolog query without any explanation or context.",
                },
            ]
        )
        prolog_query = response.choices[0].message.content.strip()

        
        if prolog_query.startswith("department"):
            query_type = "department"
        elif prolog_query.startswith("publication"):
            query_type = "publication"
        else:
            query_type = "researcher"

        return prolog_query, query_type
    except Exception as e:
        return f"LLM Hatası: {e}", None

def execute_prolog_query(query, limit=10):
    """Prolog sorgusunu çalıştırır."""
    try:
        if not query.endswith("."):
            query += "."
        print(f"Debug - Son Prolog Sorgusu: {query}")
        results = list(prolog.query(query))
        return results[:limit]
    except Exception as e:
        return f"Prolog Hatası: {e}"

def llm_process_results(question, results):
    """LLM ile Prolog sonuçlarını anlamlı şekilde açıklar."""
    try:
        response = openai.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are a helpful assistant summarizing Prolog query results."},
                {"role": "user", "content": f"Question: {question}\nResults: {results}\nSummarize these results for the user in a meaningful way."}
            ]
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"LLM Hatası: {e}"

if __name__ == "__main__":
    # Prolog dosyalarını yükle
    prolog_files = ["prolog-academician/researcher_facts.pro", 
                    "prolog-academician/department_facts.pro", 
                    "prolog-academician/publication_facts.pro"]
    load_prolog_files(prolog_files)

    # Kullanıcıdan soru al
    user_question = input("Soru: ")

    # LLM'den Prolog sorgusu oluştur
    prolog_query, query_type = llm_to_prolog_query(user_question)
    print(f"\nProlog Sorgusu:\n{prolog_query}")

    if "LLM Hatası" in prolog_query:
        print(prolog_query)
    elif query_type not in predicates:
        print("Prolog Sorgusu Hatası: LLM tarafından yanlış bir sorgu üretildi.")
    else:
        # Normalize edilmiş sorguyu al
        normalized_query = normalize_query(prolog_query, query_type)
        print(f"Debug - Normalize Edilmiş Sorgu: {normalized_query}")

        # Prolog sorgusunu çalıştır
        prolog_results = execute_prolog_query(normalized_query)

        if isinstance(prolog_results, str):
            print(prolog_results)
        elif not prolog_results:
            print("Prolog Sonuçları: Hiçbir sonuç bulunamadı.")
        else:
            print(f"\nProlog Sonuçları ({len(prolog_results)} sonuç):")
            for result in prolog_results:
                print(result)
            llm_response = llm_process_results(user_question, prolog_results)
            print("\nLLM Açıklaması:")
            print(llm_response)
