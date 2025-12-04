# Documentación de extract_genes.py

## Descripción General

`extract_genes.py` es un programa en Python que extrae secuencias de genes desde un archivo FASTA basado en anotaciones genómicas en formato GFF. El programa es modular, robusto y sigue las mejores prácticas de desarrollo en Python.

---

## Características

✅ **Carga de genomas FASTA**: Lee y valida archivos FASTA con múltiples secuencias
✅ **Parseo de anotaciones GFF**: Extrae features de tipo `gene` del archivo GFF
✅ **Extracción de secuencias**: Obtiene las subsecuencias de genes del genoma
✅ **Manejo de strand inverso**: Aplica complemento inverso para genes en strand `-`
✅ **Filtro por longitud**: Opción para filtrar genes por longitud mínima
✅ **Manejo robusto de errores**: Valida archivos y coordenadas
✅ **Interfaz CLI completa**: Usa `argparse` para argumentos de línea de comandos
✅ **Pruebas completas**: Incluye suite de tests con pytest

---

## Requisitos

- Python 3.6+
- pytest (para ejecutar pruebas)

---

## Instalación

No requiere instalación especial. Solo asegúrate de tener Python 3.6+ instalado.

Para instalar pytest (opcional, solo para pruebas):
```bash
pip install pytest
```

---

## Uso

### Sintaxis Básica

```bash
python extract_genes.py --gff <archivo_gff> --fasta <archivo_fasta> --output <archivo_salida>
```

### Opciones

| Opción | Descripción | Obligatorio |
|--------|-------------|-------------|
| `--gff` | Ruta al archivo GFF | ✓ Sí |
| `--fasta` | Ruta al archivo FASTA con el genoma | ✓ Sí |
| `--output` | Ruta al archivo FASTA de salida | ✓ Sí |
| `--min-length` | Longitud mínima de genes (en bp) | ✗ No |

### Ejemplos

#### 1. Extracción básica

```bash
python extract_genes.py --gff genes.gff --fasta genome.fasta --output genes.fna
```

#### 2. Con filtro de longitud mínima

```bash
python extract_genes.py --gff genes.gff --fasta genome.fasta --output genes.fna --min-length 300
```

Solo se exportarán genes con longitud ≥ 300 bp.

#### 3. Con rutas relativas/absolutas

```bash
python extract_genes.py \
  --gff data/annotations.gff \
  --fasta data/genome.fasta \
  --output results/extracted_genes.fna \
  --min-length 500
```

---

## Formatos de Entrada

### Archivo FASTA (genoma)

```
>chromosome1
ATGCGTACGATCGATCGATCGATCGATCGATCGATCGATCGATCGATCGA
>chromosome2
GCTAGCTAGCTAGCTAGCTAGCTAGCTAGCTAGCTAGCTAGCTAGCTAG
```

**Requisitos:**
- Encabezados comienzan con `>`
- Una secuencia por línea (o múltiples líneas)
- Solo caracteres válidos: A, T, G, C, N (mayúsculas o minúsculas)

### Archivo GFF (anotaciones)

```
chr1	RefSeq	gene	3456	41020	.	+	.	ID=gene1;Name=araC
chr1	RefSeq	gene	51000	61000	.	-	.	ID=gene2;Name=crp
```

**Requisitos:**
- 9 columnas separadas por tabulaciones
- Columna 3: tipo de feature (solo procesamos `gene`)
- Columnas 4-5: coordenadas (1-indexed, inclusivas)
- Columna 7: strand (`+` o `-`)
- Columna 9: atributos en formato `key=value;...`
- Debe contener `Name=` o `ID=` para identificar el gen

---

## Formato de Salida

### Archivo FASTA (genes extraídos)

```
>araC gene_coords=3456-41020 strand=+
ATGCGTAGCTAGCTAGCTAGCTAAATGCGTAGCTAGCTAGCTAGCTAA
>crp gene_coords=51000-61000 strand=-
TTACGCTAGCTAGCTAGCTAGCTAGCTAGCTAGCTAGCTAGCTAGCTA
```

**Formato del encabezado:**
```
>{nombre_del_gen} gene_coords={inicio}-{fin} strand={+/-}
```

---

## Funciones Principales

### 1. `load_fasta(fasta_path)`

Carga un archivo FASTA y retorna un diccionario con las secuencias.

```python
def load_fasta(fasta_path):
    """
    Carga un archivo FASTA y retorna un diccionario con las secuencias.
    
    Args:
        fasta_path (str): Ruta al archivo FASTA.
    
    Returns:
        dict: Diccionario con formato {seq_id: sequence_str}.
    
    Raises:
        FileNotFoundError: Si el archivo no existe.
        ValueError: Si el archivo está vacío o tiene formato incorrecto.
    """
```

**Ejemplo:**
```python
genome = load_fasta('genome.fasta')
# Resultado: {'chr1': 'ATGCGTACGA...', 'chr2': 'GCTAGCTAGC...'}
```

---

### 2. `parse_gff(gff_path)`

Parsea un archivo GFF y extrae únicamente features de tipo `gene`.

```python
def parse_gff(gff_path):
    """
    Parsea un archivo GFF y extrae únicamente features de tipo 'gene'.
    
    Args:
        gff_path (str): Ruta al archivo GFF.
    
    Returns:
        list: Lista de diccionarios con información de genes.
    
    Raises:
        FileNotFoundError: Si el archivo no existe.
        ValueError: Si el archivo tiene formato incorrecto.
    """
```

**Ejemplo:**
```python
genes = parse_gff('genes.gff')
# Resultado:
# [
#   {'seqid': 'chr1', 'start': 3456, 'end': 41020, 'strand': '+', 'name': 'araC'},
#   {'seqid': 'chr1', 'start': 51000, 'end': 61000, 'strand': '-', 'name': 'crp'}
# ]
```

---

### 3. `reverse_complement(seq)`

Calcula el complemento inverso de una secuencia de DNA.

```python
def reverse_complement(seq):
    """
    Calcula el complemento inverso de una secuencia de DNA.
    
    Args:
        seq (str): Secuencia de DNA.
    
    Returns:
        str: Complemento inverso de la secuencia.
    """
```

**Ejemplo:**
```python
rev_comp = reverse_complement('ATGC')
# Resultado: 'GCAT'
```

---

### 4. `extract_gene_seqs(genome, genes, min_length=None)`

Extrae las secuencias de genes desde el genoma.

```python
def extract_gene_seqs(genome, genes, min_length=None):
    """
    Extrae las secuencias de genes desde el genoma.
    
    Args:
        genome (dict): Diccionario con secuencias del genoma.
        genes (list): Lista de diccionarios con información de genes.
        min_length (int, optional): Longitud mínima de genes a incluir.
    
    Returns:
        list: Lista de tuplas (header, sequence) para cada gen.
    
    Raises:
        ValueError: Si las coordenadas están fuera de rango.
    """
```

**Ejemplo:**
```python
result = extract_gene_seqs(genome, genes, min_length=300)
# Resultado:
# [
#   ('>araC gene_coords=3456-41020 strand=+', 'ATGCGTAGC...'),
#   ('>crp gene_coords=51000-61000 strand=-', 'TTACGCTAG...')
# ]
```

---

## Manejo de Errores

El programa incluye validaciones exhaustivas:

### Errores en Archivos
- ❌ Archivo no encontrado → `FileNotFoundError`
- ❌ Archivo vacío → `ValueError`
- ❌ Formato incorrecto → `ValueError`

### Errores en Secuencias FASTA
- ❌ Caracteres inválidos (no A, T, G, C, N) → `ValueError`
- ❌ Secuencias vacías → `ValueError`

### Errores en Anotaciones GFF
- ❌ Menos de 9 columnas → `ValueError`
- ❌ Coordenadas inválidas → `ValueError`
- ❌ start > end → `ValueError`
- ❌ Strand inválido (no + o -) → `ValueError`
- ❌ Sin Name o ID → `ValueError`

### Errores en Extracción
- ❌ seqid no existe en FASTA → `ValueError`
- ❌ Coordenadas fuera de rango → `ValueError`
- ❌ min_length negativo → `ValueError`

---

## Pruebas

### Ejecutar todas las pruebas

```bash
pytest tests/test_extract_genes.py -v
```

### Ejecutar pruebas específicas

```bash
# Pruebas de load_fasta
pytest tests/test_extract_genes.py::TestLoadFasta -v

# Pruebas de parse_gff
pytest tests/test_extract_genes.py::TestParseGFF -v

# Pruebas de reverse_complement
pytest tests/test_extract_genes.py::TestReverseComplement -v

# Pruebas de extract_gene_seqs
pytest tests/test_extract_genes.py::TestExtractGeneSeqs -v

# Pruebas de integración
pytest tests/test_extract_genes.py::TestIntegration -v
```

### Cobertura de Pruebas

Se incluyen más de 30 casos de prueba que cubren:

✅ Carga correcta de FASTA
✅ Archivos FASTA vacíos e inválidos
✅ Caracteres inválidos en DNA
✅ Case-insensitivity en FASTA
✅ Parseo correcto de GFF
✅ Filtrado de features no-gene
✅ Validación de coordenadas
✅ Validación de strand
✅ Detección de genes sin nombre
✅ Reverse complement correcto
✅ Extracción correcta de genes
✅ Filtro de longitud mínima
✅ Validación de seqids
✅ Coordinadas fuera de rango
✅ Flujo completo de integración

---

## Ejemplo de Uso Completo

### Paso 1: Preparar datos

**genome.fasta:**
```
>chr1
ATGCGTACGATCGATCGATCGATCGATCGATAA
```

**genes.gff:**
```
chr1	RefSeq	gene	1	10	.	+	.	ID=gene1;Name=araC
chr1	RefSeq	gene	15	25	.	-	.	ID=gene2;Name=crp
```

### Paso 2: Ejecutar el programa

```bash
python extract_genes.py \
  --gff genes.gff \
  --fasta genome.fasta \
  --output genes.fna
```

### Paso 3: Resultado (genes.fna)

```
>araC gene_coords=1-10 strand=+
ATGCGTACGA
>crp gene_coords=15-25 strand=-
GATCGATCGA
```

---

## Notas Técnicas

### Indexación de Coordenadas

- **GFF usa indexación 1-based**: La primera posición es 1
- **Python usa indexación 0-based**: La primera posición es 0
- **El programa convierte automáticamente** entre ambas

### Strand y Reverse Complement

- **Strand `+`**: Se extrae la secuencia directamente
- **Strand `-`**: Se extrae el complemento inverso
  - A ↔ T
  - G ↔ C
  - Luego se invierte la secuencia

### Espacios en Blanco

- Las líneas vacías se ignoran
- Los espacios al inicio/final se eliminan
- Los tabuladores son obligatorios en GFF

---

## Mejores Prácticas

1. **Validar entradas**: Siempre revisa que los archivos estén bien formados
2. **Usar ruta de salida clara**: Especifica un directorio existente o el programa lo creará
3. **Guardar logs**: Redirige la salida para revisar qué pasó:
   ```bash
   python extract_genes.py ... 2>&1 | tee output.log
   ```
4. **Probar con min-length**: Valida que funciona el filtro correctamente
5. **Revisar archivo de salida**: Verifica que el FASTA de salida tiene formato válido

---

## Licencia

Este programa está disponible para uso educativo y de investigación.

---

## Autor

Creado como parte del ejercicio 1 de Bioinformática 1.

---

## Cambios y Versión

**Versión**: 1.0
**Fecha**: Diciembre 2025
**Estado**: Completo y probado

---

## Preguntas Frecuentes

### ¿Qué pasa si el gen está fuera de los límites del genoma?

El programa lanzará un error: `ValueError: Gene coordinates out of bounds`

### ¿Puedo tener múltiples genomas?

Sí, puedes tener múltiples secuencias en un solo FASTA. El programa las procesará todas.

### ¿Qué pasa con los genes que se solapan?

Se extraen ambos normalmente. El programa no resuelve solapamientos.

### ¿Puedo usar --min-length 0?

No es recomendable, pero técnicamente funcionaría y extraería todos los genes.

### ¿Cómo sé si algo salió mal?

Mira los mensajes de error. El programa es verboso y te dice exactamente qué ocurrió.

---

**Fin de la documentación**
