"use strict"
var graph_state = {};
var graph_traces = [];

goog.require('proto.galvanalyser.DataMessage');

if(!window.dash_clientside) {window.dash_clientside = {};}
window.dash_clientside.clientside_graph = {
  update_graph_trigger: function (data) {
    

    var oReq = new XMLHttpRequest();
    oReq.open("GET", "/data-server/data", true);
    oReq.responseType = "arraybuffer";

    oReq.onload = function (oEvent) {
      var arrayBuffer = oReq.response; // Note: not oReq.responseText
      if (arrayBuffer) {
        var message = proto.galvanalyser.DataMessage.deserializeBinary(arrayBuffer);//new proto.galvanalyser.DataMessage(arrayBuffer);
        console.log(message.getDataList());
        //var byteArray = new Uint8Array(arrayBuffer);
        //for (var i = 0; i < byteArray.byteLength; i++) {
        //  // do something with each byte in the array
        //}
      }
    };

    oReq.send(null);

      let plot = document.getElementById('main-graph');

      for (const current_trace of graph_traces) {
        //console.log(val);
        // if(! (current_trace['id'] in data_ids)) -- we need to make a list of ids
      }

      if(!('first' in graph_state)){
        alert("Adding plot")
        let trace1 = {
          x: [1, 2, 3, 4],
          y: [10, 15, 13, 17],
          mode: 'markers',
          type: 'scatter'
        };
        graph_state.first = trace1;
        Plotly.addTraces(plot, trace1);
      } else {
        alert("Not adding plot");
      }
      return "";
    },
    login_refresh: function (children) {
      if(children.includes("Success")){
        location.reload(true);
      }
      return "";
    }

}