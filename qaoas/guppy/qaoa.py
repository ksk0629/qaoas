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
    pass


@guppy
def x_mixer(qubits: array[qubit, num_qubits], angle: angle) -> None:
    """Apply X mixer to the borrowed qubits.

    :param array[qubit, num_qubits] qubits: qubits to be applied the X mixer to
    """
    pass


@guppy
def cost_evolution(
    qubits: array[qubit, num_qubits], ising: dict[tuple[int, ...], float]
):
    """Apply the cost ansatz specified by the given ising dict.

    :param array[qubit, num_qubits] qubits: qubits to be evolved by the cost Ising Hamiltonian
    :param dict[tuple[int, ...], float] ising: the Ising Hamiltonian
    """
    pass


@guppy
def qaoa(ising: dict[tuple[int, ...], float]) -> None:
    """Create QAOA ansatz.

    :param dict[tuple[int, ...], float] ising: the Ising Hamiltonian
    """
    pass
