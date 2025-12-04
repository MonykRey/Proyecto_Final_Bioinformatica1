# Extract Genes - Proyecto Final Bioinformática 1

## Descripción Rápida

Programa para extraer secuencias de genes desde un archivo FASTA basado en anotaciones GFF.

## Archivos del Proyecto

```
├── codigo/
│   └── extract_genes.py          ← PROGRAMA PRINCIPAL
├── tests/
│   └── test_extract_genes.py     ← PRUEBAS UNITARIAS
├── docs/
│   ├── extract_genes_documentation.md  ← DOCUMENTACIÓN COMPLETA
│   └── ejercicio1_extract_genes.md     ← REQUISITOS DEL EJERCICIO
├── data/                          ← ARCHIVOS DE ENTRADA
├── results/                       ← ARCHIVOS DE SALIDA
└── README.md                      ← ESTE ARCHIVO
```

## Uso Rápido

### Instalación
No requiere instalación. Solo necesitas Python 3.6+.

### Ejecutar el programa
```bash
python codigo/extract_genes.py --gff data/genes.gff --fasta data/genome.fasta --output results/genes.fna
```

### Con filtro de longitud
```bash
python codigo/extract_genes.py --gff data/genes.gff --fasta data/genome.fasta --output results/genes.fna --min-length 300
```

## Opciones

| Opción | Descripción |
|--------|-------------|
| `--gff` | Archivo GFF con anotaciones |
| `--fasta` | Archivo FASTA con genoma |
| `--output` | Archivo FASTA de salida |
| `--min-length` | Longitud mínima (opcional) |

## Ejecutar Pruebas

```bash
# Todas las pruebas
pytest tests/test_extract_genes.py -v

# Pruebas específicas
pytest tests/test_extract_genes.py::TestLoadFasta -v
```

## Funciones Implementadas

✅ `load_fasta()` - Carga archivo FASTA
✅ `parse_gff()` - Parsea archivo GFF
✅ `reverse_complement()` - Complemento inverso
✅ `extract_gene_seqs()` - Extrae secuencias
✅ `main()` - Interfaz CLI con argparse

## Características

- Validación robusta de archivos
- Manejo completo de errores
- Soporte para strand inverso
- Filtro por longitud mínima
- Suite de pruebas completa (30+ casos)
- Documentación exhaustiva
- PEP8 compliant
- Docstrings en todas las funciones

## Documentación Completa

Ver: `docs/extract_genes_documentation.md`

## Requisitos Técnicos (Cumplidos ✓)

- [x] `argparse` obligatorio
- [x] Funciones: `load_fasta()`, `parse_gff()`, `extract_gene_seqs()`
- [x] Manejo de errores con excepciones
- [x] Docstrings y PEP8
- [x] Pruebas con pytest
- [x] Reverse complement para strand negativo
- [x] Filtro --min-length

## Archivos Generados

- `codigo/extract_genes.py` - Programa principal (400+ líneas)
- `tests/test_extract_genes.py` - Suite de pruebas (300+ líneas, 30+ casos)
- `docs/extract_genes_documentation.md` - Documentación completa

## Ejemplo de Uso

### Entrada: genome.fasta
```
>chr1
ATGCGTACGATCGATCGATCGATCGATCGATAA
```

### Entrada: genes.gff
```
chr1	RefSeq	gene	1	10	.	+	.	ID=gene1;Name=araC
chr1	RefSeq	gene	15	25	.	-	.	ID=gene2;Name=crp
```

### Comando
```bash
python codigo/extract_genes.py --gff genes.gff --fasta genome.fasta --output genes.fna
```

### Salida: genes.fna
```
>araC gene_coords=1-10 strand=+
ATGCGTACGA
>crp gene_coords=15-25 strand=-
GATCGATCGA
```

---

**Versión 1.0** | Diciembre 2025
