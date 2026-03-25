import sys
import shutil
from collections import Counter
from tracemalloc import start

def clean_counts(assignment_file_exon, assignment_file_gene, counts_file, counts_output_file, assignment_output_file, summary_output_file):
    gene_deduction = {} 
    status_counts = {'Assigned': 0, 'Unassigned_Unmapped': 0, 'Unassigned_Read_Type': 0, 'Unassigned_Singleton': 0, 'Unassigned_MappingQuality': 0, 'Unassigned_Chimera': 0, 'Unassigned_FragmentLength': 0, 'Unassigned_Duplicate': 0, 'Unassigned_MultiMapping': 0, 'Unassigned_Secondary': 0, 'Unassigned_NonSplit': 0, 'Unassigned_NoFeatures': 0, 'Unassigned_Overlapping_Length': 0, 'Unassigned_Ambiguity': 0} #we will count the number of reads in each of the categories
    overlapping_reads=set()

#First we readthe assignment gene file and identify the overlapping reads 
    with open(assignment_file_gene, 'r') as fin:
        for line in fin:
            if line.startswith('#') or line.startswith('Geneid') or line.startswith('ReadID'): #if it follows the right format then it will be written
                continue
            
            parts = line.strip().split('\t') 
            if len(parts) < 4:
                continue

            read_id, status, no_genes, genes = parts[0], parts[1], parts[2], parts[3] #reading the assignment file 
            gene_list = set(genes.split(',')) if genes != '' else set() #put all the genes for each of the respective reads in a set

            if len(gene_list) > 1 and status == 'Assigned':
                overlapping_reads.add(read_id) #adding the reads that overlap to this list
                #fout.write(line.replace('Assigned', 'Unassigned_Ambiguity')) #we update the assignment exon file sch that we remove gene overlapping reads
                for g in gene_list:
                    gene_deduction[g] = gene_deduction.get(g, 0) + 1 #we add to the deduction dictionary those reads that were assigned t multiple genes

    print(len(overlapping_reads))

#Second we read the exon assignment file and create a new update version where we remove the overlapping reads
    with open(assignment_file_exon, 'r') as fin, open(assignment_output_file, "w") as fout:
        for line in fin:
            if line.startswith('#') or line.startswith('Geneid') or line.startswith('ReadID'):
                fout.write(line)
                continue
            
            parts = line.strip().split('\t') 
            if len(parts) < 4:
                fout.write(line)
                continue

            read_id, status, no_genes, genes = parts[0], parts[1], parts[2], parts[3] 
            
            if read_id in overlapping_reads and status == 'Assigned': #if the read is in the list of reads that overlap and it is assigned we change the status to unassigned ambiguity
                # print(f"DEBUG GENE: Found overlap read {read_id}")
                status='Unassigned_MultiMapping'
                parts[1]=status
                #print(status)
                fout.write('\t'.join(parts) + '\n')
            
            else:
                fout.write(line)

            if status in status_counts:
                status_counts[status] += 1
            else:
                status_counts[status] = status_counts.get(status, 0) + 1 #we count the status of each line in the output assignment file - it will take the information from the newly created assignment file 


#We create the counts.txt output file by removing entries from the genes that count overlapping reads 
    with open(counts_file, 'r') as fin, open(counts_output_file, 'w') as fout:
        for line in fin:
            if line.startswith('#') or line.startswith('Geneid'):
                fout.write(line)
                continue
            
            parts = line.strip().split('\t') 
            gene_id = parts[0] 
            current_count = int(parts[-1]) 
            
            deduction = gene_deduction.get(gene_id, 0)
            new_count = max(0, current_count - deduction)
            
            parts[-1] = str(new_count)
            fout.write('\t'.join(parts) + '\n')

#Summary file 
    with open(summary_output_file, 'w') as sout:
        sout.write("Status\tCount\n")
        for status, count in status_counts.items():
            sout.write(f"{status}\t{count}\n")

    print(f"Cleaned counts: {counts_output_file}")
    print(f"Cleaned assignments: {assignment_output_file}")
    print(f"Summary file: {summary_output_file}")

if __name__ == "__main__":
    if len(sys.argv) < 6:
        print("Usage: python script.py <gene_assignment> <exon_assignment> <orig_counts> <new_counts> <new_assignment> <new_summary>")
    else:
        clean_counts(sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4], sys.argv[5], sys.argv[6])

# #paths 
# assignment_file_exon="/work/FAC/FBM/CIG/jlarsch/default/Catalina/First-step/RNAseq-analysis-pipeline/reads_count/reads_count_exon_O/1_mid_lo_a/1_mid_lo_a.Aligned.sortedByCoord.out.bam.featureCounts"
# assignment_file_gene="/work/FAC/FBM/CIG/jlarsch/default/Catalina/First-step/RNAseq-analysis-pipeline/reads_count/reads_count_gene_O/1_mid_lo_a/1_mid_lo_a.Aligned.sortedByCoord.out.bam.featureCounts"
# counts_file="/work/FAC/FBM/CIG/jlarsch/default/Catalina/First-step/RNAseq-analysis-pipeline/reads_count/reads_count_exon_O/1_mid_lo_a/counts.txt"
# counts_output_file="/work/FAC/FBM/CIG/jlarsch/default/Catalina/First-step/RNAseq-analysis-pipeline/reads_count/reads_count_exon_O/1_mid_lo_a/output.counts.txt"
# assignment_output_file="/work/FAC/FBM/CIG/jlarsch/default/Catalina/First-step/RNAseq-analysis-pipeline/reads_count/reads_count_exon_O/1_mid_lo_a/output_assignment.featureCounts"
# summary_output_file="/work/FAC/FBM/CIG/jlarsch/default/Catalina/First-step/RNAseq-analysis-pipeline/reads_count/reads_count_exon_O/1_mid_lo_a/output.counts.txt.summary"

# clean_counts(assignment_file_exon, assignment_file_gene, counts_file, counts_output_file, assignment_output_file, summary_output_file)