from collections import Counter

import guppylang
from guppylang import guppy
from guppylang.defs import GuppyFunctionDefinition
from guppylang.emulator import EmulatorResult
from guppylang.std.angles import angle, pi
from guppylang.std.builtins import array, comptime, result
from guppylang.std.quantum import qubit
from guppylang.std.quantum import cx, h, measure_array, rx, rz

guppylang.enable_experimental_features()

n = guppy.nat_var("n")


@guppy
def initialise_superposition(qubits: array[qubit, n]) -> None:
    """Initialise the uniform superposition.

    :param array[qubit, n] qubits: qubits to be gotten as the superposition
    """
    # Apply the Hadamard gate to all the qubits.
    for index in range(len(qubits)):
        h(qubits[index])


@guppy
def x_mixer(qubits: array[qubit, n], beta: angle) -> None:
    """Apply X mixer to the borrowed qubits.

    :param array[qubit, n] qubits: qubits to be applied the X mixer to
    :param angle beta: the parameter
    """
    # Evolute the qubits with the X mixer using the given parameter beta.
    for index in range(len(qubits)):
        rx(qubits[index], 2 * beta)


@guppy
def cost_evolution(
    qubits: array[qubit, n], ising: list[tuple[list[int], float]], gamma: angle
) -> None:
    """Apply the cost ansatz specified by the given ising dict.

    :param array[qubit, n] qubits: qubits to be evolved by the cost Ising Hamiltonian
    :param list[tuple[list, float]] ising: linear terms of the Ising Hamiltonian
    :param angle gamma: the parameter
    """
    # Evolute the qubits with the cost Hamiltonian specified by the given ising using the given parameter gamma.
    for indices_and_coefficient in ising:
        indices, coefficient = indices_and_coefficient

        if 1e-5 < coefficient < 1e-5:
            continue

        phase_gadget(qubits, indices, 2 * gamma * coefficient)


@guppy
def phase_gadget(qubits: array[qubit, n], indices: list[int], parameter: angle) -> None:
    """Apply the phase-gadget to the qubits.

    :param array[qubit, n] qubits: qubits to be applied the phase-gadget to
    :param angle parameter: the parameter
    :raises ValueError: if the number of qubits is not more than or equal to one
    """
    # Get the number of qubits to be processed.
    num_qubits = len(indices)

    if num_qubits == 1:
        # If it is a single qubit, just add RZ gate.
        rz(qubits[0], parameter)
    elif num_qubits > 1:
        # Build CNOT chain over the qubits.
        for k in range(num_qubits - 1):
            index = indices[k]
            cx(qubits[index], qubits[index + 1])
        # Apply RZ gate to the last qubit.
        rz(qubits[-1], parameter)
        # Reverse CNOT chain over the qubits
        for k in range(num_qubits - 2, -1, -1):
            index = indices[k]
            cx(qubits[index], qubits[index + 1])


@guppy
def qaoa(ising: list, p: int) -> None:
    """Create QAOA ansatz.

    :param list ising: the Ising Hamiltonian
    :param int p: the number of layers
    """
    # Identify the number of qubits needed.

    # Create qubits.

    # Initialise the qubits.

    # Apply the cost Hamiltonian and the mixer Hamiltonian for the give p times.

    # Return the QAOA circuit.


def build_qaoa_program(num_qubits: int) -> GuppyFunctionDefinition:
    @guppy
    def main() -> None:
        # allocate number of qubits specified from outer
        # python function using a `comptime` expression.
        qubits = array(qubit() for _ in range(comptime(num_qubits)))

        gamma = pi
        # ising = [((1, 0), 1.0)]
        # linear: list[int] = [0, 1, 2]
        qudratic = [[1, 2], [3, 4]]
        # cost_evolution(qubits, ising, gamma)
        # x_mixer(qubits, gamma)

        result("c", measure_array(qubits))

    # return the guppy function
    return main


if __name__ == "__main__":
    print("Hello QAOA world.")

    num_qubits = 2

    main = build_qaoa_program(num_qubits)
    shots = (
        main.emulator(n_qubits=num_qubits)
        # .stabilizer_sim()
        .with_seed(901)
        .with_shots(1000)
        .run()
    )

    def get_counts(shots: EmulatorResult) -> Counter[str]:
        """Counter treating all results from a shot as entries in a single bitstring"""
        counter_list = []
        for shot in shots:
            for e in shot:
                bitstring = "".join(str(k) for k in e[1])
                counter_list.append(bitstring)

        return Counter(counter_list)

    print(get_counts(shots))
