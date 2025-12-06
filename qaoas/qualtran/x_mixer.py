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
