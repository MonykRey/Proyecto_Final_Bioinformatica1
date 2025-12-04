#!/usr/bin/env python3
"""
extract_genes.py

Este programa extrae secuencias de genes desde un archivo FASTA basado en
anotaciones GFF. Las secuencias se guardan en un archivo FASTA de salida.

Uso:
    python extract_genes.py --gff genes.gff --fasta genome.fasta --output genes.fna
    python extract_genes.py --gff genes.gff --fasta genome.fasta --output genes.fna --min-length 300
"""

import argparse
from pathlib import Path


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
    fasta_path = Path(fasta_path)
    
    if not fasta_path.exists():
        raise FileNotFoundError(f"FASTA file not found: {fasta_path}")
    
    genome = {}
    current_seq_id = None
    current_sequence = []
    
    try:
        with open(fasta_path, 'r') as f:
            for line in f:
                line = line.strip()
                
                if not line:  # Saltar líneas vacías
                    continue
                
                if line.startswith('>'):
                    # Guardar la secuencia anterior si existe
                    if current_seq_id is not None:
                        sequence = ''.join(current_sequence).upper()
                        if not sequence:
                            raise ValueError(f"Empty sequence for {current_seq_id}")
                        genome[current_seq_id] = sequence
                    
                    # Iniciar nueva secuencia
                    current_seq_id = line[1:].split()[0]  # Tomar solo el ID
                    current_sequence = []
                else:
                    # Validar caracteres de DNA
                    if not all(c in 'ATGCNatgcn' for c in line):
                        raise ValueError(f"Invalid DNA character in sequence: {line}")
                    current_sequence.append(line.upper())
        
        # Guardar la última secuencia
        if current_seq_id is not None:
            sequence = ''.join(current_sequence).upper()
            if not sequence:
                raise ValueError(f"Empty sequence for {current_seq_id}")
            genome[current_seq_id] = sequence
    
    except IOError as e:
        raise ValueError(f"Error reading FASTA file: {e}")
    
    if not genome:
        raise ValueError("FASTA file is empty or has no valid sequences")
    
    return genome


def parse_gff(gff_path):
    """
    Parsea un archivo GFF y extrae únicamente features de tipo 'gene'.
    
    Args:
        gff_path (str): Ruta al archivo GFF.
    
    Returns:
        list: Lista de diccionarios con información de genes:
              {'seqid': str, 'start': int, 'end': int, 'strand': str, 'name': str}
    
    Raises:
        FileNotFoundError: Si el archivo no existe.
        ValueError: Si el archivo está vacío o tiene formato incorrecto.
    """
    gff_path = Path(gff_path)
    
    if not gff_path.exists():
        raise FileNotFoundError(f"GFF file not found: {gff_path}")
    
    genes = []
    
    try:
        with open(gff_path, 'r') as f:
            for line_num, line in enumerate(f, 1):
                line = line.strip()
                
                # Saltar líneas vacías y comentarios
                if not line or line.startswith('#'):
                    continue
                
                fields = line.split('\t')
                
                # Validar que la línea tiene al menos 9 columnas
                if len(fields) < 9:
                    raise ValueError(
                        f"GFF line {line_num} has less than 9 fields: {line}"
                    )
                
                seqid = fields[0]
                feature_type = fields[2]
                start = fields[3]
                end = fields[4]
                strand = fields[6]
                attributes = fields[8]
                
                # Procesar solo features de tipo 'gene'
                if feature_type != 'gene':
                    continue
                
                # Validar coordenadas
                try:
                    start_int = int(start)
                    end_int = int(end)
                except ValueError:
                    raise ValueError(
                        f"GFF line {line_num} has invalid coordinates: "
                        f"start={start}, end={end}"
                    )
                
                if start_int > end_int:
                    raise ValueError(
                        f"GFF line {line_num}: start ({start_int}) > end ({end_int})"
                    )
                
                # Validar strand
                if strand not in ['+', '-']:
                    raise ValueError(
                        f"GFF line {line_num}: invalid strand '{strand}'. "
                        f"Must be '+' or '-'"
                    )
                
                # Extraer nombre del gen
                name = None
                for attr in attributes.split(';'):
                    attr = attr.strip()
                    if attr.startswith('Name='):
                        name = attr[5:]
                        break
                    elif attr.startswith('ID='):
                        name = attr[3:]
                
                if name is None:
                    raise ValueError(
                        f"GFF line {line_num}: gene has no Name or ID attribute"
                    )
                
                genes.append({
                    'seqid': seqid,
                    'start': start_int,
                    'end': end_int,
                    'strand': strand,
                    'name': name
                })
    
    except IOError as e:
        raise ValueError(f"Error reading GFF file: {e}")
    
    if not genes:
        raise ValueError("GFF file contains no genes")
    
    return genes


def reverse_complement(seq):
    """
    Calcula el complemento inverso de una secuencia de DNA.
    
    Args:
        seq (str): Secuencia de DNA.
    
    Returns:
        str: Complemento inverso de la secuencia.
    """
    complement_map = {'A': 'T', 'T': 'A', 'G': 'C', 'C': 'G', 'N': 'N'}
    return ''.join(complement_map[base] for base in reversed(seq))


def extract_gene_seqs(genome, genes, min_length=None):
    """
    Extrae las secuencias de genes desde el genoma.
    
    Args:
        genome (dict): Diccionario con secuencias del genoma.
        genes (list): Lista de diccionarios con información de genes.
        min_length (int, optional): Longitud mínima de genes a incluir. Defaults to None.
    
    Returns:
        list: Lista de tuplas (header, sequence) para cada gen.
    
    Raises:
        ValueError: Si las coordenadas están fuera de rango o si min_length es inválido.
    """
    if min_length is not None:
        if not isinstance(min_length, int) or min_length < 0:
            raise ValueError("--min-length must be a positive integer")
    
    extracted = []
    
    for gene in genes:
        seqid = gene['seqid']
        start = gene['start'] - 1  # GFF es 1-indexed, Python es 0-indexed
        end = gene['end']
        strand = gene['strand']
        name = gene['name']
        
        # Validar que el seqid existe en el genoma
        if seqid not in genome:
            raise ValueError(
                f"Sequence '{seqid}' from GFF not found in FASTA. "
                f"Available sequences: {', '.join(genome.keys())}"
            )
        
        genome_seq = genome[seqid]
        
        # Validar que las coordenadas están dentro del rango
        if start < 0 or end > len(genome_seq):
            raise ValueError(
                f"Gene '{name}' coordinates ({start+1}-{end}) are out of bounds "
                f"for sequence '{seqid}' (length: {len(genome_seq)})"
            )
        
        # Extraer la secuencia
        gene_seq = genome_seq[start:end]
        
        # Aplicar reverse complement si es necesario
        if strand == '-':
            gene_seq = reverse_complement(gene_seq)
        
        # Aplicar filtro de longitud mínima
        if min_length is not None and len(gene_seq) < min_length:
            continue
        
        # Crear encabezado FASTA
        header = f">{name} gene_coords={start+1}-{end} strand={strand}"
        
        extracted.append((header, gene_seq))
    
    if not extracted:
        raise ValueError("No genes extracted. Check --min-length or GFF/FASTA files.")
    
    return extracted


def main():
    """
    Función principal que orquesta todo el flujo del programa.
    """
    parser = argparse.ArgumentParser(
        description="Extract gene sequences from a genome (FASTA) using gene "
                    "annotations (GFF)",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    python extract_genes.py --gff genes.gff --fasta genome.fasta --output genes.fna
    python extract_genes.py --gff genes.gff --fasta genome.fasta --output genes.fna --min-length 300
        """
    )
    
    parser.add_argument(
        '--gff',
        required=True,
        help='Path to the GFF file'
    )
    parser.add_argument(
        '--fasta',
        required=True,
        help='Path to the FASTA genome file'
    )
    parser.add_argument(
        '--output',
        required=True,
        help='Path to the output FASTA file'
    )
    parser.add_argument(
        '--min-length',
        type=int,
        default=None,
        help='Minimum gene length to include (optional)'
    )
    
    args = parser.parse_args()
    
    try:
        print(f"Loading FASTA from {args.fasta}...")
        genome = load_fasta(args.fasta)
        print(f"✓ Loaded {len(genome)} sequences")
        
        print(f"Parsing GFF from {args.gff}...")
        genes = parse_gff(args.gff)
        print(f"✓ Found {len(genes)} genes")
        
        print("Extracting gene sequences...")
        extracted = extract_gene_seqs(genome, genes, args.min_length)
        print(f"✓ Extracted {len(extracted)} genes")
        
        # Escribir archivo de salida
        output_path = Path(args.output)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_path, 'w') as f:
            for header, seq in extracted:
                f.write(f"{header}\n{seq}\n")
        
        print(f"✓ Saved to {output_path}")
        print("\n✓ Program completed successfully!")
    
    except FileNotFoundError as e:
        print(f"❌ Error: {e}")
        exit(1)
    except ValueError as e:
        print(f"❌ Error: {e}")
        exit(1)
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        exit(1)


if __name__ == '__main__':
    main()
