# Guía Rápida - Primeros Pasos

## ¡Bienvenido! 👋

Esta guía te ayudará a ejecutar `extract_genes.py` paso a paso.

---

## 1. Requisitos

- Python 3.6 o superior
- (Opcional) pytest para ejecutar pruebas

---

## 2. Verificar Python

```bash
python --version
# o
python3 --version
```

Deberías ver Python 3.6+

---

## 3. Ubicarse en la carpeta del proyecto

```bash
cd /Users/monicareyesramirez/Documents/Documents/Bioinfo1/Data/Proyecto_Final
```

---

## 4. Ejemplo 1: Ejecución Básica

Se incluyen archivos de ejemplo en `data/`:

```bash
python codigo/extract_genes.py \
  --gff data/example_genes.gff \
  --fasta data/example_genome.fasta \
  --output results/example_output.fna
```

**Resultado esperado:**
```
Loading FASTA from data/example_genome.fasta...
✓ Loaded 2 sequences
Parsing GFF from data/example_genes.gff...
✓ Found 3 genes
Extracting gene sequences...
✓ Extracted 3 genes
✓ Saved to results/example_output.fna

✓ Program completed successfully!
```

Verifica el resultado:
```bash
cat results/example_output.fna
```

---

## 5. Ejemplo 2: Con Filtro de Longitud

Solo genes con longitud ≥ 10 bp:

```bash
python codigo/extract_genes.py \
  --gff data/example_genes.gff \
  --fasta data/example_genome.fasta \
  --output results/example_output_filtered.fna \
  --min-length 10
```

---

## 6. Ejecutar las Pruebas

### Instalar pytest (si no lo tienes)
```bash
pip install pytest
```

### Ejecutar todas las pruebas
```bash
pytest tests/test_extract_genes.py -v
```

### Ejecutar pruebas de una función específica
```bash
pytest tests/test_extract_genes.py::TestLoadFasta -v
```

---

## 7. Estructura de Carpetas

```
Proyecto_Final/
├── codigo/
│   └── extract_genes.py          ← PROGRAMA PRINCIPAL
├── data/
│   ├── example_genome.fasta      ← Archivo de entrada ejemplo
│   └── example_genes.gff         ← Archivo de entrada ejemplo
├── results/
│   └── (aquí se guardan los outputs)
├── tests/
│   └── test_extract_genes.py     ← Pruebas unitarias
├── docs/
│   ├── extract_genes_documentation.md
│   ├── test_documentation.md
│   └── ejercicio1_extract_genes.md
└── README.md
```

---

## 8. Usar tus propios archivos

Si quieres usar tus propios archivos FASTA y GFF:

```bash
python codigo/extract_genes.py \
  --gff data/tu_archivo.gff \
  --fasta data/tu_genoma.fasta \
  --output results/tu_salida.fna
```

---

## 9. Formato de Archivos

### FASTA (genoma)
```
>chromosome_name
ATGCGTACGATCGATCGATCGA
TCGATCGATCGATCGATCGAT
>another_chromosome
GCTAGCTAGCTAGCTAGCTAG
```

### GFF (anotaciones)
```
chr1	RefSeq	gene	100	500	.	+	.	ID=gene1;Name=araC
chr1	RefSeq	gene	600	800	.	-	.	ID=gene2;Name=crp
```

---

## 10. Ayuda y Opciones

```bash
python codigo/extract_genes.py --help
```

Verás:
```
usage: extract_genes.py [-h] --gff GFF --fasta FASTA --output OUTPUT
                        [--min-length MIN_LENGTH]

Extract gene sequences from a genome (FASTA) using gene annotations (GFF)

optional arguments:
  -h, --help            show this help message and exit
  --gff GFF             Path to the GFF file
  --fasta FASTA         Path to the FASTA genome file
  --output OUTPUT       Path to the output FASTA file
  --min-length MIN_LENGTH
                        Minimum gene length to include (optional)
```

---

## 11. Solucionar Problemas

### Error: "FASTA file not found"
- Verifica que la ruta del archivo es correcta
- Prueba con ruta absoluta: `/path/to/file.fasta`

### Error: "GFF file contains no genes"
- El archivo GFF no tiene features de tipo "gene"
- Verifica que la columna 3 tenga "gene"

### Error: "Gene coordinates out of bounds"
- Las coordenadas en el GFF superan la longitud del genoma
- Verifica que start ≤ end y que ambas están en rango

### Error: "Invalid DNA character"
- El FASTA tiene caracteres no válidos (A, T, G, C, N)
- Revisa y limpia el archivo FASTA

---

## 12. Ver Archivos de Salida

```bash
# Ver las primeras líneas del resultado
head -20 results/example_output.fna

# Contar cuántos genes se extrajeron
grep "^>" results/example_output.fna | wc -l

# Ver archivo completo
cat results/example_output.fna
```

---

## 13. Próximos Pasos

1. Lee la documentación completa: `docs/extract_genes_documentation.md`
2. Revisa los casos de prueba: `docs/test_documentation.md`
3. Analiza el código: `codigo/extract_genes.py`
4. Prueba con tus propios datos

---

## 14. Ayuda Adicional

- **Documentación técnica**: `docs/extract_genes_documentation.md`
- **Pruebas**: `docs/test_documentation.md`
- **Requisitos del ejercicio**: `docs/ejercicio1_extract_genes.md`
- **README general**: `README.md`

---

**¡Listo para comenzar! 🚀**

Si tienes problemas, revisa los documentos o ejecuta las pruebas para ver ejemplos funcionando.
