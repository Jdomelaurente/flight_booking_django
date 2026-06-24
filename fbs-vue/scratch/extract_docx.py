import zipfile
import xml.etree.ElementTree as ET

def get_docx_text(path):
    """
    Take the path of a docx file as argument, return the text in unicode.
    """
    document = zipfile.ZipFile(path)
    xml_content = document.read('word/document.xml')
    document.close()
    tree = ET.fromstring(xml_content)
    
    # Namespaces
    ns = {'w': 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'}
    
    text = ""
    for paragraph in tree.findall('.//w:p', ns):
        for run in paragraph.findall('.//w:r', ns):
            for t in run.findall('.//w:t', ns):
                text += t.text
        text += "\n"
    return text

path = r"c:\Users\user\OneDrive\Desktop\Folders\Fbs\fbs-vue\docs\ADMIN-SIDE - 18 A PROPOSED _SMART FLIGHT BOOKING SIMULATION PLATFORM FOR CTHM-CSUCC_ AN INTERACTIVE AND DATA-DRIVEN TRAINING TOOL FOR HOSPITALITY AND TOURISM EDUCATION.docx"
try:
    content = get_docx_text(path)
    with open(r"c:\Users\user\OneDrive\Desktop\Folders\Fbs\fbs-vue\scratch\extracted_text.txt", "w", encoding="utf-8") as f:
        # Search for Table 4.3 or nearby content
        index = content.find("Table 4.3")
        if index != -1:
            f.write(content[index-500:index+5000])
        else:
            f.write("Table 4.3 not found. Printing first 5000 chars:\n")
            f.write(content[:5000])
            f.write("\n\nSearching for other tables...\n")
            import re
            tables = re.findall(r"Table \d\.\d", content)
            f.write(f"Found tables: {set(tables)}")
except Exception as e:
    with open(r"c:\Users\user\OneDrive\Desktop\Folders\Fbs\fbs-vue\scratch\extracted_text.txt", "w", encoding="utf-8") as f:
        f.write(f"Error: {e}")
