"use strict";

var graph_state = {};
var graph_traces = [];
var all_experiment_data = new Map();//new datarange.ExperimentData();

goog.require('proto.galvanalyser.DataRanges');
goog.require('datarange');

if (!window.dash_clientside) {
    window.dash_clientside = {};
}
window.dash_clientside.clientside_graph = {
    update_graph_trigger: function(data) {
        for (const row of data) {
            let foo = new datarange.ExperimentData();

            let oReq = new XMLHttpRequest();
            oReq.open("GET", `/experiment/${row.experiment}/data?from=${row.samples_from}&to=${row.samples_to}&columns=test_time,volts,amps`, true);
            oReq.responseType = "arraybuffer";

            oReq.onload = function(oEvent) {
                let arrayBuffer = oReq.response; // Note: not oReq.responseText
                if (arrayBuffer) {
                    //var byteArray = new Uint8Array(arrayBuffer);
                    let message = proto.galvanalyser.DataRanges.deserializeBinary(arrayBuffer);
                    let ranges_list = message.getRangesList();
                    let experment_id = message.getExperimentId();
                    if(! all_experiment_data.has(experment_id)){
                        all_experiment_data.set(experment_id, new datarange.ExperimentData());
                    }
                    let experiment_data = all_experiment_data.get(experment_id);
                    ranges_list.forEach(function(range){
                        experiment_data.add_protobuf_data_range(range);
                    });
                    console.log(ranges_list);
                    ranges_list.forEach(function(range){
                        let volt_list = range.getVoltsList();
                        let data_name = `${message.getExperimentId()}_${range.getStartSampleNo()}_${volt_list.length}_volts`;
                        if (!(data_name in graph_state)) {
                            alert("Adding data plot")
                            let trace = {
                                x: range.getTestTimeList(),
                                y: volt_list,
                                mode: 'markers',
                                type: 'scattergl'
                            };
                            graph_state[data_name] = trace;
                            Plotly.addTraces(plot, trace);
                        } else {
                            alert("Not adding data plot");
                        }
                    });
                    
                    //if (!('dataplot' in graph_state)) {
                    //    alert("Adding data plot")
                    //    let trace1 = {
                    //        x: ranges_list[0].getTestTimeList(),
                    //        y: ranges_list[0].getVoltsList(),
                    //        mode: 'markers',
                    //        type: 'scattergl'
                    //    };
                    //    graph_state.dataplot = trace1;
                    //    Plotly.addTraces(plot, trace1);
                    //} else {
                    //    alert("Not adding data plot");
                    //}
                }
            };

            oReq.send(null);
        }

        let plot = document.getElementById('main-graph');

        for (const current_trace of graph_traces) {
            //console.log(val);
            // if(! (current_trace['id'] in data_ids)) -- we need to make a list of ids
        }

        //if (!('first' in graph_state)) {
        //    alert("Adding plot")
        //    let trace1 = {
        //        x: [1, 2, 3, 4],
        //        y: [10, 15, 13, 17],
        //        mode: 'markers',
        //        type: 'scattergl'
        //    };
        //    graph_state.first = trace1;
        //    Plotly.addTraces(plot, trace1);
        //} else {
        //    alert("Not adding plot");
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