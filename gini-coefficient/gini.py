import numpy as np


def gini_coefficient(y_pred, y_true):
    """Gini coefficient for predictions/probabilities of a binary target

    :param y_pred: binary predictions or prediction probabilities
    :type y_pred: np.ndarray
    :param y_true: iterable binary target
    :type y_true: np.ndarray
    :return: Gini coefficient
    :rtype: float
    """
    gini = somers_d(iterable_1=y_pred, iterable_2=y_true)

    return gini


def somers_d(iterable_1, iterable_2):
    """Equal to Kendall's Tau-a ratio: tau(iter1, iter2) / tau(iter2, iter2)

    :param iterable_1: iterable
    :type iterable_1: np.ndarray
    :param iterable_2: iterable
    :type iterable_2: np.ndarray
    :return: Somers' D
    :rtype: float
    """
    d = kendalls_tau(iterable_1, iterable_2)
    d /= kendalls_tau(iterable_2, iterable_2)

    return d


def kendalls_tau(iterable_1, iterable_2):
    """Kendall's Tau-a: concordant pairs less discordant pairs over number of pairs

    :param iterable_1: iterable
    :type iterable_1: np.ndarray
    :param iterable_2: iterable
    :type iterable_2: np.ndarray
    :return: Kendall's Tau-a
    :rtype: float
    """
    if len(iterable_1) != len(iterable_2):
        raise ValueError("Iterables must have the same length")

    n_elements = len(iterable_1)
    n_pairs = n_elements * (n_elements - 1) / 2

    pairwise_differences_1 = get_pairwise_differences(iterable_1)
    pairwise_differences_2 = get_pairwise_differences(iterable_2)

    tau = (np.sign(pairwise_differences_1) * np.sign(pairwise_differences_2)).sum()
    tau /= n_pairs

    return tau


def get_pairwise_differences(iterable):
    """Differences between distinct pairs of elements without repeats

    :param iterable: length n
    :type iterable: np.ndarray
    :return: pairwise_differences iterable[j] - iterable[i] for i less than j, length n(n-1)/2
    :rtype: np.ndarray
    """
    n_elements = len(iterable)

    pairwise_differences = np.array(
        [
            iterable[j] - iterable[i]
            for i in range(n_elements)
            for j in range(i + 1, n_elements)
        ]
    )

    return pairwise_differences
