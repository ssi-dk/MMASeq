### Mapping ###

rule long_kmeraligner:
    input:
        R1 = lambda wc: sample(wc).read1(),
        database = rules.setup_kmeraligner_index.output.names
    params:
        options = lambda wc: sample(wc).options("kmeraligner"),
        tmp_results = f"{{database}}.res",
        tmp_matrix = f"{{database}}.mat.gz",
        prefix_db = rules.setup_kmeraligner_index.params.prefix    
    output:
        results = f"{outdir}/{{sample}}/raw/long/kmeraligner/kmeraligner_{{database}}.tsv",
        matrix = temp(f"{outdir}/{{sample}}/raw/long/kmeraligner/kmeraligner_{{database}}.mat.gz")
    conda:
        ENVS_DIR / "kmeraligner.yaml"
    log:
        stdout = f"{logdir}/kmeraligner_{{database}}_{{sample}}.log"
    message:
        "[kmeraligner]: Running KMA for {wildcards.database} on {wildcards.sample}"
    shell:
        """
        OUTDIR=$(dirname {output.results})
        mkdir -p $OUTDIR

        SAMDIR=$(dirname {output.sam})
        mkdir -p $SAMDIR

        cmd="kma -i {input.R1} -o $OUTDIR/{wildcards.database} -t_db {params.prefix_db} -na -nc -nf -matrix -1t1 {params.options}"

        echo "Executing command:\n$cmd\n" > {log.stdout} 2>&1
        eval $cmd >> {log.stdout} 2>&1

        echo "Renaming result files" >> {log.stdout} 2>&1
        mv $OUTDIR/{params.tmp_results} {output.results} >> {log.stdout} 2>&1
        mv $OUTDIR/{params.tmp_matrix} {output.matrix} >> {log.stdout} 2>&1
        """

### Characterizers ###

rule long_seqsero2:
    input:
        R1 = lambda wc: sample(wc).read1()
    params:
        options = lambda wc: sample(wc).options("seqsero2"),
        tmp_results = "SeqSero_result.tsv"
    output:
        results = f"{outdir}/{{sample}}/raw/long/seqsero2/seqsero2.tsv"
    threads: max(1, workflow.cores - 1 - (workflow.cores - 1) % 2)
    priority: 1
    conda:
        ENVS_DIR / "seqsero2.yaml"
    log:
        stdout = f"{logdir}/seqsero2_{{sample}}.log"
    message:
        "[seqsero2]: Running seqsero2 on {wildcards.sample}"
    shell:
        """
        OUTDIR=$(dirname {output.results})
        mkdir -p $OUTDIR

        cmd="SeqSero2_package.py -m k -t 5 -b mem -i {input.R1} -d $OUTDIR -n {wildcards.sample} -p {threads} {params.options}"

        echo "Executing command:\n$cmd\n" > {log.stdout} 2>&1
        eval $cmd >> {log.stdout} 2>&1

        echo "Renaming result files" >> {log.stdout} 2>&1
        mv $OUTDIR/{params.tmp_results} {output.results} >> {log.stdout} 2>&1
        """


rule long_plasmidfinder:
    input:
        R1 = lambda wc: sample(wc).read1(),
        database = rules.setup_plasmidfinder.output.database
    params:
        options = lambda wc: sample(wc).options("plasmidfinder"),
        tmp_results = "results_tab.tsv"
    output:
        results = f"{outdir}/{{sample}}/raw/long/plasmidfinder/plasmidfinder.tsv"
    conda:
        ENVS_DIR / "plasmidfinder.yaml"
    log:
        stdout = f"{logdir}/plasmidfinder_{{sample}}.log"
    message:
        "[plasmidfinder]: Running PlasmidFinder on {wildcards.sample}"
    shell:
        """
        OUTDIR=$(dirname {output.results})

        cmd="plasmidfinder.py -i {input.R1} -o $OUTDIR -p {input.database} -x {params.options}"

        echo "Executing command:\n$cmd\n" > {log.stdout} 2>&1
        eval $cmd >> {log.stdout} 2>&1     

        echo "Renaming result files" >> {log.stdout} 2>&1
        mv $OUTDIR/{params.tmp_results} {output.results} >> {log.stdout} 2>&1
        """


rule long_resfinder:
    input:
        R1 = lambda wc: sample(wc).read1(),
        res_database = rules.setup_resfinder.output.database
    params:
        options = lambda wc: sample(wc).options("resfinder"),
        tmp_results = "ResFinder_results_tab.txt"
    output:
        results = f"{outdir}/{{sample}}/raw/long/resfinder/resfinder.tsv"
    conda:
        ENVS_DIR / "resfinder.yaml"
    log:
        stdout = f"{logdir}/resfinder_{{sample}}.log"
    message:
        "[resfinder]: Running ResFinder on {wildcards.sample}"
    shell:
        """
        OUTDIR=$(dirname {output.results})
        cmd="run_resfinder.py -ifq {input.R1} -o $OUTDIR --acquired -db_res {input.res_database} {params.options}"
    
        echo "Executing command:\n$cmd\n" > {log.stdout} 2>&1
        eval $cmd >> {log.stdout} 2>&1

        echo "Renaming result files" >> {log.stdout} 2>&1
        mv $OUTDIR/{params.tmp_results} {output.results} >> {log.stdout} 2>&1
        """


rule long_pointfinder:
    input:
        R1 = lambda wc: sample(wc).read1(),
        res_database = rules.setup_resfinder.output.database,
        point_database = rules.setup_pointfinder.output.database
    params:
        options = lambda wc: sample(wc).options("pointfinder"),
        tmp_results = "PointFinder_results.txt"
    output:
        results = f"{outdir}/{{sample}}/raw/long/pointfinder/pointfinder.tsv"
    conda:
        ENVS_DIR / "resfinder.yaml"
    log:
        stdout = f"{logdir}/pointfinder_{{sample}}.log"
    message:
        "[pointfinder]: Running PointFinder on {wildcards.sample}"
    shell:
        """
        OUTDIR=$(dirname {output.results})
        cmd="run_resfinder.py -ifq {input.R1} -o $OUTDIR -db_res {input.res_database} --point -db_point {input.point_database} {params.options}"
    
        echo "Executing command:\n$cmd\n" > {log.stdout} 2>&1
        eval $cmd >> {log.stdout} 2>&1

        echo "Renaming result files" >> {log.stdout} 2>&1
        mv $OUTDIR/{params.tmp_results} {output.results} >> {log.stdout} 2>&1
        """


rule long_disinfinder:
    input:
        R1 = lambda wc: sample(wc).read1(),
        res_database = rules.setup_resfinder.output.database,
        disin_database = rules.setup_disinfinder.output.database
    params:
        options = lambda wc: sample(wc).options("disinfinder"),
        tmp_results = "DisinFinder_results_tab.txt"
    output:
        results = f"{outdir}/{{sample}}/raw/long/disinfinder/disinfinder.tsv"
    conda:
        ENVS_DIR / "resfinder.yaml"
    log:
        stdout = f"{logdir}/disinfinder_{{sample}}.log"
    message:
        "[disinfinder]: Running DisinFinder on {wildcards.sample}"
    shell:
        """
        OUTDIR=$(dirname {output.results})
        cmd="run_resfinder.py -ifq {input.R1} -o $OUTDIR -db_res {input.res_database} --disinfectant -db_disinf {input.disin_database} {params.options}"
    
        echo "Executing command:\n$cmd\n" > {log.stdout} 2>&1
        eval $cmd >> {log.stdout} 2>&1

        echo "Renaming result files" >> {log.stdout} 2>&1
        mv $OUTDIR/{params.tmp_results} {output.results} >> {log.stdout} 2>&1
        """


rule long_virulencefinder:
    input:
        R1 = lambda wc: sample(wc).read1(),
        database = rules.setup_virulencefinder.output.database
    params:
        options = lambda wc: sample(wc).options("virulencefinder"),
        tmp_results = "results_tab.tsv"
    output:
        results = f"{outdir}/{{sample}}/raw/long/virulencefinder/virulencefinder.tsv",
    conda:
        ENVS_DIR / "virulencefinder.yaml"
    log:
        stdout = f"{logdir}/virulencefinder_{{sample}}.log"
    message:
        "[virulencefinder]: Running VirulenceFinder on {wildcards.sample}"
    shell:
        """
        OUTDIR=$(dirname {output.results})
        cmd="python -m virulencefinder -ifq {input.R1} -o $OUTDIR -p {input.database} -x {params.options}"

        echo "Executing command:\n$cmd\n" > {log.stdout} 2>&1
        eval $cmd >> {log.stdout} 2>&1

        echo "Renaming result files" >> {log.stdout} 2>&1
        mv $OUTDIR/{params.tmp_results} {output.results} >> {log.stdout} 2>&1
        """


rule long_serotypefinder:
    input:
        R1 = lambda wc: sample(wc).read1(),
        database = rules.setup_serotypefinder.output.database
    params:
        options = lambda wc: sample(wc).options("serotypefinder"),
        tmp_results = "results_tab.tsv"
    output:
        results = f"{outdir}/{{sample}}/raw/long/serotypefinder/serotypefinder.tsv",
    conda:
        ENVS_DIR / "serotypefinder.yaml"
    log:
        stdout = f"{logdir}/serotypefinder_{{sample}}.log"
    message:
        "[serotypefinder]: Running SerotypeFinder on {wildcards.sample}"
    shell:
        """
        OUTDIR=$(dirname {output.results})

        cmd="serotypefinder -i {input.R1} -o $OUTDIR -p {input.database} -x {params.options}"

        echo "Executing command:\n$cmd\n" > {log.stdout} 2>&1
        eval $cmd >> {log.stdout} 2>&1

        echo "Renaming result files" >> {log.stdout} 2>&1
        mv $OUTDIR/{params.tmp_results} {output.results} >> {log.stdout} 2>&1
        """


rule long_lrefinder:
    input:
        res = rules.long_kmeraligner.output.results,
        matrix = rules.long_kmeraligner.output.matrix
    params:
        options = lambda wc: sample(wc).options("lrefinder")
    output:
        results = f"{outdir}/{{sample}}/raw/long/lrefinder/lrefinder_{{database}}.tsv",
    conda:
        ENVS_DIR / "py_utls.yaml"
    log:
        stdout = f"{logdir}/lrefinder_{{database}}_{{sample}}.log"
    message:
        "[LREfinder]: Identify genes and mutations for linezolid resistance in {wildcards.sample}"
    shell:
        """
        OUTDIR=$(dirname {output.results})
        mkdir -p $OUTDIR

        cmd="python {SCRIPTS_DIR}/LRE-Typer.py -ires {input.res} -imat {input.matrix} -o {output.results} {params.options}"

        echo "Executing command:\n$cmd\n" > {log.stdout} 2>&1
        eval $cmd >> {log.stdout} 2>&1
        """

rule long_chtyper:
    input:
        results = rules.long_kmeraligner.output.results
    params:
        id = 90,
        coverage = 60
    output:
        results = f"{outdir}/{{sample}}/raw/long/chtyper/chtyper_{{database}}.tsv"
    log:
        stdout = f"{logdir}/chtyper_{{database}}_{{sample}}.log"
    message:
        "[chtyper]: Running Chtyper on {wildcards.database} assembly for {wildcards.sample}"
    shell:
        """
        OUTDIR=$(dirname {output.results})
        mkdir -p $OUTDIR

        echo "Running awk filter on {input.results}" > {log.stdout} 2>&1

        awk -F'\t' 'NR==1{{for(i=1;i<=NF;i++){{if($i=="Template_Identity")id=i;if($i=="Template_Coverage")cov=i}}print;next}} ($id+0>{params.id} && $cov+0>{params.coverage})' {input.results} > {output.results} 2>> {log.stdout}
        """

### Wranglers ###

rule long_kmeraligner_wrangler:
    input:
        results = rules.long_kmeraligner.output.results,
        database = rules.setup_kmeraligner_index.output.names
    params:
        options = lambda wc: sample(wc).options("kmeraligner_wrangler"),
        metafile = f"{SCREENING_DIR}/kmeraligner_wrangler.tsv"
    output:
        filtered_tsv = f"{outdir}/{{sample}}/raw/long/kmeraligner_wrangler/kmeraligner_wrangler_{{database}}.tsv"
    conda:
        ENVS_DIR / "py_utls.yaml"
    log:
        stdout = f"{logdir}/kmeraligner_wrangler_{{database}}_{{sample}}.log"
    message:
        "[KMA kmeraligner_wrangler]: Filtering KMA .res result for {wildcards.sample}"
    shell:
        """
        mkdir -p $(dirname {output.filtered_tsv})

        cmd="python {SCRIPTS_DIR}/KMA_Filter.py --KMA_res {input.results} --metafile {params.metafile} --sample_id {wildcards.sample} --output {output.filtered_tsv} {params.options} > {log.stdout} 2>&1"

        echo "Executing command:\n$cmd\n" > {log.stdout}
        eval $cmd >> {log.stdout} 2>&1
        """
