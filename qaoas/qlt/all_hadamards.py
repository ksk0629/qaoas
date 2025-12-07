import attrs

import qualtran as qlt
from qualtran.bloqs.basic_gates import Hadamard


@attrs.frozen
class AllHadamards(qlt.Bloq):
    """All Hadamards class"""

    num_qubits: int

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
        for index in range(self.num_qubits):
            q[index] = bb.add(Hadamard(), q=q[index])

        return {"q": q}


if __name__ == "__main__":
    import cirq
    import numpy as np
    from qualtran._infra.gate_with_registers import get_named_qubits

    num_qubits = 3
    superposition = AllHadamards(num_qubits=num_qubits)

    cbloq = superposition.as_composite_bloq()
    in_quregs = get_named_qubits(cbloq.signature.rights())
    superposition_circuit, quregs = cbloq.to_cirq_circuit_and_quregs(**in_quregs)

    qubits = np.asarray(quregs["q"], dtype=object).ravel().tolist()

    circuit = cirq.Circuit(
        superposition_circuit,
        cirq.measure(*qubits, key="q"),
    )
    print(circuit)
    sim = cirq.Simulator()
    result = sim.run(circuit, repetitions=500)

    bits = result.measurements["q"]
    print(np.unique(bits, axis=0))
