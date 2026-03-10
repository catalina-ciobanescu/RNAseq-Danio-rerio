#!/bin/bash

#SBATCH --job-name quality_check
#SBATCH --output quality_check.out
#SBATCH --partition cpu
#SBATCH --cpus-per-task 8 
#SBATCH --mem-per-cpu 10G 
#SBATCH --time 01:00:00 

module load fastqc
echo "Job started at: $(date)"
cd /work/FAC/FBM/CIG/jlarsch/default/Catalina/First-step/RNAseq-analysis-pipeline/raw
output=/work/FAC/FBM/CIG/jlarsch/default/Catalina/First-step/RNAseq-analysis-pipeline/results

for file in *.fastq.gz; do
    echo "running FastQC on $file"
    fastqc -o "$output" "$file"
done

echo "Job finished at: $(date)"

