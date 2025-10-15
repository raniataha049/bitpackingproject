import time, random
from statistics import mean
from bitpacking.crossing import BitPackingCrossing
from bitpacking.noncrossing import BitPackingNonCrossing
from bitpacking.overflow import BitPackingOverflow

def measure(fn, *args, repeat=5):
    """Mesure moyenne en secondes sur plusieurs exécutions."""
    times = []
    for _ in range(repeat):
        t0 = time.perf_counter()
        fn(*args)
        times.append(time.perf_counter() - t0)
    return mean(times)

def run_bench(n=10000, seed=42):
    random.seed(seed)
    # trois types de distributions
    datasets = {
        "uniform_small": [random.randint(0, 255) for _ in range(n)],
        "mixed_overflow": [random.choice([random.randint(0, 50), random.randint(1000, 5000)]) for _ in range(n)],
        "wide_range": [random.randint(0, 2**20) for _ in range(n)]
    }

    results = []

    for name, data in datasets.items():
        print(f"\n=== Dataset: {name} (n={len(data)}) ===")

        for mode, cls in [
            ("crossing", BitPackingCrossing),
            ("non_crossing", BitPackingNonCrossing),
            ("overflow", BitPackingOverflow)
        ]:
            t_comp = measure(cls.from_list, data)
            comp = cls.from_list(data)
            t_get = measure(lambda: [comp.get(i) for i in range(len(data))])
            t_decomp = measure(comp.to_list)
            size_bits = len(comp.words) * 32 if hasattr(comp, "words") else len(comp.main_words) * 32
            ratio = size_bits / (len(data) * 32)
            print(f"{mode:13s} | k={getattr(comp, 'k', getattr(comp, 'k_base', '?')):>4} "
                  f"| size={size_bits/8:8.1f} B | ratio={ratio:6.2f} "
                  f"| comp={t_comp*1e3:7.2f} ms | decomp={t_decomp*1e3:7.2f} ms")

            results.append((name, mode, ratio, t_comp, t_decomp, t_get))

    return results

if __name__ == "__main__":
    run_bench()
