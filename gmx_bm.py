import os
import shutil
import subprocess
import sys
import logging
import numpy as np

logging.basicConfig(
    filename="benchmark.log", level=logging.INFO, filemode="a", format="%(message)s"
)

# example tgpu10 qsub.sh script
"""
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
"""


def detect_program(programs: list[str]) -> str:
    """List of possible program names given programs list."""

    for program in programs:
        # check if the program exists in the system's PATH
        if shutil.which(program):
            # return the program name for further use
            return program

    # return empty string if no programs are found
    return ""


def create_ff(inp: str, ff: str):
    """Create a new ff (file or folder)."""

    assert ff in ("file", "folder")
    append = ".txt" if ff == "file" else ""

    for trial in range(0, 1000):
        create = f"{inp}_{trial}" + append
        if os.path.exists(create):
            continue
        else:
            if ff == "folder":
                os.makedirs(create)
                logging.info(f"Benchmarking will occur in {create}")
            else:
                open(create, "a").close()
                logging.info(f"Results will be saved in {create}\n")
            break

    if trial == 999:
        logging.info("Existing trials exceeded {trial}! will exit now.")
        exit()
    return create


def gmx_bm(tpr: str, nsteps: int = 20000):
    """A python script to benchmark gromacs runs on TGPU10.

    This script assumes the tpr can be ran."""

    # check that tpr exist and get cwd and global tpr path
    assert tpr[-4:] == ".tpr"
    assert os.path.exists(tpr)
    tpr_g = os.path.abspath(tpr)
    logging.info(f"Using {tpr_g} for benchmarking")
    cwd = os.getcwd()

    # create file folder and cd
    bm_folder = create_ff("/tmp/gmx_bm", ff="folder")
    bm_results = create_ff(cwd + "/perf_results", ff="file")
    os.chdir(bm_folder)

    # check that gromacs engine can be run:
    gmx = detect_program(["gmx", "gmx_mpi", "gmx_d"])
    assert len(gmx) > 0

    # parallels to be run
    parallels = [1, 2, 4, 6, 9, 18]
    cpus = [18, 9, 4, 3, 2, 1]
    perfs = [0 for i in range(len(cpus))]
    for i, p in enumerate(parallels):

        # create bm folder
        p_folder = bm_folder + f"/{p}"
        if not os.path.exists(p_folder):
            os.makedirs(p_folder)
        os.chdir(p_folder)

        # same number of cpus for parallels
        commands = ["nvidia-cuda-mps-control -d"]
        for j, c in enumerate([cpus[i]] * p):
            # initialize empty gmx command
            torun = f"{gmx} mdrun -s {tpr_g} "

            # add hardware
            torun += f"-ntomp {cpus[i]} -pinstride 1 -pinoffset {j*cpus[i]} "
            torun += f"-pin on -gpu_id {0 if j < p/2 else 1} "

            # add gpu and other settings
            torun += "-notunepme -nb gpu -bonded gpu -pme gpu -resethway "

            # add nsteps, name and to run in background
            torun += f"-nsteps {nsteps} -deffnm {j} &"
            commands.append(torun)

        # write commands to file
        commands.append("wait")
        commands.append("echo quit | nvidia-cuda-mps-control")
        bash = f"prun_{p}.sh"
        np.savetxt(bash, commands, fmt="%s")

        # run bash
        logging.info(f"{p} parallels, {c} cpus, running ./{bash} in {p_folder}")
        out = subprocess.run(["bash", f"./{bash}"], capture_output=True, text=True)

        # get performance:
        logging.info("--- ns/day ---")
        prints = 0
        for line in out.stderr.split("\n"):
            if "Performance:" in line:
                perfs[i] += float(line.split()[1])
                logging.info(
                    f"{float(line.split()[1]):.04f} ns/day | " + commands[prints + 1]
                )
                prints += 1
        logging.info("---        ---")
        logging.info(
            f"Total performance for {p} parallels: {np.sum(perfs[i]):.04f} ns/day\n"
        )

    logging.info(f"Done simulating in {bm_folder}")
    np.savetxt(bm_results, np.array([parallels, perfs]).T, header="parallels\tns/day")
    logging.info(f"Results should be in {bm_results}")


gmx_bm(sys.argv[1])
