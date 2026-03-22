import streamlit as st
import matplotlib.pyplot as plt
from io import BytesIO
import random

# ---------------- GREEDY ----------------
def greedy_cutting(standard_length, kerf, cuts_required):
    pieces = []
    for item in cuts_required:
        pieces.extend([item['length']] * item['qty'])

    pieces.sort(reverse=True)
    bars = []

    for piece in pieces:
        placed = False
        for bar in bars:
            used = sum(bar) + (max(0, len(bar)-1) * kerf)
            needed = piece if len(bar) == 0 else piece + kerf
            if used + needed <= standard_length:
                bar.append(piece)
                placed = True
                break
        if not placed:
            bars.append([piece])

    waste = sum(
        standard_length - (sum(bar) + (max(0, len(bar)-1) * kerf))
        for bar in bars
    )

    efficiency = ((len(bars)*standard_length - waste) / (len(bars)*standard_length)) * 100

    return bars, len(bars), waste, round(efficiency, 2)


# ---------------- GENETIC ALGORITHM ----------------
def genetic_cutting(standard_length, kerf, cuts_required, pop_size=50, generations=50):

    pieces = []
    for item in cuts_required:
        pieces.extend([item['length']] * item['qty'])

    def fitness(order):
        bars = []
        for piece in order:
            placed = False
            for bar in bars:
                used = sum(bar) + (max(0, len(bar)-1) * kerf)
                needed = piece if len(bar) == 0 else piece + kerf
                if used + needed <= standard_length:
                    bar.append(piece)
                    placed = True
                    break
            if not placed:
                bars.append([piece])

        waste = sum(
            standard_length - (sum(bar) + (max(0, len(bar)-1) * kerf))
            for bar in bars
        )

        return waste, bars

    population = [random.sample(pieces, len(pieces)) for _ in range(pop_size)]

    for _ in range(generations):
        scored = [(fitness(ind), ind) for ind in population]
        scored.sort(key=lambda x: x[0][0])

        population = [ind for (_, ind) in scored[:pop_size//2]]

        children = []
        while len(children) < pop_size:
            p1, p2 = random.sample(population, 2)
            cut = random.randint(1, len(p1)-1)
            child = p1[:cut] + p2[cut:]
            children.append(child)

        population = children

    best = min(population, key=lambda x: fitness(x)[0])
    waste, bars = fitness(best)

    efficiency = ((len(bars)*standard_length - waste) / (len(bars)*standard_length)) * 100

    return bars, len(bars), waste, round(efficiency, 2)


# ---------------- GROUP ----------------
def group_bars(bars):
    grouped = {}
    for bar in bars:
        key = tuple(sorted(bar, reverse=True))
        grouped[key] = grouped.get(key, 0) + 1
    return grouped


# ---------------- GRAPH ----------------
def draw(grouped, std_len):
    fig, ax = plt.subplots(figsize=(10, 4))

    for i, (pattern, count) in enumerate(grouped.items()):
        left = 0
        for cut in pattern:
            ax.barh(i, cut, left=left, edgecolor='black')
            left += cut

        waste = std_len - left
        if waste > 0:
            ax.barh(i, waste, left=left)

        ax.text(std_len + 50, i, f"{count} Bars", va='center')

    ax.set_xlim(0, std_len + 300)
    ax.set_title("Cutting Layout")
    return fig


# ---------------- UI ----------------
st.title("🧠 AI Cutting Optimization Tool")

st.caption("Compare Greedy vs Genetic Algorithm for better material efficiency")

algorithm = st.selectbox(
    "Select Method",
    ["Greedy", "Genetic Algorithm (AI)"]
)

standard_length = st.number_input("Standard Length", value=3000)
kerf = st.number_input("Kerf", value=10)

cuts = []
rows = st.number_input("Number of cut types", 1, 10, 3)

for i in range(rows):
    l = st.number_input(f"Length {i+1}", key=f"l{i}")
    q = st.number_input(f"Qty {i+1}", key=f"q{i}")
    if l > 0 and q > 0:
        cuts.append({"length": int(l), "qty": int(q)})

if st.button("Run Optimization"):

    if algorithm == "Greedy":
        bars, total, waste, eff = greedy_cutting(standard_length, kerf, cuts)
    else:
        bars, total, waste, eff = genetic_cutting(standard_length, kerf, cuts)

    st.success(f"Bars: {total} | Waste: {waste} | Efficiency: {eff}%")

    grouped = group_bars(bars)
    fig = draw(grouped, standard_length)
    st.pyplot(fig)
