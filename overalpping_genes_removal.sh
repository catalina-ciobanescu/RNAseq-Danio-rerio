#!/bin/bash

#SBATCH --job-name overlapping_reads
#SBATCH --output overlapping_reads_%A_%a.out
#SBATCH --partition cpu
#SBATCH --cpus-per-task 1
#SBATCH --mem=4G
#SBATCH --time=01:30:00
#SBATCH --array=1-40

echo "Job started at: $(date)"
python_script="/users/cciobane/readcount_clean_trial.py"

#module load python/3.7.6

current_dir="/work/FAC/FBM/CIG/jlarsch/default/Catalina/First-step/RNAseq-analysis-pipeline/reads_count"
metadata="$current_dir/metadata.txt"
# Read the sample name from the metadata file based on the SLURM_ARRAY_TASK_ID
line=$(sed -n "${SLURM_ARRAY_TASK_ID}p" $metadata) #it extracts the line from the tsv that is the same to the current array

echo "Processing $line at: $(date)"

read -r assignment_file_exon assignment_file_gene counts_file counts_output_file assignment_output_file summary_output_file <<< "$line"

python3 /users/cciobane/readcount_clean_trial.py "$assignment_file_exon" "$assignment_file_gene" "$counts_file" "$counts_output_file" "$assignment_output_file" "$summary_output_file"

