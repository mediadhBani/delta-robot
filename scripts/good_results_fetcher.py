import matplotlib.pyplot as plt
import pickle

with open('stats.csv') as stats:
    for line in stats:
        i, p, v, avg_x, avg_y, std_x, std_y = (float(e) for e in line.split(','))

        if avg_x**2 + avg_y**2 < .01:
            print(i, p, v)
            pickle.load(open(f'mar/I{i:.0e}P{p:.0e}V{int(v)}.mpl', 'rb'))
            plt.title("")
            plt.savefig(f"I{i*i:.2f}_P{int(p):02}_V{int(v)}".replace('.', ',') + ".png")

# plt.show()