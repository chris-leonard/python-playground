import numpy as np
import pandas as pd
from matplotlib import pyplot as plt


def plot_cap_curve(classifier, X, y, method="predict", normalised=True):
    """Plot Cumulative Accuracy Profile (CAP) curve for trained binary classifier

    :param classifier: trained sklearn binary classifier
    :param X: numpy array of input data
    :param y: numpy array of binary labels
    :param method: classifier method used to order labels ('predict' or 'predict_proba')
    :param normalised: bool, should the axes be scaled to range [0, 1]
    """
    # generate cumulative positive outputs for classifier and a perfect classifier
    perfect_cumulative_positive_outputs = get_perfect_cumulative_positive_outputs(y=y)
    classifier_cumulative_positive_outputs = get_classifier_cumulative_positive_outputs(
        classifier=classifier,
        X=X,
        y=y,
        method=method
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
        ax.set_xlabel("Proportion of Samples")
        ax.set_ylabel("Proportion Classified Positive")
    else:
        ax.set_xlabel("Samples Count")
        ax.set_ylabel("Classified Positive Count")

    ax.set_title("Cumulative Accuracy Profile (CAP) Curve")

    ax.legend(title="Model")


def get_classifier_cumulative_positive_outputs(classifier, X, y, method="predict"):
    """Running total of samples classified positive when put in decreasing order by prediction method

    :param classifier: trained sklearn binary classifier
    :param X: numpy array of input data
    :param y: numpy array of binary labels
    :param method: classifier method used to order labels ('predict' or 'predict_proba')
    :return: cumulative_positive_outputs: numpy array with index number of samples and value number of positive samples
        classified positive, length len(y)+1
    """
    if method == "predict":
        classifier_output = classifier.predict(X)
    elif method == "predict_proba":
        classifier_output = classifier.predict_proba(X)
        classifier_output = classifier_output[:, 1]
    else:
        raise ValueError("method should be either 'predict' or 'predict_proba'")

    # order labels according to classifier output
    output_with_labels = pd.DataFrame(data={"classifier_output": classifier_output, "label": y})
    output_with_labels = output_with_labels.sort_values(["classifier_output", "label"], ascending=False)

    # calculate running total - add a 0 at the start
    cumulative_positive_outputs = output_with_labels.label.cumsum(axis=0).values
    cumulative_positive_outputs = np.concatenate(([0], cumulative_positive_outputs))

    return cumulative_positive_outputs


def get_perfect_cumulative_positive_outputs(y):
    """Running total of samples classified positive for a perfect model with labels y

    :param y: numpy array of binary labels
    :return: cumulative_positive_outputs: numpy array with index number of samples and value number of positive samples
        classified positive, length len(y)+1
    """
    # order labels with 1s before 0s
    y_sorted = np.sort(y)[::-1]

    # calculate running total - add a 0 at the start
    cumulative_positive_outputs = y_sorted.cumsum()
    cumulative_positive_outputs = np.concatenate(([0], cumulative_positive_outputs))

    return cumulative_positive_outputs
