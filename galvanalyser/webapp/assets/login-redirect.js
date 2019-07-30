if (!window.dash_clientside) {
    window.dash_clientside = {};
}
window.dash_clientside.clientside_login = {
    redirect: function(href) {
        if (href) {
            window.history.pushState({}, '', href);
            const evt = document.createEvent('CustomEvent');
            evt.initCustomEvent(
                'onpushstate',
                false,
                false,
                undefined
            );
            window.dispatchEvent(evt);
        }
        return href;
    },
    login_refresh: function(children) {
        if (children.includes("Success")) {
            location.reload(true);
        }
        return "";
    }

}