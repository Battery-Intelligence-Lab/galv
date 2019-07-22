if(!window.dash_clientside) {window.dash_clientside = {};}
window.dash_clientside.clientside_graph = {
  update_graph_trigger: function (data) {
      alert(data);
      return "";
    },
    login_refresh: function (children) {
      if(children.includes("Success")){
        location.reload(true);
      }
      return "";
    }

}