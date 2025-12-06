import cirq
import jijmodeling as jm
from qamomile.core.higher_ising_model import HigherIsingModel
import numpy as np
from scipy.optimize import minimize

from qualtran._infra.gate_with_registers import get_named_qubits

from qaoas.qualtran.qaoa import QAOA


def get_maxcut() -> jm.Problem:
    V = jm.Placeholder("V")
    E = jm.Placeholder("E", ndim=2)
    x = jm.BinaryVar("x", shape=(V,))
    e = jm.Element("e", belong_to=E)

    problem = jm.Problem("Maxcut", sense=jm.ProblemSense.MAXIMIZE)
    si = 2 * x[e[0]] - 1
    sj = 2 * x[e[1]] - 1
    si.set_latex("s_{e[0]}")
    sj.set_latex("s_{e[1]}")
    obj = 1 / 2 * jm.sum(e, (1 - si * sj))
    problem += obj
    return problem


if __name__ == "__main__":
    num_nodes = 5
    edges = [(0, 1), (0, 4), (1, 2), (1, 3), (2, 3), (3, 4)]
    data = {"V": num_nodes, "E": edges}

    interpreter = jm.Interpreter(data)
    instance = interpreter.eval_problem(get_maxcut())
    hubo, constant = instance.to_hubo()

    ising = HigherIsingModel.from_hubo(hubo=hubo, constant=constant)

    p = 5

    cost_history = []

    # Cost estimator function
    def estimate_cost(param_values):
        ising_list = []
        for indices, coefficient in ising.coefficients.items():
            ising_list.append((indices, coefficient))
        ising_tuple = tuple(ising_list)
        num_params = len(param_values)
        betas = tuple(param_values[: num_params // 2])
        gammas = tuple(param_values[num_params // 2 :])
        qaoa = QAOA(ising=ising_tuple, betas=betas, gammas=gammas, p=p)
        cbloq = qaoa.as_composite_bloq()
        in_quregs = get_named_qubits(cbloq.signature.lefts())
        qaoa_circuit, quregs = cbloq.to_cirq_circuit_and_quregs(**in_quregs)
        qubits = np.asarray(quregs["q"], dtype=object).ravel().tolist()
        circuit = cirq.Circuit(
            qaoa_circuit,
        )
        observables = 0
        for indices, coefficient in ising.coefficients.items():
            observable = coefficient
            for index in indices:
                observable *= cirq.Z(qubits[index])
            observables += observable
        ising_tuple = tuple(ising_list)
        sim = cirq.Simulator()
        cost = sim.simulate_expectation_values(
            program=circuit, observables=observables
        )[0].real
        cost_history.append(cost)
        return cost

    np.random.seed(901)
    betas_initial = tuple(np.random.random(size=p * 2).tolist())
    gammas_initial = tuple(np.random.random(size=p * 2).tolist())
    initial_params = betas_initial + gammas_initial

    # Run QAOA optimization
    result = minimize(
        estimate_cost,
        initial_params,
        method="COBYLA",
        options={"maxiter": 2000},
    )

    print(result)

    import matplotlib.pyplot as plt

    plt.title("Change of Cost", fontsize=15)
    plt.xlabel("Iteration", fontsize=15)
    plt.ylabel("Cost", fontsize=15)
    plt.xscale("log")
    plt.xlim(1, result.nfev)
    plt.plot(cost_history, label="Cost", color="#2696EB")
    plt.show()

    ising_list = []
    for indices, coefficient in ising.coefficients.items():
        ising_list.append((indices, coefficient))
    ising_tuple = tuple(ising_list)
    num_params = len(result.x)
    betas = tuple(result.x[: num_params // 2])
    gammas = tuple(result.x[num_params // 2 :])
    qaoa = QAOA(ising=ising_tuple, betas=betas, gammas=gammas, p=p)
    cbloq = qaoa.as_composite_bloq()
    in_quregs = get_named_qubits(cbloq.signature.lefts())
    qaoa_circuit, quregs = cbloq.to_cirq_circuit_and_quregs(**in_quregs)
    qubits = np.asarray(quregs["q"], dtype=object).ravel().tolist()
    circuit = cirq.Circuit(
        qaoa_circuit,
        cirq.measure(*qubits, key="q"),
    )
    print(circuit)
    sim = cirq.Simulator()
    result = sim.run(circuit, repetitions=1000)

    bits = result.measurements["q"]
    keys = [cirq.big_endian_bits_to_int(row) for row in bits]
    hist = {k: keys.count(k) for k in set(keys)}
    print(hist)

    best = max(hist, key=lambda x: hist[x])
    best_in_binary = bin(best)[2:].zfill(ising.num_bits)
    solution_dict = {index: int(binary) for index, binary in enumerate(best_in_binary)}
    print(best)
    print(best_in_binary)
    print(solution_dict)

    solution = instance.evaluate(solution_dict)
    print(instance.used_decision_variables)
    print(solution.objective)
