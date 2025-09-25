from RE_logic import extract_quantity, extract_date, extract_item, extract_area, extract_equipment
from RE_logic import extract_bote
from RE_logic import extract_safe_waste, extract_dangerous_waste
from inform import informe

report = informe()
cantidad_ex = extract_quantity(report)
text_day, date_text = extract_date(report)
num_partida = extract_item(report)
equip = extract_equipment(report)
total_haz_waste_quantity, total_safe_waste_quantity = extract_bote(report)
safe_waste_data = extract_safe_waste(report)
dangerous_waste_data = extract_dangerous_waste(report)

def additional_info():
    info_text=[]
    if cantidad_ex:
        cantidad_text = f"METROS LINEALES DE LIMPIEZA EN AREAS DESCRITAS: {cantidad_ex:.2f} m".replace('.',',')
        canal_text = 'CANAL TIPO "V"'
        generic_text = "DESECHOS GENERADOS TIPO SEDIMENTOS ACUMULADOS, MALEZA Y RESTOS DE VEGETACION."

        info_text.extend([cantidad_text, canal_text, generic_text])
        return info_text
    
    raise ValueError('There is no Cantidad match to add in this inform')

def input_workarea():
    add_text = []
    sum_area = []
    print(f"Area de Trabajo a {date_text}: {extract_area(report)}")

    try:
        while True:
            work_area = input("Input the information for one Line: ")
            add_text.append(work_area)
            sum_area.append(work_area)

    except KeyboardInterrupt:
        print('Finishing the Data Entry!')
        add_text += additional_info()

    return add_text, sum_area
    

def get_summarized_area(sum_area):
    if sum_area:
        summarized_area = " / ".join(sum_area)
        return "Área: " + summarized_area.replace(" (ÁREA PLANIFICADA)", "")
    raise ValueError('There is an error in the input information (summarized area)')

def get_actual_bote(sheet):
    sum_last_dangerous_waste = sheet['A29'].value
    last_dangerous_waste_executed = sheet['C32'].value if sheet['C32'].value else 0

    if sum_last_dangerous_waste is not None and last_dangerous_waste_executed is not None:
        sum_last_dangerous_waste = float(sum_last_dangerous_waste)
        last_dangerous_waste_executed = float(last_dangerous_waste_executed)
        total_last_dangerous_quantity = round(last_dangerous_waste_executed + sum_last_dangerous_waste, 2)

        sum_last_safe_waste = sheet['D29'].value
        last_safe_waste_executed = sheet['E32'].value if sheet['E32'].value else 0

        if sum_last_safe_waste is not None and last_safe_waste_executed is not None:
            sum_last_safe_waste = float(sum_last_safe_waste)
            last_safe_waste_executed = float(last_safe_waste_executed)
            total_last_safe_quantity = round(sum_last_safe_waste + last_safe_waste_executed, 2)

            print(f"{total_haz_waste_quantity} == {total_last_dangerous_quantity}")
            print(f"{total_safe_waste_quantity} == {total_last_safe_quantity}")

            return total_last_safe_quantity, total_last_dangerous_quantity
        raise ValueError("There are no valid numbers in the last safe bote to add to the actual bote")
    raise ValueError("There are no valid numbers in the last dangerous bote to add to the actual bote")
