if (!window.dash_clientside) {
    window.dash_clientside = {};
}
window.dash_clientside.plot_export = {
    export_plot: function(btn_export_n_clicks, graph_id, format, width, height, scale, filename) {
        if(btn_export_n_clicks){
            Plotly.downloadImage(document.getElementById(graph_id),
            {
                format: format,
                width: Math.ceil(width),
                height: Math.ceil(height),
                scale: Number(scale),
                filename: filename
            });
        }
        return "";
    }

}