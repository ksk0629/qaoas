import attrs
import numpy as np

import qualtran as qlt
from qualtran.bloqs.basic_gates import CNOT, Rz


@attrs.frozen
class CostEvolution(qlt.Bloq):
    ising: tuple[tuple[tuple[int, ...], float], ...]
    gamma: float

    @property
    def num_qubits(self) -> int:
        return (
            np.max([np.max(indices_and_value[0]) for indices_and_value in self.ising])
            + 1
        )

    @property
    def signature(self) -> qlt.Signature:
        return qlt.Signature(
            [
                qlt.Register(
                    "q", qlt.QBit(), shape=(self.num_qubits,), side=qlt.Side.THRU
                )
            ]
        )

    def build_composite_bloq(
        self, bb: qlt.BloqBuilder, *, q: qlt.Register
    ) -> dict[str, qlt.Register]:
        for indices_and_coefficient in self.ising:
            indices, coefficient = indices_and_coefficient
            parameter = 2 * self.gamma * coefficient
            num_qubits = len(indices)

            if num_qubits == 1:
                q[indices[0]] = bb.add(Rz(parameter), q=q[indices[0]])
            elif num_qubits > 1:
                for k in range(num_qubits - 1):
                    q[k], q[k + 1] = bb.add(CNOT(), ctrl=q[k], target=q[k + 1])
                # Apply RZ gate to the last qubit.
                q[indices[-1]] = bb.add(Rz(parameter), q=q[indices[-1]])
                # Reverse CNOT chain over the qubits
                for k in range(num_qubits - 2, -1, -1):
                    q[k], q[k + 1] = bb.add(CNOT(), ctrl=q[k], target=q[k + 1])
            else:
                raise ValueError(
                    f"The number of qubits must be positive, but {num_qubits}"
                )

        return {"q": q}


if __name__ == "__main__":
    import cirq
    import numpy as np
    from qualtran._infra.gate_with_registers import get_named_qubits

    ising = (((0, 1), 0.4), ((0, 1, 2), 0.2), ((1,), 0.4))
    gamma = np.pi / 2
    cost_evolution = CostEvolution(ising=ising, gamma=gamma)

    cbloq = cost_evolution.as_composite_bloq()
    in_quregs = get_named_qubits(cbloq.signature.lefts())
    cost_evolution_circuit, quregs = cbloq.to_cirq_circuit_and_quregs(**in_quregs)
    print(cirq.final_state_vector(cost_evolution_circuit))

    qubits = np.asarray(quregs["q"], dtype=object).ravel().tolist()

    circuit = cirq.Circuit(
        cost_evolution_circuit,
        cirq.measure(*qubits, key="q"),
    )
    print(circuit)
    sim = cirq.Simulator()
    result = sim.run(circuit, repetitions=500)

    bits = result.measurements["q"]
    print(np.unique(bits, axis=0))
