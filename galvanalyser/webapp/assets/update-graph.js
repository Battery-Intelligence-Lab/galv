"use strict";

var graph_state = new Map();
var requested_graph_state = new Map();
var graph_traces = [];
var all_experiment_data = new Map();
var experiment_data_requested_from_server = new Map(); //new datarange.ExperimentData();

const x_axis_column_name = "test_time";

goog.require('proto.galvanalyser.DataRanges');
goog.require('datarange');

function graph_substate_same_column(a, b) {
    return a.experiment == b.experiment &&
        a.column == b.column;
}

function graph_substate_equal(a, b) {
    return a.experiment == b.experiment &&
        a.column == b.column &&
        a.samples_from == b.samples_from &&
        a.samples_to == b.samples_to;
}

/**
 * Send request to server for data, update requested data
 * @param {int} experiment_id 
 * @param {string} column 
 * @param {int} start_sample_no 
 * @param {int} end_sample_no 
 */
function send_data_request(experiment_id, column, start_sample_no, end_sample_no) {
    //console.log(`send_data_request Requesting ${experiment_id} , ${column} , ${start_sample_no} , ${end_sample_no}`);
    let oReq = new XMLHttpRequest();
    oReq.open("GET", `/experiment/${experiment_id}/data?column=${column}&from=${start_sample_no}&to=${end_sample_no}`, true);
    oReq.responseType = "arraybuffer";

    oReq.onload = function(oEvent) {
        let arrayBuffer = oReq.response; // Note: not oReq.responseText
        if (arrayBuffer) {
            //var byteArray = new Uint8Array(arrayBuffer);
            let message = proto.galvanalyser.DataRanges.deserializeBinary(arrayBuffer);
            let ranges_list = message.getRangesList();
            let received_experiment_id = message.getExperimentId();
            let received_column = message.getColumn();
            //console.log(`send_data_request Received ${received_experiment_id} , ${column}`);
            if (!all_experiment_data.has(received_experiment_id)) {
                all_experiment_data.set(received_experiment_id, new datarange.ExperimentData());
            }
            let experiment_data = all_experiment_data.get(received_experiment_id);
            ranges_list.forEach(function(range) {
                experiment_data.add_protobuf_data_range(received_column, range);
            });
            update_graph();
        }
    };
    oReq.send(null);
    // update requested data
    if (!experiment_data_requested_from_server.has(experiment_id)) {
        experiment_data_requested_from_server.set(experiment_id, new datarange.ExperimentData());
    }
    let requested_experiment_data = experiment_data_requested_from_server.get(experiment_id);
    requested_experiment_data.add_empty_data_range(column, start_sample_no, end_sample_no);
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
 * @param {int} experiment_id 
 * @param {string} column 
 * @param {int} start_sample_no 
 * @param {int} end_sample_no 
 */
function request_experiment_data(experiment_id, column, start_sample_no, end_sample_no) {
    //console.log(`request_experiment_data start ${experiment_id} , ${column} , ${start_sample_no} , ${end_sample_no}`);
    //check we haven't requested this data already
    if (!experiment_data_requested_from_server.has(experiment_id)) {
        // we don't have any data for this experiment, get it all.
        //console.log(`request_experiment_data have no ${experiment_id}`);
        send_data_request(experiment_id, column, start_sample_no, end_sample_no);
        return true;
    }
    let requested_experiment_data = experiment_data_requested_from_server.get(experiment_id);
    if (!requested_experiment_data.columns.has(column)) {
        // we don't have any data for this column, get it all.
        //console.log(`request_experiment_data has no ${experiment_id} , ${column}`);
        send_data_request(experiment_id, column, start_sample_no, end_sample_no);
        return true;
    }
    let requested_column_data = requested_experiment_data.columns.get(column);
    let missing_data_ranges = get_list_of_missing_ranges(requested_column_data, start_sample_no, end_sample_no);
    let data_requested = false;
    for (const missing_range of missing_data_ranges) {
        //console.log(`request_experiment_data has missing range ${experiment_id} , ${column} , ${missing_range.from} , ${missing_range.to}`);
        send_data_request(experiment_id, column, missing_range.from, missing_range.to);
        data_requested = true;
    }
    //console.log(`request_experiment_data data_requested: ${data_requested}`);
    return data_requested;
}

function update_graph() {
    // Add or update new plots
    let updates_requested = false;
    for (const [requested_experiment_id, requested_experiment_data] of requested_graph_state) {
        //console.log(`update_graph iterating ${requested_experiment_id}`);
        for (const [column, reading_data] of requested_experiment_data.columns) {
            //console.log(`update_graph iterating ${requested_experiment_id} , ${column}`);
            reading_data.iterate_ranges(function(data_range) {
                // get the sample times and requested data
                updates_requested |= request_experiment_data(requested_experiment_id, x_axis_column_name, data_range.from, data_range.to);
                updates_requested |= request_experiment_data(requested_experiment_id, column, data_range.from, data_range.to);
            });
        }
    }

    if (!updates_requested) {
        //console.log(`update_graph attempting to plot`);
        let plot = document.getElementById('main-graph');
        //update graph
        let traces = [];
        for (const [requested_experiment_id, requested_experiment_data] of requested_graph_state) {
            if (all_experiment_data.has(requested_experiment_id)) {
                let available_experiment_data = all_experiment_data.get(requested_experiment_id);
                if (!available_experiment_data.columns.has(x_axis_column_name)) {
                    //console.log(`update_graph NO X-AXIS ${requested_experiment_id}`);
                    // no x axis, can't plot
                    continue;
                }
                let sample_time_data = available_experiment_data.columns.get(x_axis_column_name);
                for (const [requested_column_name, requested_reading_data] of requested_experiment_data.columns) {
                    let y_ranges = [];
                    let x_ranges = [];
                    if (available_experiment_data.columns.has(requested_column_name)) {
                        let available_column_reading_data = available_experiment_data.columns.get(requested_column_name);
                        requested_reading_data.iterate_ranges(function(requested_data_range) {
                            let available_y_ranges = available_column_reading_data.get_ranges_between(requested_data_range.from, requested_data_range.to);
                            for (const available_y_range of available_y_ranges) {
                                let available_x_ranges = sample_time_data.get_ranges_between(available_y_range.from, available_y_range.to);
                                for (const available_x_range of available_x_ranges) {
                                    y_ranges.push(available_y_range.get_subset(available_x_range.from, available_x_range.to));
                                    x_ranges.push(available_x_range);
                                }
                            }
                        });
                    }
                    let fuse_data = function(data_range_array) {
                        let data = new Array(0);
                        for (const data_range of data_range_array) {
                            data = data.concat(data_range.data_values);
                        }
                        return data;
                    };
                    let x_data = fuse_data(x_ranges);
                    let y_data = fuse_data(y_ranges);
                    let trace = {
                        x: x_data,
                        y: y_data,
                        mode: 'markers',
                        type: 'scattergl',
                        marker: {size:2},
                        name: `${requested_experiment_id} ${requested_column_name}`
                    };
                    traces.push(trace);
                }
            } else {
                //console.log(`update_graph NO DATA for ${requested_experiment_id}`);
            }
        }
        Plotly.react(plot, traces);
    }
}

if (!window.dash_clientside) {
    window.dash_clientside = {};
}
window.dash_clientside.clientside_graph = {
    update_graph_trigger: function(data) {
        let new_config = new Map();
        for (const row of data) {
            if (!new_config.has(row.experiment_id)) {
                new_config.set(row.experiment_id, new datarange.ExperimentData());
            }
            let experiment_data = new_config.get(row.experiment_id);
            experiment_data.add_empty_data_range(row.column, row.samples_from, row.samples_to);
            //console.log(`update_graph_trigger wants ${row.experiment_id} , ${row.column} , ${row.samples_from} , ${row.samples_to}`);
        }
        requested_graph_state = new_config;
        update_graph();
        //for (const row of data) {
        //    let foo = new datarange.ExperimentData();
        //
        //    let oReq = new XMLHttpRequest();
        //    //oReq.open("GET", `/experiment/${row.experiment}/data?from=${row.samples_from}&to=${row.samples_to}&column=test_time,volts,amps`, true);
        //    oReq.open("GET", `/experiment/${row.experiment}/data?from=${row.samples_from}&to=${row.samples_to}&column=${row.column}`, true);
        //    oReq.responseType = "arraybuffer";
        //
        //    oReq.onload = function(oEvent) {
        //        let arrayBuffer = oReq.response; // Note: not oReq.responseText
        //        if (arrayBuffer) {
        //            //var byteArray = new Uint8Array(arrayBuffer);
        //            let message = proto.galvanalyser.DataRanges.deserializeBinary(arrayBuffer);
        //            let ranges_list = message.getRangesList();
        //            let experiment_id = message.getExperimentId();
        //            //if(! all_experiment_data.has(experiment_id)){
        //            //    all_experiment_data.set(experiment_id, new datarange.ExperimentData());
        //            //}
        //            //let experiment_data = all_experiment_data.get(experiment_id);
        //            //ranges_list.forEach(function(range){
        //            //    experiment_data.add_protobuf_data_range(range);
        //            //});
        //            ////console.log(ranges_list);
        //            //ranges_list.forEach(function(range){
        //            //    let volt_list = range.getVoltsList();
        //            //    let data_name = `${message.getExperimentId()}_${range.getStartSampleNo()}_${volt_list.length}_volts`;
        //            //    if (!(data_name in graph_state)) {
        //            //        alert("Adding data plot")
        //            //        let trace = {
        //            //            x: range.getTestTimeList(),
        //            //            y: volt_list,
        //            //            mode: 'markers',
        //            //            type: 'scattergl'
        //            //        };
        //            //        graph_state[data_name] = trace;
        //            //        Plotly.addTraces(plot, trace);
        //            //    } else {
        //            //        alert("Not adding data plot");
        //            //    }
        //            //});
        //            
        //            //if (!('dataplot' in graph_state)) {
        //            //    alert("Adding data plot")
        //            //    let trace1 = {
        //            //        x: ranges_list[0].getTestTimeList(),
        //            //        y: ranges_list[0].getVoltsList(),
        //            //        mode: 'markers',
        //            //        type: 'scattergl'
        //            //    };
        //            //    graph_state.dataplot = trace1;
        //            //    Plotly.addTraces(plot, trace1);
        //            //} else {
        //            //    alert("Not adding data plot");
        //            //}
        //        }
        //    };
        //
        //    oReq.send(null);
        //}
        //
        //let plot = document.getElementById('main-graph');
        //
        //for (const current_trace of graph_traces) {
        //    ////console.log(val);
        //    // if(! (current_trace['id'] in data_ids)) -- we need to make a list of ids
        //}

        //if (!('first' in graph_state)) {
        //    alert("Adding plot")
        //    let trace1 = [{
        //        x: [1, 2, 3, 4],
        //        y: [10, 15, 13, 17],
        //        mode: 'markers',
        //        type: 'scattergl'
        //    }];
        //    graph_state.first = trace1;
        //    Plotly.react(plot, trace1);
        //} else {
        //    alert("Updating plot");
        //    let traces = [{
        //        x: [1, 2, 3, 4],
        //        y: [-10, 15, -13, 17],
        //        mode: 'markers',
        //        type: 'scattergl'
        //    },
        //    {
        //        x: [1, 2, 3, 4],
        //        y: [15, 10, -3, 7],
        //        mode: 'markers',
        //        type: 'scattergl'
        //    }];
        //    if(Math.random() < 0.5){
        //        traces = [traces[1]];
        //    }
        //    //graph_state.first = trace1;
        //    Plotly.react(plot, traces);
        //}
        return "";
    },
    login_refresh: function(children) {
        if (children.includes("Success")) {
            location.reload(true);
        }
        return "";
    }

};