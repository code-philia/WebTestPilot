from enum import Enum


class ActionEnum(Enum):
    CLICK = "click"
    TYPE = "type"

    @classmethod
    def from_str(cls, s: str) -> "ActionEnum":
        """
        Convert a string to an ActionEnum.
        Raises ValueError if the string is not a valid action.
        """
        MAPPING = {
            "click": cls.CLICK,
            "type": cls.TYPE,
            "fill": cls.TYPE
        }

        if s in MAPPING:
            return MAPPING[s]
        else:
            raise ValueError(f"Invalid action string '{s}'. Valid actions: {list(MAPPING.keys())}")


XPath = str
TraceStep = tuple[ActionEnum, XPath]
Trace = list[TraceStep]


def task_completion(pred: Trace, gt: Trace) -> float:
    """
    Indicates whether the agent has completed the exact interaction trace.

    TC = 1 if LCS(pred, gt) == gt; otherwise 0
    """
    return 1.0 if pred == gt else 0.0


def correct_trace(pred: Trace, gt: Trace) -> tuple[float, Trace]:
    """
    Measures how much of the ground truth trace is preserved in the agent's
    trace. We compute the LCS between the two traces and normalize it by the length of the ground
    truth.

    CT = |LCS(pred, gt)| / |gt|
    """
    m, n = len(pred), len(gt)
    dp = [[0] * (n + 1) for _ in range(m + 1)]

    # Dynamic programming LCS
    for i in range(1, m + 1):
        for j in range(1, n + 1):
            if pred[i - 1] == gt[j - 1]:
                dp[i][j] = dp[i - 1][j - 1] + 1
            else:
                dp[i][j] = max(dp[i - 1][j], dp[i][j - 1])

    # Backtrack to reconstruct LCS sequence
    i, j = m, n
    lcs_sequence = []
    while i > 0 and j > 0:
        if pred[i - 1] == gt[j - 1]:
            lcs_sequence.append(pred[i - 1])
            i -= 1
            j -= 1
        elif dp[i - 1][j] >= dp[i][j - 1]:
            i -= 1
        else:
            j -= 1
    lcs_sequence.reverse()

    ratio = len(lcs_sequence) / len(pred) if pred else 0.0
    return ratio, lcs_sequence


def correct_step(pred: Trace, gt: Trace) -> float:
    """
    Measures the proportion of steps in the agent trace that are also found in
    the ground truth.

    CS = |pred ∩ gt| / |gt|
    """
    if not gt: return 0.0

    pred_set, gt_set = set(pred), set(gt)    
    intersection_count = len(pred_set & gt_set)
    return intersection_count / len(gt_set)
