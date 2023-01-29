from scipy.stats.contingency import crosstab
import pandas as pd
import numpy as np


def get_recall(y_pred, y_true):
    """Recall for a binary classifier

    :param y_pred: predicted binary classes
    :type y_pred: np.ndarray
    :param y_true: true binary classes
    :type y_true: np.ndarray
    :return: recall - true positive rate
    :rtype: float
    """
    return get_true_positive_rate(y_pred, y_true)


def get_specificity(y_pred, y_true):
    """Specificity for a binary classifier

    :param y_pred: predicted binary classes
    :type y_pred: np.ndarray
    :param y_true: true binary classes
    :type y_true: np.ndarray
    :return: specificity - true negative rate
    :rtype: float
    """
    return get_true_negative_rate(y_pred, y_true)


def get_precision(y_pred, y_true):
    """Precision for a binary classifier

    :param y_pred: predicted binary classes
    :type y_pred: np.ndarray
    :param y_true: true binary classes
    :type y_true: np.ndarray
    :return: precision - true positives over true positives plus false positives
    :rtype: float
    """
    _, false_positives, _, true_positives = get_binary_outcome_counts(y_pred, y_true)
    precision = true_positives / (true_positives + false_positives)

    return precision


def get_true_positive_rate(y_pred, y_true):
    """False positive rate for a binary classifier

    :param y_pred: predicted binary classes
    :type y_pred: np.ndarray
    :param y_true: true binary classes
    :type y_true: np.ndarray
    :return: true_positive_rate - true positives over true positives plus false negatives
    :rtype: float
    """
    _, _, false_negatives, true_positives = get_binary_outcome_counts(y_pred, y_true)
    true_positive_rate = true_positives / (true_positives + false_negatives)

    return true_positive_rate


def get_false_positive_rate(y_pred, y_true):
    """False positive rate for a binary classifier

    :param y_pred: predicted binary classes
    :type y_pred: np.ndarray
    :param y_true: true binary classes
    :type y_true: np.ndarray
    :return: false_positive_rate - false positives over false positives plus true negatives
    :rtype: float
    """
    true_negatives, false_positives, _, _ = get_binary_outcome_counts(y_pred, y_true)
    false_positive_rate = false_positives / (false_positives + true_negatives)

    return false_positive_rate


def get_true_negative_rate(y_pred, y_true):
    """True negative rate for a binary classifier

    :param y_pred: predicted binary classes
    :type y_pred: np.ndarray
    :param y_true: true binary classes
    :type y_true: np.ndarray
    :return: true_negative_rate - true negatives over true negatives plus true positives
    :rtype: float
    """
    true_negatives, false_positives, _, _ = get_binary_outcome_counts(y_pred, y_true)
    true_negative_rate = true_negatives / (true_negatives + false_positives)

    return true_negative_rate


def get_false_negative_rate(y_pred, y_true):
    """False negative rate for a binary classifier

    :param y_pred: predicted binary classes
    :type y_pred: np.ndarray
    :param y_true: true binary classes
    :type y_true: np.ndarray
    :return: false_negative_rate - false negatives over false negatives plus true positives
    :rtype: float
    """
    _, _, false_negatives, true_positives = get_binary_outcome_counts(y_pred, y_true)
    false_negative_rate = false_negatives / (false_negatives + true_positives)

    return false_negative_rate


def get_binary_outcome_counts(y_pred, y_true):
    """True/False Positive/Negative counts for a binary classifier

    :param y_pred: predicted binary classes
    :type y_pred: np.ndarray
    :param y_true: true binary classes
    :type y_true: np.ndarray
    :return: true_negatives, false_positives, false_negatives, true_positives
    :rtype: (float, float, float, float)
    """
    confusion_matrix = get_confusion_matrix(y_pred, y_true)
    (
        true_negatives,
        false_positives,
        false_negatives,
        true_positives,
    ) = confusion_matrix.values.ravel()

    return true_negatives, false_positives, false_negatives, true_positives


def get_confusion_matrix(y_pred, y_true):
    """Confusion matrix for classifier

    :param y_pred: predicted classes
    :type y_pred: np.ndarray
    :param y_true: true classes
    :type y_true: np.ndarray
    :return: confusion_matrix - rows are true, columns are predictions, values are counts
    :rtype: pd.DataFrame
    """
    (row_vals, column_vals), counts = crosstab(y_true, y_pred)
    confusion_matrix = pd.DataFrame(
        index=pd.Index(row_vals, name="True"),
        columns=pd.Index(column_vals, name="Pred"),
        data=counts,
    )

    return confusion_matrix
