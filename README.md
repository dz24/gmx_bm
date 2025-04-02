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

# cd in working directory
cd ${PBS_O_WORKDIR}

# specify files to be ran
script=path/to/gmx_bm.py
tpr=path/to/tpr/file

# run the gmx python gmx_bm.py script
python3 $script $tpr
```

#### BM results

| Atoms/Parallels [ns/day] | 1        | 2        | 4         | 6         | 8         | 18        |
|-----------------|----------|----------|-----------|-----------|-----------|-----------|
| 32.4K           | 493.2    | 850.8    | 1232.2    | 1580.5    | 1726.3    | 2128.4    |
| 68.9K           | 414.8    | 792.4    | 875.5     | 984.9     | 1005.4    | 1011.8    |
| 101.2K          | 287.9    | 551.0    | 598.6     | 663.4     | 670.9     | 675.9     |


| Atoms/Parallels [relative] | 1        | 2        | 4         | 6         | 8         | 18        |
|-----------------|----------|----------|-----------|-----------|-----------|-----------|
| 32.4K           | 1.0      | 1.7      | 2.5       | 3.2       | 3.5       | 4.3       |
| 68.9K           | 1.0      | 1.9      | 2.1       | 2.4       | 2.4       | 2.4       |
| 101.2K          | 1.0      | 1.9      | 2.1       | 2.3       | 2.3       | 2.3       |
