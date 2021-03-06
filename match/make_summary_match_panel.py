from pandas import concat

from ._check_features_index import _check_features_index
from ._make_annotations import _make_annotations
from ._match import _match
from ._process_target_or_features_for_plotting import \
    _process_target_or_features_for_plotting
from .information.information.compute_information_coefficient import \
    compute_information_coefficient
from .make_match_panel import (ANNOTATION_FONT_SIZE,
                               LAYOUT_ANNOTATION_TEMPLATE,
                               MATCH_PANEL_LAYOUT_TEMPLATE, ROW_HEIGHT)
from .plot.plot.plot_and_save import plot_and_save
from .support.support.df import drop_df_slice
from .support.support.iterable import make_object_int_mapping


def make_summary_match_panel(
        target,
        multiple_features,
        plot_only_columns_shared_by_target_and_all_features=False,
        target_ascending=False,
        min_n_sample=2,
        match_function=compute_information_coefficient,
        random_seed=20121020,
        n_sampling=0,
        n_permutation=0,
        target_type='continuous',
        plot_target_std_max=3,
        plot_features_std_max=3,
        title='Summary Match Panel',
        html_file_path=None,
        plotly_file_path=None):

    if plot_only_columns_shared_by_target_and_all_features:

        for features_dict in multiple_features.values():

            target = target.loc[target.index & features_dict['df'].columns]

    if target.dtype == 'O':

        target = target.map(make_object_int_mapping(target)[0])

    if isinstance(target_ascending, bool):

        target.sort_values(ascending=target_ascending, inplace=True)

    target, target_plot_min, target_plot_max, target_colorscale = _process_target_or_features_for_plotting(
        target, target_type, plot_target_std_max)

    target_df = target.to_frame().T

    layout = MATCH_PANEL_LAYOUT_TEMPLATE

    n_row = 1 + len(multiple_features)

    for features_dict in multiple_features.values():

        n_row += len(features_dict['indices'])

    layout.update(height=ROW_HEIGHT / 2 * max(8, n_row), title=title)

    layout_annotations = []

    row_fraction = 1 / n_row

    yaxis_name = 'yaxis{}'.format(len(multiple_features) + 1).replace(
        'axis1', 'axis')

    domain_end = 1

    domain_start = domain_end - row_fraction

    layout[yaxis_name] = dict(
        domain=(domain_start, domain_end),
        tickfont=dict(size=ANNOTATION_FONT_SIZE))

    data = [
        dict(
            yaxis=yaxis_name.replace('axis', ''),
            type='heatmap',
            z=target_df.values[::-1],
            x=target_df.columns,
            y=target_df.index[::-1],
            text=(target_df.columns, ),
            zmin=target_plot_min,
            zmax=target_plot_max,
            colorscale=target_colorscale,
            showscale=False)
    ]

    multiple_scores = []

    for features_index, (name, features_dict) in enumerate(
            multiple_features.items()):

        print('Making match panel for {} ...'.format(name))

        features = features_dict['df']

        _check_features_index(features)

        indices = features_dict['indices']

        index_aliases = features_dict['index_aliases']

        emphasis = features_dict['emphasis']

        data_type = features_dict['data_type']

        missing_indices = tuple(
            index for index in indices if index not in features.index)

        if len(missing_indices):

            raise ValueError(
                'features do not have indices {}.'.format(missing_indices))

        features = features.loc[indices]

        features = drop_df_slice(
            features[target.index], 1, min_n_not_na_unique_value=2)

        scores = _match(target.values, features.values, min_n_sample,
                        match_function, 1, None, n_sampling, n_permutation,
                        random_seed)

        scores.index = features.index

        scores.sort_values('Score', ascending=emphasis == 'low', inplace=True)

        multiple_scores.append(scores)

        features_to_plot = features.loc[scores.index]

        features_to_plot.index = features_to_plot.index.map(
            {index: alias
             for index, alias in zip(indices, index_aliases)}.get)

        annotations = _make_annotations(scores)

        features_to_plot, features_plot_min, features_plot_max, features_colorscale = _process_target_or_features_for_plotting(
            features_to_plot, data_type, plot_features_std_max)

        yaxis_name = 'yaxis{}'.format(
            len(multiple_features) - features_index).replace('axis1', 'axis')

        domain_end = domain_start - row_fraction

        domain_start = domain_end - len(
            features_dict['indices']) * row_fraction

        layout[yaxis_name] = dict(
            domain=(domain_start, domain_end),
            dtick=1,
            tickfont=dict(size=ANNOTATION_FONT_SIZE))

        data.append(
            dict(
                yaxis=yaxis_name.replace('axis', ''),
                type='heatmap',
                z=features_to_plot.values[::-1],
                x=features_to_plot.columns,
                y=features_to_plot.index[::-1],
                zmin=features_plot_min,
                zmax=features_plot_max,
                colorscale=features_colorscale,
                showscale=False))

        for annotation_index, (annotation, strs) in enumerate(
                annotations.items()):

            x = 1.008 + annotation_index / 8

            if annotation_index == 0:

                layout_annotations.append(
                    dict(
                        x=x,
                        y=1 - (row_fraction / 2),
                        text='<b>{}</b>'.format(annotation),
                        **LAYOUT_ANNOTATION_TEMPLATE))

            y = domain_end - (row_fraction / 2)

            for str_ in strs:

                layout_annotations.append(
                    dict(
                        x=x,
                        y=y,
                        text='<b>{}</b>'.format(str_),
                        **LAYOUT_ANNOTATION_TEMPLATE))

                y -= row_fraction

    layout.update(annotations=layout_annotations)

    plot_and_save(
        dict(layout=layout, data=data), html_file_path, plotly_file_path)

    return concat(multiple_scores).sort_values('Score')
