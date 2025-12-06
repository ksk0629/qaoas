from guppylang import guppy
from guppylang.std.angles import angle
from guppylang.std.builtins import array
from guppylang.std.quantum import qubit

num_qubits = guppy.nat_var("num_qubits")


@guppy
def initialise_superposition(qubits: array[qubit, num_qubits]) -> None:
    """Initialise the uniform superposition.

    :param array[qubit, num_qubits] qubits: qubits to be gotten as the superposition
    """
    # Apply the Hadamard gate to all the qubits.
    pass


@guppy
def x_mixer(qubits: array[qubit, num_qubits], beta: angle) -> None:
    """Apply X mixer to the borrowed qubits.

    :param array[qubit, num_qubits] qubits: qubits to be applied the X mixer to
    :param angle beta: the parameter
    """
    # Evolute the qubits with the X mixer using the given parameter beta.
    pass


@guppy
def cost_evolution(
    qubits: array[qubit, num_qubits], ising: dict[tuple[int, ...], float], gamma: angle
):
    """Apply the cost ansatz specified by the given ising dict.

    :param array[qubit, num_qubits] qubits: qubits to be evolved by the cost Ising Hamiltonian
    :param dict[tuple[int, ...], float] ising: the Ising Hamiltonian
    :param angle gamma: the parameter
    """
    # Evolute the qubits with the cost Hamiltonian specified by the given ising using the given parameter gamma.
    pass


@guppy
def qaoa(ising: dict[tuple[int, ...], float], p: int) -> None:
    """Create QAOA ansatz.

    :param dict[tuple[int, ...], float] ising: the Ising Hamiltonian
    :param int p: the number of layers
    """
    # Identify the number of qubits needed.

    # Create qubits.

    # Initialise the qubits.

    # Apply the cost Hamiltonian and the mixer Hamiltonian for the give p times.

    # Return the QAOA circuit.


if __name__ == "__main__":
    print("Hello QAOA world.")
