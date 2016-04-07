'use strict';
var React = require('react');

/*
[props]
    app
*/   
module.exports = React.createClass({

    getInitialState: function() {
        return {
            log: null,
        };
    },
    componentDidMount: function() {
        var that = this;
        this.serverRequest = $.ajax({
            url         : that.props.app.url.api,
            type        : 'POST',
            dataType    : 'json',
            data        : {option:'get_log'},

            success: function(r) {
                console.log(r);
                that.setState({log: r.log});
            }.bind(this)
        });

        that.props.app.pubnub.subscribe({
            channel: that.props.app.pubnub_channel,
            message: function(r){
                console.log('Log : pubnub : subscribe :');
                console.log(r);
                // only process when response is a document
                if (r.type == 'doc') {
                    var currLog = that.state.log;
                    currLog.unshift(r.doc);
                    that.setState({log: currLog});
                }
            },
            error: function (error) {
              // Handle error here
              console.log(JSON.stringify(error));
            }
         });
    },
    componentWillUnmount: function() {
        this.serverRequest.abort();
    },
    render: function() {
        var that = this;

        if (!that.state.log) return null;

        var rows = $.map(that.state.log, function(v, k){
            return(
                <LogRow doc={v} key={k} app={that.props.app} />
            );
        });

        return (
            <div className="log">
                {rows}
            </div>
        );
    }
});

var LogRow = React.createClass({

    render: function() {
        var doc = this.props.doc;
        var src = this.props.app.url.img + 'id=' + doc._id + '&f=' + doc.filename;
        var type = doc.manual ? 'manual' : 'pi';
        var rowClass = "row placeholders "+type;
        var colClass = "col-sm-4 col-xs-12 placeholder vcenter";

        return(
            <div className={rowClass}>
                <div className={colClass}>
                    <a href={src} target="_blank">
                        <img className="img-responsive" src={src} />
                    </a>
                </div>
                <div className={colClass}>
                    {doc.timestamp}<br />{"(UTC)"}
                </div>
                <div className={colClass}>
                    {type}
                </div>
            </div>
        );
    }
});