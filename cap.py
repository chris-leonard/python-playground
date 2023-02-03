import numpy as np
import pandas as pd
from matplotlib import pyplot as plt


def plot_cap_curve(classifier, X, y, method="predict", normalised=True):
    """Plot Cumulative Accuracy Profile (CAP) curve for trained binary classifier

    :param classifier: trained sklearn binary classifier
    :param X: input data
    :type X: np.ndarray
    :param y: binary labels
    :type y: np.ndarray
    :param method: classifier method used to order labels ('predict' or 'predict_proba')
    :type method: str
    :param normalised: should the axes be scaled to range [0, 1]
    :type X: bool
    :return: None
    """
    # generate cumulative positive outputs for classifier and a perfect classifier
    perfect_cumulative_positive_outputs = get_perfect_cumulative_positive_outputs(y=y)
    classifier_cumulative_positive_outputs = get_classifier_cumulative_positive_outputs(
        classifier=classifier, X=X, y=y, method=method
    )

    samples_count = len(y)
    positive_samples_count = y.sum()

    # generate data for plotting
    x_plot = np.arange(0, samples_count + 1)

    y_classifier_plot = classifier_cumulative_positive_outputs
    y_perfect_plot = perfect_cumulative_positive_outputs
    y_random_plot = np.linspace(0, positive_samples_count, samples_count + 1)

    # rescale to [0, 1]
    if normalised:
        x_plot = x_plot / samples_count

        y_classifier_plot = y_classifier_plot / positive_samples_count
        y_perfect_plot = y_perfect_plot / positive_samples_count
        y_random_plot = y_random_plot / positive_samples_count

    # plot curves
    fig, ax = plt.subplots()

    ax.plot(x_plot, y_classifier_plot, label="Classifier")
    ax.plot(x_plot, y_perfect_plot, ls="--", label="Perfect")
    ax.plot(x_plot, y_random_plot, ls="--", color="k", label="Random")

    # clean up figure
    if normalised:
        ax.set_title("Normalised Cumulative Accuracy Profile (CAP) Curve")
        ax.set_xlabel("Proportion Classified Positive")
        ax.set_ylabel("True Positive Rate")
    else:
        ax.set_title("Cumulative Accuracy Profile (CAP) Curve")
        ax.set_xlabel("Classified Positive Count")
        ax.set_ylabel("True Positives Count")

    ax.legend(title="Model")


def get_classifier_cumulative_positive_outputs(classifier, X, y, method="predict"):
    """Running total of samples classified positive when put in decreasing order by prediction method

    :param classifier: trained sklearn binary classifier
    :param X: numpy array of input data
    :type X: np.ndarray
    :param y: numpy array of binary labels
    :type y: np.ndarray
    :param method: classifier method used to order labels ('predict' or 'predict_proba')
    :type method: str
    :return:  index is number of samples and value number of positive samples classified positive, length len(y)+1
    :rtype: np.ndarray
    """
    if method == "predict":
        classifier_output = classifier.predict(X)
    elif method == "predict_proba":
        classifier_output = classifier.predict_proba(X)
        classifier_output = classifier_output[:, 1]
    else:
        raise ValueError("method should be either 'predict' or 'predict_proba'")

    # order labels according to classifier output
    output_with_labels = pd.DataFrame(
        data={"classifier_output": classifier_output, "label": y}
    )
    output_with_labels = output_with_labels.sort_values(
        ["classifier_output", "label"], ascending=False
    )

    # calculate running total - add a 0 at the start
    cumulative_positive_outputs = output_with_labels.label.cumsum(axis=0).values
    cumulative_positive_outputs = np.concatenate(([0], cumulative_positive_outputs))

    return cumulative_positive_outputs


def get_perfect_cumulative_positive_outputs(y):
    """Running total of samples classified positive for a perfect model with labels y

    :param y: numpy array of binary labels
    :type y: np.ndarray
    :return: index is number of samples and value number of positive samples classified positive, length len(y)+1
    :rtype: np.ndarray
    """
    # order labels with 1s before 0s
    y_sorted = np.sort(y)[::-1]

    # calculate running total - add a 0 at the start
    cumulative_positive_outputs = y_sorted.cumsum()
    cumulative_positive_outputs = np.concatenate(([0], cumulative_positive_outputs))

    return cumulative_positive_outputs


def transform_cap_to_roc(cap_values):
    """Maps an array of values defining a (un-normalised) CAP curve to values defining the (un-normalised) ROC curve

    :param cap_values: (n, 2) array of x and y values defining a CAP curve
    :type cap_values: np.ndarray
    :return: (n, 2) array of x and y values defining an ROC curve
    :rtype: np.ndarray
    """
    cap_to_roc_linear_transformation = np.array([[1, -1], [0, 1]])
    roc_values = cap_values @ cap_to_roc_linear_transformation.T

    return roc_values


def transform_roc_to_cap(roc_values):
    """Maps an array of values defining a (un-normalised) ROC curve to values defining the (un-normalised) CAP curve

    :param roc_values: (n, 2) array of x and y values defining an ROC curve
    :type roc_values: np.ndarray
    :return: (n, 2) array of x and y values defining a CAP curve
    :rtype: np.ndarray
    """
    roc_to_cap_linear_transformation = np.array([[1, 1], [0, 1]])
    cap_values = roc_values @ roc_to_cap_linear_transformation.T

    return cap_values
