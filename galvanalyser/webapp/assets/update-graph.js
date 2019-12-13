"use strict";

var requested_metadata_ranges = new Map();
var requested_graph_ranges = new Map();
var graph_traces = [];
var all_dataset_data = new Map();
var dataset_data_requested_from_server = new Map(); //new datarange.DatasetData();
var column_names = new Map();

const x_axis_column_id = 1; // Test Time

goog.require('proto.galvanalyser.DataRanges');
goog.require('datarange');

function graph_substate_same_column(a, b) {
    return a.dataset == b.dataset &&
        a.column == b.column;
}

function graph_substate_equal(a, b) {
    return a.dataset == b.dataset &&
        a.column == b.column &&
        a.samples_from == b.samples_from &&
        a.samples_to == b.samples_to;
}

/**
 * Send request to server for data, update requested data
 * @param {int} dataset_id 
 * @param {int} column_id 
 * @param {int} start_sample_no 
 * @param {int} end_sample_no 
 */
function send_data_request(dataset_id, column_id, start_sample_no, end_sample_no) {
    //console.log(`send_data_request Requesting ${dataset_id} , ${column_id} , ${start_sample_no} , ${end_sample_no}`);
    let oReq = new XMLHttpRequest();
    oReq.open("GET", `/dataset/${dataset_id}/data?column_id=${column_id}&from=${start_sample_no}&to=${end_sample_no}`, true);
    oReq.responseType = "arraybuffer";

    oReq.onload = function(oEvent) {
        let arrayBuffer = oReq.response; // Note: not oReq.responseText
        if (arrayBuffer) {
            //var byteArray = new Uint8Array(arrayBuffer);
            let message = proto.galvanalyser.DataRanges.deserializeBinary(arrayBuffer);
            let ranges_list = message.getRangesList();
            let received_dataset_id = message.getDatasetId();
            let received_column_id = message.getColumnId();
            //console.log(`send_data_request Received ${received_dataset_id} , ${column_id}`);
            if (!all_dataset_data.has(received_dataset_id)) {
                all_dataset_data.set(received_dataset_id, new datarange.DatasetData());
            }
            let dataset_data = all_dataset_data.get(received_dataset_id);
            ranges_list.forEach(function(range) {
                dataset_data.add_protobuf_data_range(received_column_id, range);
            });
            update_graph();
        }
    };
    oReq.send(null);
    // update requested data
    if (!dataset_data_requested_from_server.has(dataset_id)) {
        dataset_data_requested_from_server.set(dataset_id, new datarange.DatasetData());
    }
    let requested_dataset_data = dataset_data_requested_from_server.get(dataset_id);
    requested_dataset_data.add_empty_data_range(column_id, start_sample_no, end_sample_no);
}

/**
 * Get a list of ranges made by subtracting the ranges in the reading_data from
 * the requested range start_sample_no to end_sample_no
 * @param {ReadingData} reading_data 
 * @param {int} start_sample_no 
 * @param {int} end_sample_no 
 */
function get_list_of_missing_ranges(reading_data, start_sample_no, end_sample_no) {
    let available_ranges = [];
    reading_data.iterate_ranges_from(function(data_range) {
        // if start is beyond end stop iteration
        if (data_range.from >= end_sample_no) {
            return true;
        }
        available_ranges.push(data_range);
        return data_range.to >= end_sample_no;
    }, start_sample_no);
    let missing_ranges = [];
    if (available_ranges.length == 0 || available_ranges[0].from >= end_sample_no) {
        missing_ranges.push(new datarange.DataRange(start_sample_no, end_sample_no));
    }
    let missing_start = NaN;
    for (let i = 0; i < available_ranges.length; ++i) {
        let current_range = available_ranges[i];
        if (i == 0) {
            if (current_range.from > start_sample_no) {
                // first element starts inside requested range
                missing_ranges.push(new datarange.DataRange(start_sample_no, current_range.from));
            }
        }
        if (!isNaN(missing_start)) {
            //we are in a missing block, end the missing block
            missing_ranges.push(new datarange.DataRange(missing_start, Math.min(end_sample_no, current_range.from)));
            missing_start = NaN;
        }
        if (isNaN(missing_start)) {
            if (current_range.to < end_sample_no) {
                //this range ends in the requested range
                missing_start = current_range.to;
            }
        }
    }
    if (!isNaN(missing_start)) {
        //we are in a missing block, end the missing block
        missing_ranges.push(new datarange.DataRange(missing_start, end_sample_no));
    }
    return missing_ranges;
}

/**
 * Check if we have already sent a request for data, send requests for parts not already requested.
 * Returns true if a request for data was sent
 * @param {int} dataset_id 
 * @param {int} column_id 
 * @param {int} start_sample_no 
 * @param {int} end_sample_no 
 */
function request_dataset_data(dataset_id, column_id, start_sample_no, end_sample_no) {
    //console.log(`request_dataset_data start ${dataset_id} , ${column_id} , ${start_sample_no} , ${end_sample_no}`);
    //check we haven't requested this data already
    if (!dataset_data_requested_from_server.has(dataset_id)) {
        // we don't have any data for this dataset, get it all.
        //console.log(`request_dataset_data have no ${dataset_id}`);
        send_data_request(dataset_id, column_id, start_sample_no, end_sample_no);
        return true;
    }
    let requested_dataset_data = dataset_data_requested_from_server.get(dataset_id);
    if (!requested_dataset_data.columns.has(column_id)) {
        // we don't have any data for this column, get it all.
        //console.log(`request_dataset_data has no ${dataset_id} , ${column_id}`);
        send_data_request(dataset_id, column_id, start_sample_no, end_sample_no);
        return true;
    }
    let requested_column_data = requested_dataset_data.columns.get(column_id);
    let missing_data_ranges = get_list_of_missing_ranges(requested_column_data, start_sample_no, end_sample_no);
    let data_requested = false;
    for (const missing_range of missing_data_ranges) {
        //console.log(`request_dataset_data has missing range ${dataset_id} , ${column} , ${missing_range.from} , ${missing_range.to}`);
        send_data_request(dataset_id, column_id, missing_range.from, missing_range.to);
        data_requested = true;
    }
    //console.log(`request_dataset_data data_requested: ${data_requested}`);
    return data_requested;
}

function apply_offset(data, offset) {
    if (offset == 0.0) {
        return data;
    }
    return data.map(x => x + offset);
}

function update_graph() {
    // Add or update new plots
    let updates_requested = false;
    for (const [requested_dataset_id, requested_dataset_data] of requested_graph_ranges) {
        //console.log(`update_graph iterating ${requested_dataset_id}`);
        for (const [column_id, reading_data] of requested_dataset_data.columns) {
            //console.log(`update_graph iterating ${requested_dataset_id} , ${column_id}`);
            reading_data.iterate_ranges(function(data_range) {
                // get the sample times and requested data
                updates_requested |= request_dataset_data(requested_dataset_id, x_axis_column_id, data_range.from, data_range.to);
                updates_requested |= request_dataset_data(requested_dataset_id, column_id, data_range.from, data_range.to);
            });
        }
    }

    if (!updates_requested) {
        //console.log(`update_graph attempting to plot`);
        let plot = document.getElementById('main-graph');
        //update graph
        let traces = [];
        let legend_entries = [];
        for (const [requested_dataset_id, requested_dataset_data] of requested_metadata_ranges) {
            if (all_dataset_data.has(requested_dataset_id)) {
                let available_dataset_data = all_dataset_data.get(requested_dataset_id);
                if (!available_dataset_data.columns.has(x_axis_column_id)) {
                    //console.log(`update_graph NO X-AXIS ${requested_dataset_id}`);
                    // no x axis, can't plot
                    continue;
                }
                let sample_time_data = available_dataset_data.columns.get(x_axis_column_id);
                for (const [requested_column_id, requested_reading_data] of requested_dataset_data) {
                    let y_ranges = [];
                    let x_ranges = [];
                    let colour = '#000000';
                    if (available_dataset_data.columns.has(requested_column_id)) {
                        let available_column_reading_data = available_dataset_data.columns.get(requested_column_id);
                        for (const requested_data_range of requested_reading_data) {
                            colour = requested_data_range.colour;
                            let legend_entry_id = `${requested_dataset_id}_${requested_column_id}_${requested_data_range.from}_${requested_data_range.to}`
                            legend_entries.push({
                                legend_entry_id: legend_entry_id,
                                range_name: `${requested_dataset_id} ${column_names.get(requested_column_id)}`,
                                dataset_id: requested_dataset_id,
                                column_id: requested_column_id,
                                column_name: column_names.get(requested_column_id),
                                requested_data_range: requested_data_range
                            });
                            let available_y_ranges = available_column_reading_data.get_ranges_between(requested_data_range.from, requested_data_range.to);
                            for (const available_y_range of available_y_ranges) {
                                let available_x_ranges = sample_time_data.get_ranges_between(available_y_range.from, available_y_range.to);
                                for (const available_x_range of available_x_ranges) {
                                    y_ranges.push(available_y_range.get_subset(available_x_range.from, available_x_range.to).data_values);
                                    x_ranges.push(apply_offset(available_x_range.data_values, requested_data_range.offset)); // apply offset from requested_data_range here
                                }
                            }
                        }
                    } else {
                        continue;
                    }
                    let fuse_data = function(data_range_values_array) {
                        let data = new Array(0);
                        for (const data_range_values of data_range_values_array) {
                            if (data.length > 0) {
                                // Insert dummy data values to make plotly split the lines on gaps between data
                                data.push(null);
                            }
                            data = data.concat(data_range_values);
                        }
                        return data;
                    };
                    let x_data = fuse_data(x_ranges);
                    let y_data = fuse_data(y_ranges);
                    let trace = {
                        x: x_data,
                        y: y_data,
                        mode: 'lines',
                        type: 'scattergl',
                        name: `${requested_dataset_id} ${column_names.get(requested_column_id)}`,
                        line: {
                            color: colour
                        },
                    };
                    traces.push(trace);
                }
            } else {
                //console.log(`update_graph NO DATA for ${requested_dataset_id}`);
            }
        }
        Plotly.react(plot, traces);
        if (window.legend_update_callback) {
            window.legend_update_callback(legend_entries);
        }
    }
}

if (!window.dash_clientside) {
    window.dash_clientside = {};
}
window.dash_clientside.clientside_graph = {
    update_graph_trigger: function(data) {
        let new_config = new Map();
        let new_dataset_ranges = new Map();
        for (const row of data) {
            column_names.set(row.column_id, row.column);
            if (!new_config.has(row.dataset_id)) {
                new_config.set(row.dataset_id, new datarange.DatasetData());
                new_dataset_ranges.set(row.dataset_id, new Map());
            }
            let dataset_data = new_config.get(row.dataset_id);
            dataset_data.add_empty_data_range(row.column_id, row.samples_from, row.samples_to);
            let dataset_ranges = new_dataset_ranges.get(row.dataset_id);
            if (!dataset_ranges.has(row.column_id)) {
                dataset_ranges.set(row.column_id, []);
            }
            dataset_ranges.get(row.column_id).push({
                name: row.label_name,
                range_id: row.id,
                from: row.samples_from,
                to: row.samples_to,
                from_value: row.start_time,
                to_value: row.end_time,
                offset: row.offset || 0.0,
                colour: row.colour || '0x0000FF',
            });
            //console.log(`update_graph_trigger wants ${row.dataset_id} , ${row.column} , ${row.samples_from} , ${row.samples_to}`);
        }
        requested_graph_ranges = new_config;
        requested_metadata_ranges = new_dataset_ranges;
        update_graph();

        return "";
    },
    login_refresh: function(children) {
        if (children.includes("Success")) {
            location.reload(true);
        }
        return "";
    }

};