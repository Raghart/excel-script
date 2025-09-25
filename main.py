from put_excel import put_date, put_area, put_equipment, put_images, diary_format, clean_area, text_day
from put_excel import text_day, put_bote, put_personal
from openpyxl import load_workbook

WB = load_workbook('REPORTE DIARIO.xlsx')
sheet = WB[text_day]
sheet_diary = WB['FORMATO DIARIO']
sheet_bote = WB['BOTE']

def diary_inform():
    try:
        print(diary_format(sheet_diary))
        print(put_date(sheet))
        print(clean_area(sheet))
        print(put_area(sheet))
        print(put_equipment(sheet))
        print(put_personal(sheet))
        print(put_images(sheet))
        print(put_bote(sheet_bote))
        WB.save('REPORTE DIARIO.xlsx')
        
        return f"Diary Inform for {text_day} Done!"
    
    except Exception as e:
        return f"An error ocurred {e}"

print(diary_inform())