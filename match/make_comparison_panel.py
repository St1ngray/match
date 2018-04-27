from numpy import asarray
from pandas import DataFrame

from .information.information.compute_information_coefficient import \
    compute_information_coefficient
from .nd_array.nd_array.apply_function_on_2_2d_arrays_slices import \
    apply_function_on_2_2d_arrays_slices
from .plot.plot.plot_heat_map import plot_heat_map
from .support.support.path import establish_path


def make_comparison_panel(_2d_array_or_df_0,
                          _2d_array_or_df_1,
                          match_function=compute_information_coefficient,
                          axis=0,
                          title='Comparison Panel',
                          name_0='',
                          name_1='',
                          file_path_prefix=None):

    comparison = apply_function_on_2_2d_arrays_slices(
        asarray(_2d_array_or_df_0),
        asarray(_2d_array_or_df_1),
        match_function,
        axis=axis)

    if isinstance(_2d_array_or_df_0, DataFrame) and isinstance(
            _2d_array_or_df_1, DataFrame):

        if axis == 0:

            comparison = DataFrame(
                comparison,
                index=_2d_array_or_df_0.columns,
                columns=_2d_array_or_df_1.columns)

        elif axis == 1:

            comparison = DataFrame(
                comparison,
                index=_2d_array_or_df_0.index,
                columns=_2d_array_or_df_1.index)

    if file_path_prefix:
        establish_path(file_path_prefix, 'file')

        comparison.to_csv(
            '{}.comparison_panel.tsv'.format(file_path_prefix), sep='\t')

        html_file_path = '{}.comparison_panel.html'.format(file_path_prefix)

    else:
        html_file_path = None

    plot_heat_map(
        comparison,
        cluster=True,
        title=title,
        xaxis_title=name_1,
        yaxis_title=name_0,
        html_file_path=html_file_path)

    return comparison
