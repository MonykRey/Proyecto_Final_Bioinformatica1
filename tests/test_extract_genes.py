"""
test_extract_genes.py

Archivo de pruebas para extract_genes.py usando pytest.
Verifica que todas las funciones principales funcionan correctamente.
"""

import pytest
import tempfile
from pathlib import Path
import sys

# Agregar la carpeta codigo al path para importar el módulo
sys.path.insert(0, str(Path(__file__).parent.parent / 'codigo'))

from extract_genes import (
    load_fasta,
    parse_gff,
    reverse_complement,
    extract_gene_seqs
)


class TestLoadFasta:
    """Pruebas para la función load_fasta()"""
    
    def test_load_fasta_valid(self):
        """Test: Cargar un FASTA válido"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.fasta', delete=False) as f:
            f.write(">chr1\n")
            f.write("ATGCGTACGA\n")
            f.write("TCGATCGATC\n")
            f.write(">chr2\n")
            f.write("GCTAGCTAGC\n")
            f.name_temp = f.name
        
        try:
            result = load_fasta(f.name_temp)
            assert len(result) == 2
            assert 'chr1' in result
            assert 'chr2' in result
            assert result['chr1'] == 'ATGCGTACGATCGATCGATC'
            assert result['chr2'] == 'GCTAGCTAGC'
        finally:
            Path(f.name_temp).unlink()
    
    def test_load_fasta_empty_file(self):
        """Test: Archivo FASTA vacío debe lanzar ValueError"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.fasta', delete=False) as f:
            f.name_temp = f.name
        
        try:
            with pytest.raises(ValueError, match="empty or has no valid"):
                load_fasta(f.name_temp)
        finally:
            Path(f.name_temp).unlink()
    
    def test_load_fasta_file_not_found(self):
        """Test: Archivo no existente debe lanzar FileNotFoundError"""
        with pytest.raises(FileNotFoundError):
            load_fasta('/nonexistent/file.fasta')
    
    def test_load_fasta_invalid_characters(self):
        """Test: Caracteres inválidos en FASTA deben lanzar ValueError"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.fasta', delete=False) as f:
            f.write(">chr1\n")
            f.write("ATGC123XYZ\n")
            f.name_temp = f.name
        
        try:
            with pytest.raises(ValueError, match="Invalid DNA character"):
                load_fasta(f.name_temp)
        finally:
            Path(f.name_temp).unlink()
    
    def test_load_fasta_case_insensitive(self):
        """Test: FASTA debe ser case-insensitive"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.fasta', delete=False) as f:
            f.write(">chr1\n")
            f.write("AtGc\n")
            f.write("gAtC\n")
            f.name_temp = f.name
        
        try:
            result = load_fasta(f.name_temp)
            assert result['chr1'] == 'ATGCGATC'
        finally:
            Path(f.name_temp).unlink()


class TestParseGFF:
    """Pruebas para la función parse_gff()"""
    
    def test_parse_gff_valid(self):
        """Test: Parsear un GFF válido"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.gff', delete=False) as f:
            f.write("# comentario\n")
            f.write("chr1\tRefSeq\tgene\t100\t500\t.\t+\t.\tID=gene1;Name=araC\n")
            f.write("chr1\tRefSeq\tgene\t600\t900\t.\t-\t.\tID=gene2;Name=crp\n")
            f.write("chr1\tRefSeq\tCDS\t100\t150\t.\t+\t.\tID=cds1\n")  # Ignorar CDS
            f.name_temp = f.name
        
        try:
            result = parse_gff(f.name_temp)
            assert len(result) == 2
            assert result[0]['name'] == 'araC'
            assert result[0]['start'] == 100
            assert result[0]['end'] == 500
            assert result[0]['strand'] == '+'
            assert result[1]['name'] == 'crp'
            assert result[1]['strand'] == '-'
        finally:
            Path(f.name_temp).unlink()
    
    def test_parse_gff_file_not_found(self):
        """Test: Archivo GFF no existente debe lanzar FileNotFoundError"""
        with pytest.raises(FileNotFoundError):
            parse_gff('/nonexistent/file.gff')
    
    def test_parse_gff_invalid_columns(self):
        """Test: GFF con menos de 9 columnas debe lanzar ValueError"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.gff', delete=False) as f:
            f.write("chr1\tRefSeq\tgene\t100\t500\n")  # Solo 5 columnas
            f.name_temp = f.name
        
        try:
            with pytest.raises(ValueError, match="less than 9 fields"):
                parse_gff(f.name_temp)
        finally:
            Path(f.name_temp).unlink()
    
    def test_parse_gff_invalid_coordinates(self):
        """Test: GFF con coordenadas inválidas debe lanzar ValueError"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.gff', delete=False) as f:
            f.write("chr1\tRefSeq\tgene\tabc\t500\t.\t+\t.\tID=gene1;Name=test\n")
            f.name_temp = f.name
        
        try:
            with pytest.raises(ValueError, match="invalid coordinates"):
                parse_gff(f.name_temp)
        finally:
            Path(f.name_temp).unlink()
    
    def test_parse_gff_start_greater_than_end(self):
        """Test: GFF con start > end debe lanzar ValueError"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.gff', delete=False) as f:
            f.write("chr1\tRefSeq\tgene\t500\t100\t.\t+\t.\tID=gene1;Name=test\n")
            f.name_temp = f.name
        
        try:
            with pytest.raises(ValueError, match="start.*end"):
                parse_gff(f.name_temp)
        finally:
            Path(f.name_temp).unlink()
    
    def test_parse_gff_invalid_strand(self):
        """Test: GFF con strand inválido debe lanzar ValueError"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.gff', delete=False) as f:
            f.write("chr1\tRefSeq\tgene\t100\t500\t.\t?\t.\tID=gene1;Name=test\n")
            f.name_temp = f.name
        
        try:
            with pytest.raises(ValueError, match="invalid strand"):
                parse_gff(f.name_temp)
        finally:
            Path(f.name_temp).unlink()
    
    def test_parse_gff_missing_name(self):
        """Test: GFF sin Name o ID debe lanzar ValueError"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.gff', delete=False) as f:
            f.write("chr1\tRefSeq\tgene\t100\t500\t.\t+\t.\tTag=value\n")
            f.name_temp = f.name
        
        try:
            with pytest.raises(ValueError, match="no Name or ID"):
                parse_gff(f.name_temp)
        finally:
            Path(f.name_temp).unlink()
    
    def test_parse_gff_empty(self):
        """Test: GFF vacío debe lanzar ValueError"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.gff', delete=False) as f:
            f.write("# solo comentarios\n")
            f.name_temp = f.name
        
        try:
            with pytest.raises(ValueError, match="contains no genes"):
                parse_gff(f.name_temp)
        finally:
            Path(f.name_temp).unlink()


class TestReverseComplement:
    """Pruebas para la función reverse_complement()"""
    
    def test_reverse_complement_basic(self):
        """Test: Reverse complement básico"""
        assert reverse_complement('ATGC') == 'GCAT'
        assert reverse_complement('A') == 'T'
        assert reverse_complement('T') == 'A'
        assert reverse_complement('G') == 'C'
        assert reverse_complement('C') == 'G'
    
    def test_reverse_complement_with_n(self):
        """Test: Reverse complement con N"""
        assert reverse_complement('ATGCN') == 'NGCAT'
    
    def test_reverse_complement_palindrome(self):
        """Test: Secuencia palindrómica"""
        seq = 'GAATTC'
        assert reverse_complement(seq) == 'GAATTC'


class TestExtractGeneSeqs:
    """Pruebas para la función extract_gene_seqs()"""
    
    def test_extract_gene_seqs_basic(self):
        """Test: Extracción básica de genes"""
        genome = {'chr1': 'ATGCGTACGATCGATCGATCGA'}
        genes = [
            {'seqid': 'chr1', 'start': 1, 'end': 10, 'strand': '+', 'name': 'gene1'},
            {'seqid': 'chr1', 'start': 11, 'end': 20, 'strand': '+', 'name': 'gene2'}
        ]
        
        result = extract_gene_seqs(genome, genes)
        assert len(result) == 2
        assert 'gene1' in result[0][0]
        assert result[0][1] == 'ATGCGTACGA'
    
    def test_extract_gene_seqs_reverse_strand(self):
        """Test: Extracción con strand negativo"""
        genome = {'chr1': 'ATGCGTACGA'}
        genes = [
            {'seqid': 'chr1', 'start': 1, 'end': 4, 'strand': '-', 'name': 'gene1'}
        ]
        
        result = extract_gene_seqs(genome, genes)
        # Reverse complement de ATGC es GCAT
        assert result[0][1] == 'GCAT'
    
    def test_extract_gene_seqs_min_length(self):
        """Test: Filtro de longitud mínima"""
        genome = {'chr1': 'ATGCGTACGATCGATCGATCGA'}
        genes = [
            {'seqid': 'chr1', 'start': 1, 'end': 5, 'strand': '+', 'name': 'short'},
            {'seqid': 'chr1', 'start': 1, 'end': 15, 'strand': '+', 'name': 'long'}
        ]
        
        result = extract_gene_seqs(genome, genes, min_length=10)
        assert len(result) == 1
        assert 'long' in result[0][0]
    
    def test_extract_gene_seqs_seqid_not_found(self):
        """Test: Secuencia (seqid) no encontrada en genoma"""
        genome = {'chr1': 'ATGCGTACGA'}
        genes = [
            {'seqid': 'chr2', 'start': 1, 'end': 5, 'strand': '+', 'name': 'gene1'}
        ]
        
        with pytest.raises(ValueError, match="not found in FASTA"):
            extract_gene_seqs(genome, genes)
    
    def test_extract_gene_seqs_out_of_bounds(self):
        """Test: Coordenadas fuera de rango"""
        genome = {'chr1': 'ATGCGTACGA'}
        genes = [
            {'seqid': 'chr1', 'start': 1, 'end': 100, 'strand': '+', 'name': 'gene1'}
        ]
        
        with pytest.raises(ValueError, match="out of bounds"):
            extract_gene_seqs(genome, genes)
    
    def test_extract_gene_seqs_invalid_min_length(self):
        """Test: min_length inválido"""
        genome = {'chr1': 'ATGCGTACGA'}
        genes = [
            {'seqid': 'chr1', 'start': 1, 'end': 5, 'strand': '+', 'name': 'gene1'}
        ]
        
        with pytest.raises(ValueError, match="must be a positive integer"):
            extract_gene_seqs(genome, genes, min_length=-1)
    
    def test_extract_gene_seqs_header_format(self):
        """Test: Formato correcto del encabezado FASTA"""
        genome = {'chr1': 'ATGCGTACGA'}
        genes = [
            {'seqid': 'chr1', 'start': 1, 'end': 5, 'strand': '+', 'name': 'araC'}
        ]
        
        result = extract_gene_seqs(genome, genes)
        header = result[0][0]
        assert '>araC' in header
        assert 'gene_coords=1-5' in header
        assert 'strand=+' in header


class TestIntegration:
    """Pruebas de integración completa"""
    
    def test_complete_workflow(self):
        """Test: Flujo completo del programa"""
        # Crear archivos temporales
        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir = Path(tmpdir)
            
            # Crear FASTA
            fasta_file = tmpdir / 'test.fasta'
            with open(fasta_file, 'w') as f:
                f.write(">chr1\n")
                f.write("ATGCGTACGATCGATCGATCGATAA\n")
            
            # Crear GFF
            gff_file = tmpdir / 'test.gff'
            with open(gff_file, 'w') as f:
                f.write("chr1\tRefSeq\tgene\t1\t10\t.\t+\t.\tID=gene1;Name=araC\n")
                f.write("chr1\tRefSeq\tgene\t11\t20\t.\t-\t.\tID=gene2;Name=crp\n")
            
            # Cargar datos
            genome = load_fasta(str(fasta_file))
            genes = parse_gff(str(gff_file))
            
            # Extraer genes
            result = extract_gene_seqs(genome, genes)
            
            assert len(result) == 2
            assert result[0][1] == 'ATGCGTACGA'  # Forward strand
            # Reverse complement de TCGATCGATC es GATCGATCGA
            assert result[1][1] == 'GATCGATCGA'
    
    def test_workflow_with_min_length(self):
        """Test: Flujo completo con filtro de longitud"""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir = Path(tmpdir)
            
            # Crear FASTA
            fasta_file = tmpdir / 'test.fasta'
            with open(fasta_file, 'w') as f:
                f.write(">chr1\n")
                f.write("ATGCGTACGATCGATCGATCGATAA\n")
            
            # Crear GFF
            gff_file = tmpdir / 'test.gff'
            with open(gff_file, 'w') as f:
                f.write("chr1\tRefSeq\tgene\t1\t5\t.\t+\t.\tID=gene1;Name=short\n")
                f.write("chr1\tRefSeq\tgene\t1\t15\t.\t+\t.\tID=gene2;Name=long\n")
            
            # Ejecutar
            genome = load_fasta(str(fasta_file))
            genes = parse_gff(str(gff_file))
            result = extract_gene_seqs(genome, genes, min_length=10)
            
            assert len(result) == 1
            assert 'long' in result[0][0]


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
