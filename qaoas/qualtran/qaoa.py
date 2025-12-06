import attrs

import numpy as np

import qualtran as qlt

from all_hadamards import AllHadamards
from x_mixer import XMixer
from cost_evolution import CostEvolution


@attrs.frozen
class QAOA(qlt.Bloq):
    ising: tuple[tuple[tuple[int, ...], float], ...]
    betas: tuple[float, ...]
    gammas: tuple[float, ...]
    p: int

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
        q = bb.add(AllHadamards(num_qubits=self.num_qubits), q=q)

        for index in range(self.p):
            q = bb.add(XMixer(num_qubits=self.num_qubits, beta=self.betas[index]), q=q)
            q = bb.add(CostEvolution(ising=self.ising, gamma=self.gammas[index]), q=q)

        return {"q": q}


if __name__ == "__main__":
    import cirq
    import numpy as np
    from qualtran._infra.gate_with_registers import get_named_qubits

    ising = (((0, 1), 0.4), ((0, 1, 2), 0.2), ((1,), 0.4))
    num_qubits = 3
    p = 2
    betas = tuple([np.pi / 2 + 1 / index for index in range(1, p + 1)])
    gammas = tuple([np.pi / 4 + 1 / index for index in range(1, p + 1)])
    qaoa = QAOA(ising=ising, betas=betas, gammas=gammas, p=p)

    cbloq = qaoa.as_composite_bloq()
    in_quregs = get_named_qubits(cbloq.signature.lefts())
    print(in_quregs)
    qaoa_circuit, quregs = cbloq.to_cirq_circuit_and_quregs(**in_quregs)
    print(cirq.final_state_vector(qaoa_circuit))

    qubits = np.asarray(quregs["q"], dtype=object).ravel().tolist()

    circuit = cirq.Circuit(
        qaoa_circuit,
        cirq.measure(*qubits, key="q"),
    )
    print(circuit)
    sim = cirq.Simulator()
    result = sim.run(circuit, repetitions=1000)

    bits = result.measurements["q"]
    print(np.unique(bits, axis=0))

    keys = [cirq.big_endian_bits_to_int(row) for row in bits]
    hist = {k: keys.count(k) for k in set(keys)}
    print(hist)
