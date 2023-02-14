from psycopg2 import sql
from galvanalyser.database.experiment.timeseries_data_row import (
    TEST_TIME_COLUMN_ID,
)

import numpy as np
from galvanalyser.database.experiment import (
    TimeseriesDataRow, ColumnRow
)

def select_timeseries_column(
        dataset_id, column_id, conn, max_samples=None):
    """
    Arguments
    ---------

    dataset_id: int
        id of dataset
    columns: int
        id of column to get
    sample_range: (int, int)
        length two tuple with beginnging and end sample numbers
    max_samples: int
        subsample to give an array of only max_samples
    """
    column = ColumnRow.select_from_id(column_id, conn)

    pivot_for_column = (
        'MAX(case when column_id={} then value else NULL end)'
    ).format(column.id)

    max_sample_number = (
        'SELECT MAX(sample_no) '
        'FROM experiment.timeseries_data '
        'WHERE column_id={},'
    ).format(column.id)

    if max_samples is None:
        filter_by_max_samples = ''
    else:
        filter_by_max_samples = \
            'and sample_no%(({})/2000)=0'.format(max_sample_number)

    sql = (
        'SELECT {} '
        'FROM experiment.timeseries_data '
        'WHERE column_id={} {}'
        'GROUP BY sample_no '
        'ORDER by sample_no '
    ).format(pivot_for_column, column.id,
             filter_by_max_samples)

    with conn.cursor() as cursor:
        cursor.execute(sql)
        records = cursor.fetchall()
        return np.array([r[0] for r in records])



def select_experiment_columns(dataset_id, conn):
    with conn.cursor() as cursor:
        cursor.execute(
            (
                'SELECT experiment.timeseries_data.column_id, experiment."column".name '
                "FROM experiment.timeseries_data "
                'INNER JOIN experiment."column" ON experiment.timeseries_data.column_id=experiment."column".id '
                "WHERE experiment.timeseries_data.dataset_id=%s AND experiment.timeseries_data.sample_no in "
                "(SELECT sample_no FROM experiment.timeseries_data WHERE dataset_id=%s LIMIT 1);"
            ),
            [dataset_id, dataset_id],
        )
        records = cursor.fetchall()
        return [(result[0], result[1]) for result in records]


def select_timeseries_data_record_nos_in_range(
    dataset_id, samples_from, samples_to, conn
):
    with conn.cursor("column_cursor") as cursor:
        cursor.execute(
            (
                "SELECT sample_no FROM experiment.timeseries_data "
                "WHERE dataset_id=%s AND column_id=%s AND sample_no >= %s AND sample_no < %s"
                " ORDER BY sample_no ASC"
            ),
            [
                dataset_id,
                TEST_TIME_COLUMN_ID,  # Use the test time column to get distinct sample no
                # values since it should always be there and will be
                # cheaper than SELECT DISTINCT
                samples_from,
                samples_to,
            ],
        )
        return tuple(column for column in zip(*(sample for sample in cursor)))


def select_timeseries_data_column_in_range(
    dataset_id, column_id, samples_from, samples_to, conn
):
    with conn.cursor("column_cursor") as cursor:
        cursor.execute(
            (
                "SELECT sample_no, value FROM experiment.timeseries_data "
                "WHERE dataset_id=%s AND column_id=%s AND sample_no >= %s AND sample_no < %s"
                " ORDER BY sample_no ASC"
            ),
            [dataset_id, column_id, samples_from, samples_to],
        )
        return tuple(column for column in zip(*(sample for sample in cursor)))


def select_closest_record_no_above_or_below(
    dataset_id, column_id, value, conn, below=True
):
    with conn.cursor() as cursor:
        cursor.execute(
            (
                "SELECT sample_no FROM "
                "("
                "(SELECT sample_no, value from experiment.timeseries_data"
                " WHERE dataset_id=%s AND column_id=%s AND value >= %s "
                "ORDER BY value LIMIT 1) "
                "UNION ALL "
                "(SELECT sample_no, value from experiment.timeseries_data"
                " WHERE dataset_id=%s AND column_id=%s AND value <= %s "
                "ORDER BY value DESC LIMIT 1)"
                ") as foo "
                "ORDER BY sample_no " + ("ASC" if below else "DESC") + " "
                "LIMIT 1"
            ),
            [dataset_id, column_id, value, dataset_id, column_id, value],
        )
        return cursor.fetchone()[0]


## http://aklaver.org/wordpress/2018/04/21/building-dynamic-sql-using-psycopg2/
# def select_dataset_data_columns_in_range(
#    dataset_id, columns, samples_from, samples_to, conn
# ):
#    with conn.cursor("column_cursor") as cursor:
#        query_string = sql.SQL(
#            (
#                "SELECT {} FROM experiment.timeseries_data "
#                "WHERE dataset_id={} AND sample_no >= {} AND sample_no < {}"
#                " ORDER BY sample_no ASC"
#            )
#        ).format(
#            sql.SQL(",").join(map(sql.Identifier, columns)),
#            sql.Placeholder(),
#            sql.Placeholder(),
#            sql.Placeholder(),
#        )
#        cursor.execute(query_string, [dataset_id, samples_from, samples_to])
#        return tuple(column for column in zip(*(sample for sample in cursor)))
