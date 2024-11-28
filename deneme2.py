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
    for file in files:
        try:
            prolog.consult(file)
            print(f"Yüklendi: {file}")
        except Exception as e:
            print(f"Prolog dosyası yüklenemedi: {file}. Hata: {e}")



def normalize_name(name):
    """İsimleri normalize ederek Prolog formatına uygun hale getirir."""
    name = name.strip()
    name = name.replace("dr", "Dr.").replace("doç", "Doç.").replace("prof", "Prof.").replace("i̇", "i")#ar gör eklenecek
    # Harfleri normalize et ve Prolog'ta string olarak ele alınması için tırnak içine al
    name = " ".join([word.capitalize() for word in name.split()])
    return f"'{name}'"


def llm_to_prolog_query(question):
    """LLM'den Prolog sorgusu oluşturur."""
    try:
        response = openai.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": f"You are an expert in Prolog query translation. Use these predicates: {predicates}. Ensure proper case sensitivity. Respond with only the Prolog query and no additional explanation."},
                {"role": "user", "content": f"Translate this question into a valid Prolog query: {question}. Only return a valid Prolog query without any explanation or context."}
            ]
        )
        prolog_query = response.choices[0].message.content.strip()
        print(f"Debug - LLM Sorgusu: {prolog_query}")
        
        # Predicate türünü belirle
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
    normalized_question = normalize_name(user_question)

    # LLM'den Prolog sorgusu oluştur
    prolog_query, query_type = llm_to_prolog_query(normalized_question)
    print(f"\nProlog Sorgusu:\n{prolog_query}")

    # Sorgu kontrolü
    if "LLM Hatası" in prolog_query:
        print(prolog_query)
    elif query_type not in predicates:
        print("Prolog Sorgusu Hatası: LLM tarafından yanlış bir sorgu üretildi.")
    else:
        # Prolog sorgusunu çalıştır
        prolog_results = execute_prolog_query(prolog_query)
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
