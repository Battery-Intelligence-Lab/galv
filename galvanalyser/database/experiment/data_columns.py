from psycopg2 import sql
import galvanalyser.harvester.battery_exceptions as battery_exceptions


# http://aklaver.org/wordpress/2018/04/21/building-dynamic-sql-using-psycopg2/
def select_dataset_data_columns_in_range(
    dataset_id, columns, samples_from, samples_to, conn
):
    with conn.cursor("column_cursor") as cursor:
        query_string = sql.SQL(
            (
                "SELECT {} FROM experiment.data "
                "WHERE dataset_id={} AND sample_no >= {} AND sample_no < {}"
                " ORDER BY sample_no ASC"
            )
        ).format(
            sql.SQL(",").join(map(sql.Identifier, columns)),
            sql.Placeholder(),
            sql.Placeholder(),
            sql.Placeholder(),
        )
        cursor.execute(query_string, [dataset_id, samples_from, samples_to])
        return tuple(column for column in zip(*(sample for sample in cursor)))
