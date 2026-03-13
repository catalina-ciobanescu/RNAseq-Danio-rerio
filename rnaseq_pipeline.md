# RNAseq pipeline

This is a summary of the steps and programs involved in my bioinformatic pipeline to analyze RNAseq data and get read counts at a per-gene and per-exon level

## Brief description of the data:
- The data is composed of 40 samples, with two files per sample - one for each pair read.
- Each sample is a pool of 6 zebrafish juvenile heads
- The samples include five lines: 
    - The Sel1 hi and lo lines
    - The Sel3 hi and low lines
    - The Sel3 mid line, which works as a control
- For each line Johannes ran a shoaling assay and selected the six highest and six lowest shoalers
- He did this four times (replicates a-d) per line
    - Replicates a and b are same clutch siblings, with one day of difference
    - Likewise for replicates c and d
- Sample codes are the following:
    [LineNumber][Hi/Lo line][Hi/Lo performers in assay]_[replicate a-d]
    E.g 3LoHi_a line Sel3 Low, high shoalers, repeat a


## 1 - Setup work environment

### 1.1. Create a git repository and clone it to your $HOME folder in curnagl. 
This is important not only for version control but also because it stores your scripts in the cloud and there is less chance of losing your scripts to an accident. After the raw data, the scripts are the most valuable files for a bioinformatician!!
    - I recommend creating your repository in GitHub only because of the easier integration with the GitHub Copilot AI companion. However, there are other online hosting services for git repositories like BitBucket.
    
#### 1.2. Create a conda environment in curnagl
- Important for the replicability of your analyses! Conda environments make sure you always use the same version and set of programs for your analyses. You should use a different conda environment for different bioinformatic pipelines. For now, you can set up one conda environment for the RNAseq pipeline. 
- Installing conda in curnagl has a couple of quirks. So follow the curnagl wiki page on how to use conda in the cluster: https://wiki.unil.ch/ci/books/high-performance-computing-hpc/page/using-conda-and-anaconda 

### 1.3 Download Zebrafish genome
- We are going to be mapping and aligning our RNAseq reads to the zebrafish (Danio rerio) reference genome, so we need to download it! 
- This is the link to the reference genome: https://www.ncbi.nlm.nih.gov/datasets/genome/GCF_049306965.1/ 
- You can download it from the website and then upload it to curnagl, but you can also download it directly from curnagl using the NCBI Datasets command-line tools (CLI).
- You can install the program with conda using the following command: 
    conda install -c conda-forge ncbi-datasets-cli
- From curnagl you can then use the ncbi datasets tool to download the genome
    datasets download genome accession GCF_049306965.1 --include gff3,genome

### 1.4. Convert zebrafish genome annotation file from GFF to GTF
- The programs we are going to use are not compatible with the default gff3 format of the annotation file that we downloaded with the zebrafish genome. So we need to convert it to a format known as gtf.
- This can be done with a program called "agat". Once you install it you can use the script "agat_convert_sp_gff2gtf.pl" to do this. Read the agat documentation for more info on how to use the script.

### 1.5 Install necessary programs using conda
- Using conda install the following programs:
    - FastQC (for quality control of the rnaseq reads)
    - Trimmomatic (for getting read of low-quality rnaseq reads)
    - STAR (for aligning your filtered good quality reads to the zebrafish genome)
    - Subread ( a collection of programs for rnaseq analysis, which includes the program FeatureCounts that we are going to use to summarize how many reads mapped to each gene/exon on the genome)

### 1.6 Find your RNAseq data and the metadata associated to it
- Once you have access to the LarschLab network drive, you will be able to find the files here:
    - Raw data: \\nasdcsr.unil.ch\RECHERCHE\FAC\FBM\CIG\jlarsch\default\D2c\07_Data\Carlos\Sequencing\RNASeq_ShoalingSelection\raw
    - Metadata: \\nasdcsr.unil.ch\RECHERCHE\FAC\FBM\CIG\jlarsch\default\D2c\Carlos\RNAseq\samples_info\


## 2 - Check quality of your RNAseq data

### 2.1 Use FastQC and MultiQC to get a summary of your data quality

- Use the program FastQC to get quality reports for all of your samples (This should be a script)
- Use the program MultiQC to copile the per-sample reports into a single report. (This doesn't need to be a script. You can run the command directly on the terminal. However, DON'T do it on the login node. Get to a computing node first with the command "Sinteractive").
 - **Computing resources used**: 1 cpu, 8G memory, 1h

### 2.2 Use Trimmomatic to filter low-quality reads (This should be a script)

- Filtering on a per-sample basis. Use SLURMs array job functionality to submit all samples in parallel. 
- Run trimmomatic with the PE (pair-end) label, since our data is paired-end. You need to provide the two pair end files for each sample.
- You need to provide some filtering settings on the trimmomatic command. Read about them and try to find out what the default values are.
- Run again MultiQC to see the changes to your reads quality before and after filtering!
- **Computing resources used**: 4 cpu, 3G memory, 15min (optimized with *seff* info)


## 3 - Map good quality reads to genome 

- In this step we are going to align our filtered high-quality reads to the Danio rerio genome to find out how many of our reads are coming from each gene - this is the basis to our measurement of gene expression 

- For this step I use a program called STAR. It is one of the most commonly used programs for this, but definitively not the only one. I use it because I am interested in alternative splicing and for that STAR is considered one of the best aligners.
    - I highly recommend that you read at least the first part of the STAR manual to understand a bit better how it works. You can find it here: https://github.com/alexdobin/STAR/blob/master/doc/STARmanual.pdf
    - There is also a nice tutorial to STAR here: https://hbctraining.github.io/Intro-to-rnaseq-hpc-O2/lessons/03_alignment.html



### 3.1 STAR genome indexing and preparation (this should be its own script)
 - Before doing the actual alignment, we need to generate a genome index. This is a folder where STAR writes several files with summary information on our genome that it requires to align more efficiently the reads on the mapping step. 

 - This step can be **very** memory intensive. If your job is failing due to segmentation issues, try increasing the memory that you are allocating to the job when you submit it to Curnagl. 
- **Computing resources used**: 6 cpu, 30G memory, 30min (optimized with *seff* info)


### 3.2 Read mapping with STAR - 2 step mode (this should be another script)
- This is the step where you map your reads to the genome. You can find the necessary commands in the tutorial and manual that I shared above.

- Things to keep in mind:
    - The alignment is made for each sample individually. Just like the quality filtering step
    - Since we are interested in alternative splicing, we are going to do the two-pass alignment method of STAR. This means that we are going to do twice alignment to benefit from the novel (i.e not in the genome annotation) splice junction recognition algorithm of STAR . Check the manual to see how this works. 

- The output of this step will be individual folders for each sample with a lot of files. The most important files are the ".bam" files. These are the files that contain the actual read alignments of your samples. They are binary files so if you open them, they will not be human readable, however they are what we are going to use as input for step 4. 

- Be careful to save the files of the 2nd mapping step on a different folder of the files of the 1st mapping step to avoid overwriting them. The default file names that STAR generates are the same regardless of whether your are running the first or second step of alignment. 

- **Computing resources used**: 8 cpu, 25G memory, 1h (optimized with *seff* info)



### 3.3 Mapping QC

- Now you can do the quality control of your bam files using MultiQC again! Some of the multiple files that STAR generates after mapping are quality reports. MultiQC can look for these files and compile a QC report for STAR. All you need to do is run MultiQC on the mother folder containing all the STAR folders for all your samples.

- However, you need to do this separately for the results of the first and second mapping steps, since the files will have the same name.  


## 4 - Read counting

- In this step we are going to take the alignments we did for all our samples in the previous step and count how many reads are aligned to each gene in the genome. Our output will be a huge table with genes on the rows and our samples in the columns and read counts on the cells of the table. Plus some metadata.
- For this we are going to use the program **featureCounts**. This is part of a package called **subread** so you will need to install **subread** in your conda environment.
- The manual for featureCounts can be found on chapter 6 of the subread manual: https://bioconductor.org/packages/release/bioc/vignettes/Rsubread/inst/doc/SubreadUsersGuide.pdf 



### 4.1 - Conversion of genome annotation gtf file to saf (important for exon usage analysis)

- This is an important step for the counting of reads mapping to exons - which is the information that we use for our splicing analysis.
- Annotation files usually will have information at the gene level and at the transcript-level.
- Often for a single-gene you will have multiple mRNAs transcript entries
- However featureCounts doesn't know how to properly deal with this, so it will assume that every exon in the multiple transcripts of a gene is a different exon, which often is not the case.
- This leads to the same exon being replicated multiple times in the output of featureCounts
- To avoid this issue we can "flatten" our annotation file into a .saf format.
- This saf format gets rid of all transcript-level information and only saves the information on the genes and their exons location, making the read counting process much simpler. 
- **subread** includes a program specific for this called **flattenGTF**
- When running **flattenGTF** you may run into an error due to a slight formatting issue with the gtf created by agat. For me the issue was on the **Dbxref** field of the 9th column of the gtf file. This field had two values instead of one. You just need to do a bit of shell scripting to merge this two values with an "_"
    - eg. Dbxref "GeneID:120821053" "Genbank:XM_040179415.1"; needs to become Dbxref "GeneID:120821053_Genbank:XM_040179415.1"



### 4.2 - Gene and exon-level read counting using featureCounts

- Once you have your SAF file, running featureCounts is actually super straightforward. Just check the command on the documentation for featureCounts.
- The most important setting you should pay attention to is the "-f" setting, which will determine whether featureCounts will count reads at the gene or exon-level


### 4.3 - Read counting QC

- Then use again multiqc to get a report on the results of featureCounts! 
    - Be careful to do this separately for the exon and gene-level data, since they will have the same name files and this will confuse multiqc


## 5 - Read counts pre-processing


## 6 - Gene expression and Exon Usage analyzes using EdgeR




