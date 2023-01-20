import numpy as np
import pandas as pd
from matplotlib import pyplot as plt


def plot_cumulative_accuracy_profile(classifier, X, y, method="predict", normalised=True):
    """Plot CAP for trained binary classifier

    :param classifier: trained sklearn binary classifier
    :param X: numpy array of input data
    :param y: numpy array of binary labels
    :param method: classifier method used to order labels ('predict' or 'predict_proba')
    """
    # generate cumulative accuracy data
    perfect_cumulative_accuracy = get_perfect_cumulative_accuracy(y=y, normalised=normalised)
    classifier_cumulative_accuracy = get_classifier_cumulative_accuracy(
        classifier=classifier,
        X=X,
        y=y,
        method=method, normalised=normalised
    )

    # plot curves
    fig, ax = plt.subplots()

    sample_count = len(y)
    if normalised:
        x_plot = np.linspace(0, 1, sample_count + 1)
        x_plot = x_plot[1:]
    else:
        x_plot = np.arange(1, sample_count + 1)

    ax.plot(x_plot, classifier_cumulative_accuracy, label="Classifier")
    ax.plot(x_plot, perfect_cumulative_accuracy, ls="--", label="Perfect")

    plot_random_cumulative_accuracy(y, ax=ax, normalised=normalised)

    # clean up figure
    if normalised:
        ax.set_xlabel("Proportion of Samples")
        ax.set_ylabel("Cumulative Accuracy")
    else:
        ax.set_xlabel("Samples Count")
        ax.set_ylabel("Classified Positive Count")

    ax.set_title("Cumulative Accuracy Profile (CAP)")

    ax.legend(title="Model")


def get_classifier_cumulative_accuracy(classifier, X, y, method="predict", normalised=True):
    """Cumulative accuracy for trained binary classifier

    :param classifier: trained sklearn binary classifier
    :param X: numpy array of input data
    :param y: numpy array of binary labels
    :param method: classifier method used to order labels ('predict' or 'predict_proba')
    :return: cumulative_accuracy: Series with index number of samples and value number of positive samples
    """
    if method == "predict":
        classifier_output = classifier.predict(X)
    elif method == "predict_proba":
        classifier_output = classifier.predict_proba(X)
        classifier_output = classifier_output[:, 1]
    else:
        raise ValueError("method should be either 'predict' or 'predict_proba'")

    output_with_labels = pd.DataFrame(data={"classifier_output": classifier_output, "label": y})
    output_with_labels = output_with_labels.sort_values(["classifier_output", "label"], ascending=False)

    cumulative_accuracy = output_with_labels.label.cumsum(axis=0).values

    if normalised:
        positive_sample_count = y.sum()
        return cumulative_accuracy / positive_sample_count
    else:
        return cumulative_accuracy


def get_perfect_cumulative_accuracy(y, normalised=True):
    """Cumulative accuracy for a perfect model with labels y

    :param y: numpy array of binary labels
    :return: cumulative_accuracy: Series with index number of samples and value number of positive samples
    """
    y_sorted = np.sort(y)[::-1]
    cumulative_accuracy = y_sorted.cumsum()

    if normalised:
        positive_sample_count = y.sum()
        return cumulative_accuracy / positive_sample_count
    else:
        return cumulative_accuracy


def plot_random_cumulative_accuracy(y, ax=None, normalised=True):
    """Plots expected cumulative accuracy for a random model with labels y

    :param y: numpy array of binary labels
    :param ax: matplotlib axis, if null a new plot is created
    """
    if ax is None:
        fig, ax = plt.subplots()

    if normalised:
        x_plot = [0, 1]
        y_plot = [0, 1]
    else:
        sample_count = len(y)
        positive_sample_count = y.sum()

        x_plot = [0, sample_count]
        y_plot = [0, positive_sample_count]

    ax.plot(x_plot, y_plot, ls="--", color="k", label="Random")
