import time
import random
from bitpacking.crossing import BitPackingCrossing
from bitpacking.noncrossing import BitPackingNonCrossing
from bitpacking.overflow import BitPackerOverflow


BITS_PER_INT = 32           
BANDWIDTH = 10_000_000      

def bitsize(bp):
    if hasattr(bp, "k"):
        return bp.k * bp.n
    elif hasattr(bp, "kprime"):
        return bp.kprime * bp.n
    elif hasattr(bp, "kprime_bits"):
        return bp.kprime_bits * bp.n
    else:
        return bp.n * 32 
    

def benchmark_one(data, mode):
    """Mesure les performances pour un mode donné"""
    n = len(data)
    start = time.perf_counter()

    
    if mode == "crossing":
        bp = BitPackingCrossing.from_list(data)
    elif mode == "non_crossing":
        bp = BitPackingNonCrossing.from_list(data)
    elif mode == "overflow":
        bp = BitPackerOverflow.from_list(data)
    else:
        raise ValueError("Mode inconnu")

    t_comp = (time.perf_counter() - start) * 1000  # ms

    start = time.perf_counter()
    _ = bp.to_list()
    t_decomp = (time.perf_counter() - start) * 1000  # ms


    start = time.perf_counter()
    _ = bp.get(len(data)//2)
    t_get = (time.perf_counter() - start) * 1000  # ms

    raw_bits = n * BITS_PER_INT
    comp_bits = bitsize(bp)
    gain = 100 * (1 - comp_bits / raw_bits)

   
    if raw_bits == comp_bits:
        t_seuil = None
        print("\n⚠️  Aucun gain de compression détecté (comp_bits = raw_bits).")
    else:
        t_seuil = (t_comp + t_decomp) / (raw_bits - comp_bits)
        print(f"\nLatence seuil t_seuil : {t_seuil:.8f} ms/bit")
        print(f"Si la latence réseau > {t_seuil:.8f} ms/bit, la compression devient avantageuse.")


    print(f"\n=== Mode : {mode} ===")
    print(f"n = {n} entiers")
    print(f"Gain : {gain:.2f} %")
    print(f"Tcomp : {t_comp:.4f} ms")
    print(f"Tdecomp : {t_decomp:.4f} ms")
    print(f"Tget : {t_get:.6f} ms")

    if raw_bits == comp_bits:
        print("⚠️  Aucun gain de compression détecté (comp_bits = raw_bits).")
        print("Latence seuil t_seuil : Non définie.")
    else:
        t_seuil = (t_comp + t_decomp) / (raw_bits - comp_bits)
        print(f"Latence seuil t_seuil : {t_seuil:.8f} ms/bit")
        print(f"Si la latence réseau > {t_seuil:.8f} ms/bit, la compression devient avantageuse.")

    return {
        "mode": mode,
        "gain": gain,
        "t_comp": t_comp,
        "t_decomp": t_decomp,
        "t_get": t_get,
        "t_seuil": t_seuil if raw_bits != comp_bits else None,
    }


    return {
        "mode": mode,
        "gain": gain,
        "t_comp": t_comp,
        "t_decomp": t_decomp,
        "t_get": t_get,
        "t_seuil": t_seuil,
    }


print("=== BENCHMARK BITPACKING 2025 ===")

mode = input("Choisissez le mode (crossing / non_crossing / overflow) : ").strip()
dtype = input("Type de données (croissante / aleatoire / melange / petites) : ").strip()
N = int(input("Combien d'entiers voulez-vous tester ? (ex: 100, 1000, 10000) : "))


if dtype == "croissante":
    data = list(range(N))
elif dtype == "aleatoire":
    data = [random.randint(0, 4095) for _ in range(N)]
elif dtype == "melange":
    data = [random.choice([0, 1, 2, 3, 1024, 2048, 4095]) for _ in range(N)]
elif dtype == "petites":
    data = [random.randint(0, 15) for _ in range(N)]
else:
    print("❌ Type de données invalide.")
    exit()


benchmark_one(data, mode)
print("\nFin du benchmark ✅")
