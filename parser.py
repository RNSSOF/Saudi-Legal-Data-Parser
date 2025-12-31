import os
import re
import json

def clean_text(text):
    """تنظيف النص من شوائب الـ OCR والفراغات الزائدة"""
    if not text: return ""
    text = re.sub(r'Page \d+', '', text)
    text = re.sub(r'ايضًأ', '', text)
    text = re.sub(r'\s+', ' ', text)
    return text.strip()

def parse_legal_text(file_path):
    """تحليل ملف تكست واحد واستخراج القضايا منه بناءً على منهجية الديوان"""
    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()
    
    # تقسيم المجلد بناءً على "رقم القضية" لضمان فصل القضايا عن بعضها وعن المقدمة
    case_blocks = re.split(r'(?=رقم القضية)', content)
    cases = []
    
    for block in case_blocks:
        # تجاهل الكتل التي لا تحتوي على أركان القضية الأساسية (مثل المقدمات)
        if "وقائع" not in block and "أسباب" not in block:
            continue
            
        # 1. استخراج البيانات التعريفية (رقم القضية، الحكم، التاريخ)
        header_info = block[:400].split("الموضوعات")[0]
        
        # 2. استخراج الموضوعات (بناءً على الكلمات المفتاحية في المنهجية)
        subjects = re.search(r'الموضوعات(.*?)مُستَندُ الحَكِ|الوَقَاتِعُ', block, re.S)
        
        # 3. استخراج مستند الحكم (الأنظمة واللوائح)
        legal_basis = re.search(r'مُستَندُ الحَكِ(.*?)الوَقَاتِعُ', block, re.S)
        
        # 4. استخراج الوقائع
        facts = re.search(r'الوَقَاتِعُ(.*?)الأسباب|وحيث إن|بناءً على', block, re.S)
        
        # 5. استخراج الأسباب (التسبيب القانوني)
        reasons = re.search(r'(?:الأسباب|وحيث إن|بناءً على)(.*?)(?=حكمت الدائرة|منطوق الحكم|لذلك)', block, re.S)
        
        # 6. استخراج المنطوق (الحكم النهائي)
        verdict = re.search(r'(?:حكمت الدائرة|منطوق الحكم)(.*?)(?=والله الموفق|$)', block, re.S)

        cases.append({
            "source_file": os.path.basename(file_path), # معرفة اسم الملف الأصلي لكل قضية
            "case_header": clean_text(header_info),
            "subjects": clean_text(subjects.group(1)) if subjects else "غير متوفر",
            "legal_basis": clean_text(legal_basis.group(1)) if legal_basis else "غير متوفر",
            "facts": clean_text(facts.group(1)) if facts else "غير متوفر",
            "reasons": clean_text(reasons.group(1)) if reasons else "غير متوفر",
            "verdict": clean_text(verdict.group(1)) if verdict else "غير متوفر",
            "full_original": clean_text(block) # النص الكامل للرجوع إليه عند الحاجة
        })
    return cases

# --- الجزء المسؤول عن الأتمتة والمعالجة الجماعية ---
def run_automation():
    input_folder = "./my_legal_texts" # تأكدي من إنشاء هذا المجلد ووضع الملفات فيه
    all_extracted_cases = []

    if not os.path.exists(input_folder):
        print(f"خطأ: المجلد {input_folder} غير موجود. يرجى إنشاؤه ووضع ملفات الـ txt بداخله.")
        return

    files = [f for f in os.listdir(input_folder) if f.endswith(".txt")]
    
    if not files:
        print("لا توجد ملفات txt داخل المجلد.")
        return

    print(f"تم العثور على {len(files)} ملفات. بدء المعالجة...")

    for filename in files:
        file_path = os.path.join(input_folder, filename)
        print(f"جاري استخراج البيانات من: {filename}...")
        try:
            file_cases = parse_legal_text(file_path)
            all_extracted_cases.extend(file_cases)
            print(f"بنجاح: تم استخراج {len(file_cases)} قضية من {filename}")
        except Exception as e:
            print(f"خطأ في معالجة الملف {filename}: {e}")

    # حفظ النتيجة النهائية في ملف واحد
    output_filename = "final_intellectual_property_db.json"
    with open(output_filename, "w", encoding="utf-8") as f:
        json.dump(all_extracted_cases, f, ensure_ascii=False, indent=4)
    
    print("-" * 30)
    print(f"اكتملت العملية بنجاح!")
    print(f"إجمالي القضايا المستخرجة: {len(all_extracted_cases)}")
    print(f"تم حفظ الملف النهائي باسم: {output_filename}")

if __name__ == "__main__":
    run_automation()