# gmx_bm

A simple `gmx_bm.py` script for testing gromacs parallel throughput on nodes with 2 nvidia GPUs and 18 total cores.

The `gmx_bm.py` can be ran on a pbs cluster by specifying the path to `gmx_bm.py` and a runnable `tpr` file,
```
script=path/to/gmx_bm.py
tpr=path/to/tpr/file
```

in the following pbs submission script,

```
#!/bin/bash
#PBS -N gmx_bm
#PBS -l nodes=1:ppn=18:gpus=2
#PBS -e job.err
#PBS -o job.out

# load gromacs
ml gromacs/2024.5-gcc-impi

# specify files to be ran
script=path/to/gmx_bm.py
tpr=path/to/tpr/file

# cd in working directory
cd ${PBS_O_WORKDIR}

# run the gmx python gmx_bm.py script
python3 $script $tpr
```
