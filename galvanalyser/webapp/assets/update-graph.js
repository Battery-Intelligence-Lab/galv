"use strict";

var graph_state = new Map();
var requested_graph_state = new Map();
var graph_traces = [];
var all_experiment_data = new Map();
var requested_experiment_data = new Map();//new datarange.ExperimentData();

goog.require('proto.galvanalyser.DataRanges');
goog.require('datarange');

function graph_substate_same_column(a, b){
    return a.experiment == b.experiment &&
            a.column == b.column;
}

function graph_substate_equal(a, b){
    return a.experiment == b.experiment &&
            a.column == b.column &&
            a.samples_from == b.samples_from &&
            a.samples_to == b.samples_to;
}

function update_graph(){
    /*
    for each requested graph state:
        if state already satisfied:
            pass
        elif already have data:
            add or update graph traces
        elif already fetching data:
            pass
        else:
            request data
    */
    // Add or update new plots
    let updates_requested = false;
    for (const row of requested_graph_state) {

    }

    if(!updates_requested){
        let plot = document.getElementById('main-graph');
        //update graph
        let traces = [{
                    x: [1, 2, 3, 4],
                    y: [-10, 15, -13, 17],
                    mode: 'markers',
                    type: 'scattergl'
                },
                {
                    x: [1, 2, 3, 4],
                    y: [15, 10, -3, 7],
                    mode: 'markers',
                    type: 'scattergl'
                }];
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
            if(! new_config.has(row.experment_id)){
                new_config.set(row.experment_id, new datarange.ExperimentData());
            }
            let experiment_data = new_config.get(row.experment_id);
            experiment_data.add_empty_data_range(row.column, row.samples_from, row.samples_to);
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
        //            let experment_id = message.getExperimentId();
        //            //if(! all_experiment_data.has(experment_id)){
        //            //    all_experiment_data.set(experment_id, new datarange.ExperimentData());
        //            //}
        //            //let experiment_data = all_experiment_data.get(experment_id);
        //            //ranges_list.forEach(function(range){
        //            //    experiment_data.add_protobuf_data_range(range);
        //            //});
        //            //console.log(ranges_list);
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
        //    //console.log(val);
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