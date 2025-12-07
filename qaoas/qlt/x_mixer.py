import attrs

import qualtran as qlt
from qualtran.bloqs.basic_gates import Rx


@attrs.frozen
class XMixer(qlt.Bloq):
    """X mixer class"""

    num_qubits: int
    beta: float

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
        # Compute the right angle.
        parameter = 2 * self.beta
        for index in range(self.num_qubits):
            # Add Rx gate to each qubit.
            q[index] = bb.add(Rx(parameter), q=q[index])

        return {"q": q}


if __name__ == "__main__":
    import cirq
    import numpy as np
    from qualtran._infra.gate_with_registers import get_named_qubits

    num_qubits = 3
    beta = np.pi / 2
    x_mixer = XMixer(num_qubits=num_qubits, beta=beta)

    cbloq = x_mixer.as_composite_bloq()
    in_quregs = get_named_qubits(cbloq.signature.lefts())
    x_mixer_circuit, quregs = cbloq.to_cirq_circuit_and_quregs(**in_quregs)

    qubits = np.asarray(quregs["q"], dtype=object).ravel().tolist()

    circuit = cirq.Circuit(
        x_mixer_circuit,
        cirq.measure(*qubits, key="q"),
    )
    print(circuit)
    sim = cirq.Simulator()
    result = sim.run(circuit, repetitions=500)

    bits = result.measurements["q"]
    print(bits)
