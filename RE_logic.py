import re

# Extracting executed quantity from the report
def extract_quantity(report):
    cantidad_match = re.search(r'Cantidad\s*Ejecutada\s*:\s*(\d+[.,]?\d*)\s*m', report)
    if not cantidad_match:
        raise ValueError('There is no Quantity match in this inform')
    return float(cantidad_match.group(1).replace(',', '.'))

# Extracting executed date from the report
def extract_date(report):
    date_match = re.search(r'Fecha\s+(\w+)\s+(\d{2}/\d{2}/\d{4})', report)
    if date_match:
        text_day = date_match.group(1).upper()
        date_text = date_match.group(2).replace('2024','2025')
        return text_day, date_text
    raise ValueError('There is no Date match format in this inform')

# Extracting executed Item from the report
def extract_item(report):
    partida_match = re.search(r'Actividades\s*:\s*correspondiente\s*a\s*partida\s*N#\s*(\d+(\.\d+)?)', report)
    if partida_match:
        return partida_match.group(1)
    raise ValueError("There is no Valid Item Number text in this inform")

# Extracting used Equipment from the report
def extract_equipment(report):
    equip_match_unpolished = re.search(r'Equipos\s*\/\s*herramientas\s*requeridos\s*en\s*Obra\s*:\s*(.*?)(?=,?\s*botiquín de primeros auxilios)', report, re.DOTALL)
    
    if equip_match_unpolished:
        equip_text = equip_match_unpolished.group(1).strip().upper()
        return f"HERRAMIENTAS MANUALES ({equip_text})"
    raise ValueError("There is no Equipment match format in this inform")

# Extracting executed Area from the report
def extract_area(report):
    workarea_match = re.search(r'Ubicación\s*de\s*la\s*actividad\s*:\s*(.*?)(?:\r?\n|$)', report, re.DOTALL)
    if workarea_match:
        return workarea_match.group(1).strip().upper() + " (ÁREA PLANIFICADA)"
    raise ValueError('There is no Work Area or Plan match format in this inform')

# Extract the total sum of dangerous and non-dangerous waste
def extract_bote(report):
    hazardous_quantity_match = re.search(r'Disposición\s*=\s*traslado\s*a\s*los\s*nísperos\s*RPLC\s*\.(.*?)CANTIDAD\s*ACUMULADA\s*(\d+\.\d+)m3', report, re.DOTALL)
    non_hazardous_quantity_match = re.search(r'CANTIDAD\s*ACUMULADA\s*EN\s*BOTE\s*DE\s*DESECHOS\s*NO\s*PELIGROSOS(.*?)CANTIDAD\s*ACUMULADA\s*(\d+\.\d+)m3', report, re.DOTALL)

    if hazardous_quantity_match and non_hazardous_quantity_match:
        total_haz_waste_quantity = float(hazardous_quantity_match.group(2))
        total_safe_waste_quantity = float(non_hazardous_quantity_match.group(2))

        return total_haz_waste_quantity, total_safe_waste_quantity
    raise ValueError("There is no Valid Total hazaraous waste quantity or Total Safe quantity")

# Extract the date and quantities of the waste
def extract_waste(report, pattern, error_message):
    matches = re.findall(pattern, report, re.DOTALL)
    if matches:
        waste_data = re.findall(r"(\d{2}-\d{2}-\d{4}) Cant=\s*(\d+\.\d+)", matches[0])
        if waste_data:
            return waste_data
        raise ValueError(error_message)
    raise ValueError(error_message)

# Extract the safe date and quantities of the waste data
def extract_safe_waste(report):
    RE_safe_waste = r"CANTIDAD\s*ACUMULADA\s*EN\s*BOTE\s*DE\s*DESECHOS\s*NO\s*PELIGROSOS\s*Tipo\s*sedimento\s*no\s*contaminado\s*\(SNC\)\s*((?:\d{2}-\d{2}-\d{4}\s*Cant=\s*\d+\.\d+m3\s*)+)CANTIDAD\s*ACUMULADA"
    return extract_waste(report, RE_safe_waste, 'No Safe waste date and quantities found in the inform')

# Extract the dangerous date and quantities of the waste data
def extract_dangerous_waste(report):
    RE_dangerous_waste = r"CANTIDAD\s*EJECUTADA\s*EN\s*BOTE\s*DE\s*DESECHOS\s*DESECHOS\s*PELIGROSOS\s*TIPO\s*SEDIMENTO\s*CONTAMINADO\s*\(SC\)\s*((?:\d{2}-\d{2}-\d{4}\s*Cant=\s*\d+\.\d+\s*m3\s*)+)Disposición\s*=\s*traslado\s*a\s*los\s*nísperos\s*RPLC\."
    return extract_waste(report, RE_dangerous_waste, 'No Dangerous waste date and quantities found in the inform')

# Extracting The Indirect Personal from the report
def extract_indirect_personal(report):
    indirect_match = re.search(r'INDIRECTO\s*:\s*(.*?)(?=\n\n|\Z)', report, re.DOTALL)
    
    if indirect_match:
        indirect_text = indirect_match.group(1).strip().upper()
        indirect_text = re.sub(r'\s*=\s*01', '', indirect_text)

        desired_order = [
            "GERENTE DE PROYECTO",
            "COORDINADOR DE EJECUCION DE OBRA",
            "ADMINISTRADOR DE CONTRATOS / PLANIFICADOR",
            "COORDINADOR LABORAL",
            "COORDINADOR SIHO-A",   
            "INSPECTOR SIHO",
            "SUPERVISOR DE OBRA",
            "PARAMÉDICO",
            "CHOFER DE AMBULANCIA",
            "CHOFER DE CAMIÓN VOLTEO",
            "OPERADOR DE RETROEXCAVADORA"
        ]

        name_mapping = {
            "COORDINADOR SIHOA": "COORDINADOR SIHO-A",
            "PLANIFICADOR": "ADMINISTRADOR DE CONTRATOS / PLANIFICADOR",
            "COORDINADOR DE EJECUCIÓN": "COORDINADOR DE EJECUCION DE OBRA"
        }

        indirect = [line.strip() for line in indirect_text.split('\n')]
        indice = indirect.index('OPERADOR DE RETROEXCAVADORA') + 1
        indirect = indirect[:indice]
        indirect = [name_mapping.get(name, name) for name in indirect]
        return [name for name in desired_order if name in indirect]
    raise ValueError('No Indirect Match Section in this inform')

# Extracting The Direct Personal from the report
def extract_direct_personal(report):
    direct_worker_match = re.search(r'Obreros\s+DIRECTO:=\s*(\d+)', report)
    indirect_worker_match = re.search(r'Obreros\s+indirecto=\s*(\d+)', report)

    if direct_worker_match and indirect_worker_match:
        num_dir_worker = int(direct_worker_match.group(1))
        num_indir_worker = int(indirect_worker_match.group(1))

        if num_dir_worker == 1 and num_indir_worker == 2:
            direct_workers = {'OBREROS': num_dir_worker}
            indirect_workers = {
                'ANALISTA DE LOGÍSTICA Y PROCURA' : 1,
                'ASISTENTE DE MANTENIMIENTO Y LOGISTICA': 1 
            }
            return direct_workers, indirect_workers
        raise ValueError('There is a Change in the number of Workers, there is no 1 Direct and 2 indirect!')
    raise ValueError('Indirect and Directs workers match not found')