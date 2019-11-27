if (!window.dash_clientside) {
    window.dash_clientside = {};
}
window.dash_clientside.custom_range = {
    get_from_plot_view: function(btn_custom_range_from_view_n_clicks, graph_id, current_from_value, current_to_value) {
        if (btn_custom_range_from_view_n_clicks) {
            return document.getElementById(graph_id).layout.xaxis.range;
        }
        return [current_from_value, current_to_value];
    }

}