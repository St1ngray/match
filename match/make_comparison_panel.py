from numpy import array
from pandas import DataFrame

from .array_nd.array_nd.array_2d import apply_2
from .information.information.information import \
    compute_information_coefficient
from .plot.plot.plot import plot_clustermap
from .plot.plot.style import FIGURE_SIZE


def make_comparison_panel(array_2d_0,
                          array_2d_1,
                          function=compute_information_coefficient,
                          axis=0,
                          figure_size=FIGURE_SIZE,
                          annotate='auto',
                          title=None,
                          array_2d_0_name='',
                          array_2d_1_name='',
                          file_path_prefix=None):
    """
    Compare array_2d_0 and array_2d_1 slices and plot the result as clustermap.
    Arguments:
        array_2d_0 (array | DataFrame):
        array_2d_1 (array | DataFrame):
        function (callable):
        axis (int): 0 | 1
        figure_size (tuple):
        annotate (str | bool): whether to show values on the clustermap 'auto' |
            True | False
        title (str): plot title
        array_2d_0_name (str): array_2d_0 name
        array_2d_1_name (str): array_2d_1 name
        file_path_prefix (str): file_path_prefix.comparison_panel.txt and
            file_path_prefix.comparison_panel.png will be saved
    Returns:
        array | DataFrame:
    """

    comparison = apply_2(
        array(array_2d_1), array(array_2d_0), function, axis=axis)

    if isinstance(array_2d_0, DataFrame):

        if axis == 0:
            comparison = DataFrame(
                comparison,
                index=array_2d_1.columns,
                columns=array_2d_0.columns)

        elif axis == 1:
            comparison = DataFrame(
                comparison, index=array_2d_1.index, columns=array_2d_0.index)

    if file_path_prefix:
        comparison.to_csv(
            '{}.comparison_panel.txt'.format(file_path_prefix), sep='\t')
        plot_file_path = '{}.comparison_panel.png'.format(file_path_prefix)
    else:
        plot_file_path = None

    plot_clustermap(
        comparison,
        figure_size=figure_size,
        annotate=annotate,
        title=title,
        xlabel=array_2d_0_name,
        ylabel=array_2d_1_name,
        file_path=plot_file_path)

    return comparison
