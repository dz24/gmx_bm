import matplotlib.pyplot as plt
import numpy as np
from dztools.funcs.plotter import COLS
import scienceplots
plt.style.use('science')


tprs = ["30k", "70k", "100k"]
atms = [32351, 68895, 101240]
trials = 5


for idx, (tpr, atm) in enumerate(zip(tprs, atms)):
	datas = []
	for trial in range(trials):
		data = np.loadtxt(f"{tpr}/perf_results_{trial}.txt")
		datas.append(data[:, 1])

	avg = np.average(datas, axis=0)
	std = np.std(datas, axis=0)

	plt.plot(data[:, 0], avg, color=COLS[idx])
	plt.scatter(data[:, 0], avg, color=COLS[idx], label=f"{atms[idx]/1000:.01f}k AT")
	plt.fill_between(data[:, 0], avg - std, avg + std, color=COLS[idx], alpha=0.5)

plt.legend(frameon=False, prop={'size': 7})
plt.xticks(data[:, 0])
plt.minorticks_off()
plt.xlabel("Parallel simulations")
plt.ylabel("Total ns/day")
plt.savefig('nsday.png', dpi=300)


