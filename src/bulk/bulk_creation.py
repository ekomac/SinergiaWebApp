import os
import json
from places.models import Partido, Town, Zone, ZipCode
from prices.models import DeliveryCode, FlexCode


mensajerias = [
    {'code': 'M01', 'price': 380},
    {'code': 'M02', 'price': 400},
    {'code': 'M03', 'price': 480},
    {'code': 'M04', 'price': 550},
    {'code': 'M05', 'price': 650},
    {'code': 'M06', 'price': 700},
    {'code': 'M07', 'price': 750},
    {'code': 'M08', 'price': 800},
    {'code': 'M09', 'price': 900},
    {'code': 'M10', 'price': 950},
    {'code': 'M11', 'price': 1000},
    {'code': 'M12', 'price': 1100},
    {'code': 'M13', 'price': 1200},
    {'code': 'M14', 'price': 1300},
    {'code': 'M15', 'price': 1500},
]

flexs = [
    {'code': 'F01', 'price': 380},
    {'code': 'F02', 'price': 600},
    {'code': 'F03', 'price': 820},
]

partidos = [
    'ALMIRANTE BROWN', 'AVELLANEDA', 'BERAZATEGUI', 'CABA', 'ESCOBAR',
    'ESTEBAN ECHEVERRIA', 'EXALTACION DE LA CRUZ', 'EZEIZA',
    'FLORENCIO VARELA', 'GENERAL RODRIGUEZ', 'GENERAL SAN MARTIN',
    'HURLINGHAM', 'ITUZAINGO', 'JOSE C. PAZ', 'MERLO', 'LA MATANZA',
    'LA MATANZA NORTE', 'LANUS', 'LOMAS DE ZAMORA', 'LUJAN',
    'MALVINAS ARGENTINAS', 'MORENO', 'MORON', 'PILAR', 'QUILMES',
    'SAN FERNANDO', 'SAN ISIDRO', 'SAN MIGUEL', 'TIGRE',
    'TRES DE FEBRERO', 'VICENTE LOPEZ']

localidades = [
    ('ADROGUE', 'ALMIRANTE BROWN', 'M13', 'F03'),
    ('BURZACO', 'ALMIRANTE BROWN', 'M14', 'F03'),
    ('CLAYPOLE', 'ALMIRANTE BROWN', 'M14', 'F03'),
    ('DON ORIONE', 'ALMIRANTE BROWN', 'M14', 'F03'),
    ('GLEW', 'ALMIRANTE BROWN', 'M14', 'F03'),
    ('JOSE MARMOL', 'ALMIRANTE BROWN', 'M13', 'F03'),
    ('LONGCHAMPS', 'ALMIRANTE BROWN', 'M14', 'F03'),
    ('MALVINAS ARGENTINAS', 'ALMIRANTE BROWN', 'M13', 'F03'),
    ('MINISTRO RIVADAVIA', 'ALMIRANTE BROWN', 'M14', 'F03'),
    ('RAFAEL CALZADA', 'ALMIRANTE BROWN', 'M13', 'F03'),
    ('SAN FRANCISCO SOLANO', 'ALMIRANTE BROWN', 'M14', 'F03'),
    ('SAN JOSE', 'ALMIRANTE BROWN', 'M13', 'F03'),
    ('AREA CINTURON ECOLOGICO', 'AVELLANEDA', 'M13', 'F03'),
    ('AVELLANEDA', 'AVELLANEDA', 'M12', 'F03'),
    ('CRUCESITA', 'AVELLANEDA', 'M12', 'F03'),
    ('DOCK SUD', 'AVELLANEDA', 'M12', 'F03'),
    ('GERLI', 'AVELLANEDA', 'M13', 'F03'),
    ('PINEYRO', 'AVELLANEDA', 'M12', 'F03'),
    ('SARANDI', 'AVELLANEDA', 'M13', 'F03'),
    ('VILLA DOMINICO', 'AVELLANEDA', 'M13', 'F03'),
    ('WILDE', 'AVELLANEDA', 'M13', 'F03'),
    ('BERAZATEGUI', 'BERAZATEGUI', 'M14', 'F03'),
    ('BERAZATEGUI OESTE', 'BERAZATEGUI', 'M14', 'F03'),
    ('CARLOS TOMAS SOURIGUES', 'BERAZATEGUI', 'M15', 'F03'),
    ('SOURIGUES', 'BERAZATEGUI', 'M15', 'F03'),
    ('EL PATO', 'BERAZATEGUI', 'M15', 'F03'),
    ('GUILLERMO ENRIQUE HUDSON', 'BERAZATEGUI', 'M15', 'F03'),
    ('HUDSON', 'BERAZATEGUI', 'M15', 'F03'),
    ('JUAN MARIA GUTIERREZ', 'BERAZATEGUI', 'M15', 'F03'),
    ('GUTIERREZ', 'BERAZATEGUI', 'M15', 'F03'),
    ('PEREYRA', 'BERAZATEGUI', 'M15', 'F03'),
    ('PLATANOS', 'BERAZATEGUI', 'M15', 'F03'),
    ('RANELAGH', 'BERAZATEGUI', 'M15', 'F03'),
    ('VILLA ESPANA', 'BERAZATEGUI', 'M12', 'F03'),
    ('AGRONOMIA', 'CABA', 'M09', 'F03'),
    ('ALMAGRO', 'CABA', 'M11', 'F03'),
    ('BALVANERA', 'CABA', 'M11', 'F03'),
    ('BARRACAS', 'CABA', 'M11', 'F03'),
    ('BELGRANO', 'CABA', 'M09', 'F03'),
    ('BOCA', 'CABA', 'M11', 'F03'),
    ('LA BOCA', 'CABA', 'M11', 'F03'),
    ('BOEDO', 'CABA', 'M11', 'F03'),
    ('CABALLITO', 'CABA', 'M11', 'F03'),
    ('CHACARITA', 'CABA', 'M09', 'F03'),
    ('COGHLAN', 'CABA', 'M09', 'F03'),
    ('COLEGIALES', 'CABA', 'M09', 'F03'),
    ('CONSTITUCION', 'CABA', 'M11', 'F03'),
    ('FLORES', 'CABA', 'M11', 'F03'),
    ('FLORESTA', 'CABA', 'M11', 'F03'),
    ('LINIERS', 'CABA', 'M09', 'F03'),
    ('MATADEROS', 'CABA', 'M11', 'F03'),
    ('MONSERRAT', 'CABA', 'M11', 'F03'),
    ('MONTE CASTRO', 'CABA', 'M09', 'F03'),
    ('NUEVA POMPEYA', 'CABA', 'M11', 'F03'),
    ('POMPEYA', 'CABA', 'M11', 'F03'),
    ('NUNEZ', 'CABA', 'M09', 'F03'),
    ('PALERMO', 'CABA', 'M11', 'F03'),
    ('PARQUE AVELLANEDA', 'CABA', 'M09', 'F03'),
    ('PARQUE CHACABUCO', 'CABA', 'M09', 'F03'),
    ('PARQUE CHAS', 'CABA', 'M09', 'F03'),
    ('PARQUE PATRICIOS', 'CABA', 'M09', 'F03'),
    ('PATERNAL', 'CABA', 'M09', 'F03'),
    ('PUERTO MADERO', 'CABA', 'M11', 'F03'),
    ('RECOLETA', 'CABA', 'M11', 'F03'),
    ('RETIRO', 'CABA', 'M11', 'F03'),
    ('SAAVEDRA', 'CABA', 'M09', 'F03'),
    ('SAN CRISTOBAL', 'CABA', 'M11', 'F03'),
    ('SAN NICOLAS', 'CABA', 'M11', 'F03'),
    ('SAN TELMO', 'CABA', 'M11', 'F03'),
    ('VELEZ SARSFIELD', 'CABA', 'M09', 'F03'),
    ('VERSALLES', 'CABA', 'M09', 'F03'),
    ('VILLA CRESPO', 'CABA', 'M09', 'F03'),
    ('VILLA DEL PARQUE', 'CABA', 'M09', 'F03'),
    ('VILLA DEVOTO', 'CABA', 'M09', 'F03'),
    ('DEVOTO', 'CABA', 'M09', 'F03'),
    ('VILLA GENERAL MITRE', 'CABA', 'M09', 'F03'),
    ('VILLA LUGANO', 'CABA', 'M11', 'F03'),
    ('VILLA LURO', 'CABA', 'M11', 'F03'),
    ('VILLA ORTUZAR', 'CABA', 'M11', 'F03'),
    ('VILLA PUEYRREDON', 'CABA', 'M09', 'F03'),
    ('VILLA REAL', 'CABA', 'M09', 'F03'),
    ('VILLA RIACHUELO', 'CABA', 'M11', 'F03'),
    ('VILLA SANTA RITA', 'CABA', 'M11', 'F03'),
    ('VILLA SOLDATI', 'CABA', 'M11', 'F03'),
    ('VILLA URQUIZA', 'CABA', 'M09', 'F03'),
    ('BELEN DE ESCOBAR', 'ESCOBAR', 'M09', 'F03'),
    ('ESCOBAR', 'ESCOBAR', 'M09', 'F03'),
    ('EL CAZADOR', 'ESCOBAR', 'M09', 'F03'),
    ('GARIN', 'ESCOBAR', 'M08', 'F03'),
    ('INGENIERO MASCHWITZ', 'ESCOBAR', 'M08', 'F03'),
    ('MASCHWITZ', 'ESCOBAR', 'M08', 'F03'),
    ('LOMA VERDE', 'ESCOBAR', 'M08', 'F03'),
    ('MAQUINISTA F. SAVIO ESTE', 'ESCOBAR', 'M08', 'F03'),
    ('MAQUINISTA SAVIO ESTE', 'ESCOBAR', 'M08', 'F03'),
    ('MAQUINISTA F SAVIO ESTE', 'ESCOBAR', 'M08', 'F03'),
    ('MATHEU', 'ESCOBAR', 'M08', 'F03'),
    ('9 DE ABRIL', 'ESTEBAN ECHEVERRIA', 'M10', 'F03'),
    ('CANNING', 'ESTEBAN ECHEVERRIA', 'M12', 'F03'),
    ('EL JAGUEL', 'ESTEBAN ECHEVERRIA', 'M12', 'F03'),
    ('LUIS GUILLON', 'ESTEBAN ECHEVERRIA', 'M12', 'F03'),
    ('MONTE GRANDE', 'ESTEBAN ECHEVERRIA', 'M12', 'F03'),
    ('ARROYO DE LA CRUZ', 'EXALTACION DE LA CRUZ', 'M13', 'F03'),
    ('CAPILLA DEL SENOR', 'EXALTACION DE LA CRUZ', 'M13', 'F03'),
    ('DIEGO GAYNOR', 'EXALTACION DE LA CRUZ', 'M14', 'F03'),
    ('EL REMANSO', 'EXALTACION DE LA CRUZ', 'M13', 'F03'),
    ('LOS CARDALES', 'EXALTACION DE LA CRUZ', 'M13', 'F03'),
    ('PARADA ORLANDO', 'EXALTACION DE LA CRUZ', 'M13', 'F03'),
    ('PARADA ROBLES', 'EXALTACION DE LA CRUZ', 'M13', 'F03'),
    ('PAVON', 'EXALTACION DE LA CRUZ', 'M13', 'F03'),
    ('AEROPUERTO INTERNACIONAL EZEIZA', 'EZEIZA', 'M12', 'F03'),
    ('CANNING', 'EZEIZA', 'M10', 'F03'),
    ('CARLOS SPEGAZZINI', 'EZEIZA', 'M12', 'F03'),
    ('JOSE MARIA EZEIZA', 'EZEIZA', 'M10', 'F03'),
    ('EZEIZA', 'EZEIZA', 'M10', 'F03'),
    ('LA UNION', 'EZEIZA', 'M12', 'F03'),
    ('TRISTAN SUAREZ', 'EZEIZA', 'M12', 'F03'),
    ('BOSQUES', 'FLORENCIO VARELA', 'M12', 'F03'),
    ('EL TROPEZON', 'FLORENCIO VARELA', 'M12', 'F03'),
    ('TROPEZON', 'FLORENCIO VARELA', 'M12', 'F03'),
    ('ESTANISLAO SEVERO ZEBALLOS', 'FLORENCIO VARELA', 'M12', 'F03'),
    ('ZEBALLOS', 'FLORENCIO VARELA', 'M12', 'F03'),
    ('FLORENCIO VARELA', 'FLORENCIO VARELA', 'M10', 'F03'),
    ('GOBERNADOR JULIO A. COSTA', 'FLORENCIO VARELA', 'M10', 'F03'),
    ('INGENIERO JUAN ALLAN', 'FLORENCIO VARELA', 'M12', 'F03'),
    ('LA CAPILLA', 'FLORENCIO VARELA', 'M12', 'F03'),
    ('VILLA BROWN', 'FLORENCIO VARELA', 'M12', 'F03'),
    ('VILLA SAN LUIS', 'FLORENCIO VARELA', 'M12', 'F03'),
    ('VILLA SANTA ROSA', 'FLORENCIO VARELA', 'M12', 'F03'),
    ('VILLA VATTEONE', 'FLORENCIO VARELA', 'M12', 'F03'),
    ('BARRIO MORABO', 'GENERAL RODRIGUEZ', 'M08', 'F03'),
    ('BARRIO RUTA 24 KILOMETRO 10', 'GENERAL RODRIGUEZ', 'M06', 'F03'),
    ('BARRIO RUTA 24 KM. 10', 'GENERAL RODRIGUEZ', 'M06', 'F03'),
    ('C.C. BOSQUE REAL', 'GENERAL RODRIGUEZ', 'M08', 'F03'),
    ('BOSQUE REAL', 'GENERAL RODRIGUEZ', 'M08', 'F03'),
    ('GENERAL RODRGUEZ', 'GENERAL RODRIGUEZ', 'M08', 'F03'),
    ('RODRIGUEZ', 'GENERAL RODRIGUEZ', 'M08', 'F03'),
    ('BARRIO PARQUE GENERAL SAN MARTIN', 'GENERAL SAN MARTIN', 'M05', 'F02'),
    ('SAN MARTIN', 'GENERAL SAN MARTIN', 'M05', 'F02'),
    ('BARRIO PARQUE', 'GENERAL SAN MARTIN', 'M05', 'F02'),
    ('BILLINGHURST', 'GENERAL SAN MARTIN', 'M05', 'F02'),
    ('CIUDAD DEL LIBERTADOR GENERAL SAN MARTIN',
     'GENERAL SAN MARTIN', 'M05', 'F02'),
    ('CIUDAD JARDIN EL LIBERTADOR', 'GENERAL SAN MARTIN', 'M05', 'F02'),
    ('VILLA AYACUCHO', 'GENERAL SAN MARTIN', 'M05', 'F02'),
    ('VILLA BALLESTER', 'GENERAL SAN MARTIN', 'M05', 'F02'),
    ('VILLA BERNARDO MONTEAGUDO', 'GENERAL SAN MARTIN', 'M05', 'F02'),
    ('VILLA CHACABUCO', 'GENERAL SAN MARTIN', 'M05', 'F02'),
    ('VILLA CORONEL JOSE M. ZAPIOLA', 'GENERAL SAN MARTIN', 'M05', 'F02'),
    ('VILLA GENERAL ANTONIO J. DE SUCRE', 'GENERAL SAN MARTIN', 'M05', 'F02'),
    ('VILLA GENERAL EUGENIO NECOCHEA', 'GENERAL SAN MARTIN', 'M05', 'F02'),
    ('VILLA GENERAL JOSE TOMAS GUIDO', 'GENERAL SAN MARTIN', 'M05', 'F02'),
    ('VILLA GENERAL JUAN G. LAS HERAS', 'GENERAL SAN MARTIN', 'M05', 'F02'),
    ('VILLA GODOY CRUZ', 'GENERAL SAN MARTIN', 'M05', 'F02'),
    ('VILLA GRANADEROS DE SAN MARTIN', 'GENERAL SAN MARTIN', 'M05', 'F02'),
    ('VILLA GREGORIA MATORRAS', 'GENERAL SAN MARTIN', 'M05', 'F02'),
    ('VILLA JOSE LEON SUAREZ', 'GENERAL SAN MARTIN', 'M05', 'F02'),
    ('VILLA JUAN MARTIN DE PUEYRREDON', 'GENERAL SAN MARTIN', 'M05', 'F02'),
    ('VILLA LIBERTAD', 'GENERAL SAN MARTIN', 'M05', 'F02'),
    ('VILLA LYNCH', 'GENERAL SAN MARTIN', 'M05', 'F02'),
    ('VILLA MAIPU', 'GENERAL SAN MARTIN', 'M05', 'F02'),
    ('VILLA MARIA IRENE DE LOS REMEDIOS DE ESCALADA',
     'GENERAL SAN MARTIN', 'M05', 'F02'),
    ('MARIA IRENE DE LOS REMEDIOS DE ESCALADA', 'GENERAL SAN MARTIN', 'M05',
     'F02'),
    ('VILLA MARQUES ALEJANDRO MARIA DE AGUADO', 'GENERAL SAN MARTIN', 'M05',
     'F02'),
    ('VILLA PARQUE PRESIDENTE FIGUEROA ALCORTA',
     'GENERAL SAN MARTIN', 'M05', 'F02'),
    ('VILLA PARQUE SAN LORENZO', 'GENERAL SAN MARTIN', 'M05', 'F02'),
    ('VILLA SAN ANDRES', 'GENERAL SAN MARTIN', 'M05', 'F02'),
    ('VILLA YAPEYU', 'GENERAL SAN MARTIN', 'M05', 'F02'),
    ('HURLINGHAM', 'HURLINGHAM', 'M03', 'F02'),
    ('VILLA SANTOS TESEI', 'HURLINGHAM', 'M03', 'F02'),
    ('WILLIAM C. MORRIS', 'HURLINGHAM', 'M02', 'F02'),
    ('ITUZAINGO CENTRO', 'ITUZAINGO', 'M05', 'F02'),
    ('ITUZAINGO SUR', 'ITUZAINGO', 'M05', 'F02'),
    ('VILLA GOBERNADOR UDAONDO', 'ITUZAINGO', 'M04', 'F02'),
    ('DEL VISO', 'JOSE C. PAZ', 'M04', 'F01'),
    ('JOSE C. PAZ', 'JOSE C. PAZ', 'M03', 'F01'),
    ('TORTUGUITAS', 'JOSE C. PAZ', 'M03', 'F01'),
    ('20 DE JUNIO', 'MERLO', 'M10', 'F03'),
    ('ALDO BONZI', 'LA MATANZA', 'M10', 'F03'),
    ('CIUDAD EVITA', 'LA MATANZA', 'MNN', 'F03'),
    ('GONZALEZ CATAN', 'LA MATANZA', 'M10', 'F03'),
    ('GONZALEZS CATAN', 'LA MATANZA', 'M11', 'F03'),
    ('GREGORIO DE LAFERRERE', 'LA MATANZA', 'M10', 'F03'),
    ('ISIDRO CASANOVA', 'LA MATANZA', 'M10', 'F03'),
    ('LA MATANZA', 'LA MATANZA NORTE', 'M07', 'F03'),
    ('LA TABLADA', 'LA MATANZA', 'M10', 'F03'),
    ('LOMAS DEL MIRADOR', 'LA MATANZA', 'M07', 'F03'),
    ('RAFAEL CASTILLO', 'LA MATANZA', 'M10', 'F03'),
    ('RAMOS MEJIA', 'LA MATANZA', 'M07', 'F03'),
    ('SAN JUSTO', 'LA MATANZA', 'M07', 'F03'),
    ('TAPIALES', 'LA MATANZA', 'M10', 'F03'),
    ('VILLA CELINA', 'LA MATANZA', 'M10', 'F03'),
    ('VILLA EDUARDO MADERO', 'LA MATANZA', 'M07', 'F03'),
    ('VILLA LUZURIAGA', 'LA MATANZA', 'M07', 'F03'),
    ('VIRREY DEL PINO', 'LA MATANZA', 'M10', 'F03'),
    ('GERLI', 'LANUS', 'M13', 'F03'),
    ('LANUS ESTE', 'LANUS', 'M12', 'F03'),
    ('LANUS OESTE', 'LANUS', 'M12', 'F03'),
    ('LANUS', 'LANUS', 'M12', 'F03'),
    ('MONTE CHINGOLO', 'LANUS', 'M13', 'F03'),
    ('REMEDIOS ESCALADA DE SAN MARTIN', 'LANUS', 'M13', 'F03'),
    ('REMEDIOS DE ESCALADA DE SAN MARTIN', 'LANUS', 'M13', 'F03'),
    ('REMEDIOS DE ESCALADA', 'LANUS', 'M13', 'F03'),
    ('VALENTIN ALSINA', 'LANUS', 'M12', 'F03'),
    ('BANFIELD', 'LOMAS DE ZAMORA', 'M12', 'F03'),
    ('LLAVALLOL', 'LOMAS DE ZAMORA', 'M12', 'F03'),
    ('LOMAS DE ZAMORA', 'LOMAS DE ZAMORA', 'M12', 'F03'),
    ('TEMPERLEY', 'LOMAS DE ZAMORA', 'M13', 'F03'),
    ('TURDERA', 'LOMAS DE ZAMORA', 'M13', 'F03'),
    ('VILLA CENTENARIO', 'LOMAS DE ZAMORA', 'M12', 'F03'),
    ('VILLA FIORITO', 'LOMAS DE ZAMORA', 'M13', 'F03'),
    ('CARLOS KEEN', 'LUJAN', 'M14', 'F03'),
    ('CORTINES', 'LUJAN', 'M14', 'F03'),
    ('COUNTRY CLUB LAS PRADERAS', 'LUJAN', 'M13', 'F03'),
    ('LUJAN', 'LUJAN', 'M13', 'F03'),
    ('LUJAN', 'LUJAN', 'M13', 'F03'),
    ('OLIVERA', 'LUJAN', 'M14', 'F03'),
    ('OPEN DOOR', 'LUJAN', 'M13', 'F03'),
    ('TORRES', 'LUJAN', 'M13', 'F03'),
    ('VILLA FLANDRIA NORTE (PUEBLO NUEVO)', 'LUJAN', 'M14', 'F03'),
    ('VILLA FLANDRIA SUR (EST. JAUREGUI)', 'LUJAN', 'M14', 'F03'),
    ('AREA DE PROMOCION EL TRIANGULO', 'MALVINAS ARGENTINAS', 'M04', 'F02'),
    ('GRAND BOURG', 'MALVINAS ARGENTINAS', 'M04', 'F02'),
    ('INGENIERO ADOLFO SOURDEAUX', 'MALVINAS ARGENTINAS', 'M03', 'F02'),
    ('INGENIERO PABLO NOGUES', 'MALVINAS ARGENTINAS', 'M03', 'F02'),
    ('LOS POLVORINES', 'MALVINAS ARGENTINAS', 'M03', 'F02'),
    ('TORTUGUITAS', 'MALVINAS ARGENTINAS', 'M03', 'F02'),
    ('VILLA DE MAYO', 'MALVINAS ARGENTINAS', 'M03', 'F02'),
    ('LIBERTAD', 'MERLO', 'M07', 'F03'),
    ('MARIANO ACOSTA', 'MERLO', 'M07', 'F03'),
    ('MERLO', 'MERLO', 'M05', 'F03'),
    ('PONTEVEDRA', 'MERLO', 'M07', 'F03'),
    ('SAN ANTONIO DE PADUA', 'MERLO', 'M05', 'F03'),
    ('CUARTEL V', 'MORENO', 'M05', 'F02'),
    ('FRANCISCO ALVAREZ', 'MORENO', 'M05', 'F02'),
    ('LA REJA', 'MORENO', 'M05', 'F02'),
    ('MORENO', 'MORENO', 'M04', 'F02'),
    ('PASO DEL REY', 'MORENO', 'M05', 'F02'),
    ('TRUJUI', 'MORENO', 'M04', 'F02'),
    ('CASTELAR', 'MORON', 'M05', 'F02'),
    ('EL PALOMAR', 'MORON', 'M05', 'F02'),
    ('HAEDO', 'MORON', 'M05', 'F02'),
    ('MORON', 'MORON', 'M07', 'F02'),
    ('VILLA SARMIENTO', 'MORON', 'M07', 'F02'),
    ('DEL VISO', 'PILAR', 'M04', 'F03'),
    ('FATIMA', 'PILAR', 'M08', 'F03'),
    ('LA LONJA', 'PILAR', 'M06', 'F03'),
    ('MANZANARES', 'PILAR', 'M08', 'F03'),
    ('MANZONE', 'PILAR', 'M08', 'F03'),
    ('ALBERTI', 'PILAR', 'M06', 'F03'),
    ('MANUEL ALBERTI', 'PILAR', 'M06', 'F03'),
    ('MAQUINISTA F. SAVIO (OESTE)', 'PILAR', 'M08', 'F03'),
    ('MAQUINISTA F SAVIO OESTE', 'PILAR', 'M09', 'F03'),
    ('MAQUINISTA SAVIO OESTE', 'PILAR', 'M09', 'F03'),
    ('PILAR', 'PILAR', 'M08', 'F03'),
    ('PRESIDENTE DERQUI', 'PILAR', 'M06', 'F03'),
    ('TORTUGUITAS', 'PILAR', 'M03', 'F03'),
    ('VILLA ASTOLFI', 'PILAR', 'M04', 'F03'),
    ('VILLA ROSA', 'PILAR', 'M08', 'F03'),
    ('ZELAYA', 'PILAR', 'M08', 'F03'),
    ('BERNAL', 'QUILMES', 'M13', 'F03'),
    ('BERNAL OESTE', 'QUILMES', 'M14', 'F03'),
    ('DON BOSCO', 'QUILMES', 'M13', 'F03'),
    ('EZPELETA', 'QUILMES', 'M14', 'F03'),
    ('EZPELETA OESTE', 'QUILMES', 'M14', 'F03'),
    ('QUILMES', 'QUILMES', 'M13', 'F03'),
    ('QUILMES OESTE', 'QUILMES', 'M14', 'F03'),
    ('SAN FRANCISCO SOLANO', 'QUILMES', 'M14', 'F03'),
    ('VILLA LA FLORIDA', 'QUILMES', 'M14', 'F03'),
    ('SAN FERNANDO', 'SAN FERNANDO', 'M07', 'F03'),
    ('VICTORIA', 'SAN FERNANDO', 'M07', 'F03'),
    ('VIRREYES', 'SAN FERNANDO', 'M05', 'F03'),
    ('ACASSUSO', 'SAN ISIDRO', 'M07', 'F03'),
    ('BECCAR', 'SAN ISIDRO', 'M07', 'F03'),
    ('BOULOGNE SUR MER', 'SAN ISIDRO', 'M05', 'F03'),
    ('MARTINEZ', 'SAN ISIDRO', 'M07', 'F03'),
    ('SAN ISIDRO', 'SAN ISIDRO', 'M07', 'F03'),
    ('VILLA ADELINA', 'SAN ISIDRO', 'M05', 'F03'),
    ('BELLA VISTA', 'SAN MIGUEL', 'M01', 'F01'),
    ('CAMPO DE MAYO', 'SAN MIGUEL', 'M01', 'F01'),
    ('MUNIZ', 'SAN MIGUEL', 'M01', 'F01'),
    ('SAN MIGUEL', 'SAN MIGUEL', 'M01', 'F01'),
    ('SAN MIGUEL OESTE', 'SAN MIGUEL', 'M01', 'F01'),
    ('BENAVIDEZ', 'TIGRE', 'M08', 'F02'),
    ('DIQUE LUJAN', 'TIGRE', 'M08', 'F02'),
    ('DON TORCUATO ESTE', 'TIGRE', 'M03', 'F02'),
    ('DON TORCUATO OESTE', 'TIGRE', 'M03', 'F02'),
    ('EL TALAR', 'TIGRE', 'M05', 'F02'),
    ('GENERAL PACHECO', 'TIGRE', 'M04', 'F02'),
    ('LOS TRONCOS DEL TALAR', 'TIGRE', 'M05', 'F02'),
    ('RICARDO ROJAS', 'TIGRE', 'M07', 'F02'),
    ('RINCON DE MILBERG', 'TIGRE', 'M07', 'F02'),
    ('TIGRE', 'TIGRE', 'M07', 'F02'),
    ('11 DE SEPTIEMBRE', 'TRES DE FEBRERO', 'MNN', 'F02'),
    ('CASEROS', 'TRES DE FEBRERO', 'M05', 'F02'),
    ('CHURRUCA', 'TRES DE FEBRERO', 'M03', 'F02'),
    ('CIUDAD JARDIN LOMAS DEL PALOMAR', 'TRES DE FEBRERO', 'M04', 'F02'),
    ('CIUDADELA', 'TRES DE FEBRERO', 'M07', 'F02'),
    ('EL LIBERTADOR', 'TRES DE FEBRERO', 'M05', 'F02'),
    ('JOSE INGENIEROS', 'TRES DE FEBRERO', 'M05', 'F02'),
    ('LOMA HERMOSA', 'TRES DE FEBRERO', 'M04', 'F02'),
    ('MARTIN CORONADO', 'TRES DE FEBRERO', 'M04', 'F02'),
    ('PABLO PODESTA', 'TRES DE FEBRERO', 'M04', 'F02'),
    ('SAENZ PENA', 'TRES DE FEBRERO', 'M05', 'F02'),
    ('SANTOS LUGARES', 'TRES DE FEBRERO', 'M05', 'F02'),
    ('VILLA BOSCH (EST. JUAN MARIA BOSCH)', 'TRES DE FEBRERO', 'M05', 'F02'),
    ('VILLA RAFFO', 'TRES DE FEBRERO', 'M05', 'F03'),
    ('CARAPACHAY', 'VICENTE LOPEZ', 'M05', 'F03'),
    ('FLORIDA', 'VICENTE LOPEZ', 'M07', 'F03'),
    ('FLORIDA OESTE', 'VICENTE LOPEZ', 'M05', 'F03'),
    ('LA LUCILA', 'VICENTE LOPEZ', 'M07', 'F03'),
    ('MUNRO', 'VICENTE LOPEZ', 'M05', 'F03'),
    ('OLIVOS', 'VICENTE LOPEZ', 'M07', 'F03'),
    ('VICENTE LOPEZ', 'VICENTE LOPEZ', 'M07', 'F03'),
    ('VILLA ADELINA', 'VICENTE LOPEZ', 'M05', 'F03'),
    ('VILLA MARTELLI', 'VICENTE LOPEZ', 'M07', 'F03'),
]


def create_mensajerias():
    DeliveryCode.objects.bulk_create(
        [DeliveryCode(**q) for q in mensajerias]
    )
    return True


def create_flexes():
    FlexCode.objects.bulk_create(
        [FlexCode(**q) for q in flexs]
    )
    return True


def create_zones():
    Zone.objects.bulk_create(
        [Zone(name="Norte"), Zone(name="Sur"), ]
    )
    return True


def create_partidos():
    Partido.objects.bulk_create([
        Partido(name=partido, is_amba=True) for partido in partidos
    ])
    return True


def create_localidades():
    Town.objects.bulk_create(
        [Town(**q)for q in map(map_localidades, localidades)]
    )
    return True


def map_localidades(localidad):
    nombre, municipio, id_mensajeria, id_flex = localidad
    print(nombre, municipio, id_mensajeria, id_flex)
    result = {
        'name': nombre,
        'partido': Partido.objects.get(name=municipio),
    }
    try:
        result['delivery_code'] = DeliveryCode.objects.get(code=id_mensajeria)
        result['flex_code'] = FlexCode.objects.get(code=id_flex)
    except DeliveryCode.DoesNotExist:
        print(f"DeliveryCode matching query '{id_mensajeria}' does not exist.")
    except FlexCode.DoesNotExist:
        print(f"FlexCode matching query '{id_mensajeria}' does not exist.")
    return result


def create_user_groups():
    # TODO CREATE GROUPS
    pass


def codigos_postales():
    # Opening JSON file
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    errors_file_path = f"{BASE_DIR}\\postal_codes_bulk_result.csv"
    with open(errors_file_path, 'a') as csv:
        line = 'status,code,town\n'
    with open(BASE_DIR+'\\postal_codes.json') as file:
        # returns JSON object as a dictionary
        data = json.load(file)

        # Iterating through the json
        # list
        for obj in data['codes']:
            code = obj['code']
            town_name = obj['town']
            print("code", code, "town_name", town_name)
            zipcodes = ZipCode.objects.filter(code=code)
            print("zipcodes", zipcodes)
            if not zipcodes:
                zipcode = ZipCode(code=code)
                zipcode.save()
            else:
                zipcode = zipcodes[0]
            towns = Town.objects.filter(name=town_name.upper())
            towns = towns if towns else Town.objects.filter(
                name__contains=town_name.upper())
            if towns:
                for town in towns:
                    zipcode.towns.add(town)
                    with open(errors_file_path, 'a') as csv:
                        line = f'success,{code},\
                            "intended={town_name}{towns}"\n'
                        csv.write(line)
            else:
                with open(errors_file_path, 'a') as csv:
                    line = f'error,{code},{town_name}\n'
                    csv.write(line)
            del towns


def main():
    create_mensajerias()
    create_flexes()
    create_zones()
    create_partidos()
    create_localidades()
    return True
