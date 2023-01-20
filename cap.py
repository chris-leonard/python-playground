import numpy as np
import pandas as pd
from matplotlib import pyplot as plt


def plot_cumulative_accuracy_profile(classifier, X, y, method="predict"):
    """Plot CAP for trained binary classifier

    :param classifier: trained sklearn binary classifier
    :param X: numpy array of input data
    :param y: numpy array of binary labels
    :param method: classifier method used to order labels ('predict' or 'predict_proba')
    """
    # generate cumulative accuracy data
    perfect_cumulative_accuracy = get_perfect_cumulative_accuracy(y=y)
    classifier_cumulative_accuracy = get_classifier_cumulative_accuracy(
        classifier=classifier,
        X=X,
        y=y,
        method=method
    )

    # plot curves
    fig, ax = plt.subplots()

    ax.plot(classifier_cumulative_accuracy, label="Classifier")
    ax.plot(perfect_cumulative_accuracy, ls="--", label="Perfect")
    plot_random_cumulative_accuracy(y, ax=ax)

    # clean figure
    ax.set_xlabel("Samples Count")
    ax.set_ylabel("Classified Positive Count")

    ax.set_title("Cumulative Accuracy Profile (CAP)")

    ax.legend(title="Model")


def get_classifier_cumulative_accuracy(classifier, X, y, method="predict"):
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

    cumulative_accuracy = output_with_labels.label.cumsum(axis=0).reset_index(drop=True)

    return cumulative_accuracy


def get_perfect_cumulative_accuracy(y):
    """Cumulative accuracy for a perfect model with labels y

    :param y: numpy array of binary labels
    :return: cumulative_accuracy: Series with index number of samples and value number of positive samples
    """
    y_sorted = np.sort(y)[::-1]
    cumulative_accuracy = y_sorted.cumsum()

    return cumulative_accuracy


def plot_random_cumulative_accuracy(y, ax=None):
    """Plots expected cumulative accuracy for a random model with labels y

    :param y: numpy array of binary labels
    :param ax: matplotlib axis, if null a new plot is created
    """
    if ax is None:
        fig, ax = plt.subplots()

    sample_count = len(y)
    positive_sample_count = y.sum()

    x_rand = [0, sample_count]
    y_rand = [0, positive_sample_count]

    ax.plot(x_rand, y_rand, ls="--", color="k", label="Random")
