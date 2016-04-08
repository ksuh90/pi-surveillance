'use strict';
var React = require('react');
var StatusAlert = require('./StatusAlert.jsx');

/*
[props]
    app    
*/   
module.exports = React.createClass({

    render: function() {       
        var that = this;
        
        var controls = [
            {
                option: 'take_pic',
                label: 'Take picture',
                desc: 'Manually take a picture.'
            },
            {
                option: 'pause',
                label: 'Pause',
                desc: 'Briefly pause the system.'
            },
            {
                option: 'resume',
                label: 'Resume',
                desc: 'Resume paused system.'
            },
            {
                option: 'ping',
                label: 'Ping',
                desc: 'Ping the pi-surveillance system'
            }
        ];
        var rows = $.map(controls, function(row, key){
            return (
                <Control key={key} row={row} app={that.props.app} />
            );
        });
        return (
            <div>{rows}</div>
        );
    }
});


var Control = React.createClass({

    getInitialState: function() {
        return { statusComponent: ''};
    },
    componentDidMount: function() {
        var that = this;
        
        that.props.app.pubnub.subscribe({
            channel: that.props.app.pubnub_channel,
            message: function(r){
                console.log('ControlPanel : ');
                console.log(r);
                if (r.type == 'control_resp') {
                    var status = <StatusAlert status={true} msg={r.msg} />;
                    that.setState({statusComponent: status});
                    $.unblockUI();
                }
            },
            error: function (error) {
                var status = <StatusAlert status={false} msg={JSON.stringify(error)} />;
                that.setState({statusComponent: status});
                //console.log(JSON.stringify(error));
            }
        });
        
    },
    controlClick: function(option) {
        var that = this;

        console.log('remote control option: '+option);
        that.setState({statusComponent: ''});
        $.blockUI.defaults.message = '';
        $.blockUI();

        // publish control option via pubnub
        var payload = {
            type: 'control_request',
            option: option
        };
        that.props.app.pubnub.publish({
            channel: that.props.app.pubnub_channel,        
            message: payload,
            callback : function(m){
                console.log('Control : pubnub : publish :');
                console.log(m);
            }
        });    
    },
    render: function() {
        return(
            <div className="jumbotron control-slot">
                <h3>{this.props.row.label}</h3>
                <p>{this.props.row.desc}</p>
                <div className="status-container">{this.state.statusComponent}</div>
                <button
                    type="button"
                    className="btn btn-lg btn-primary btn-control"
                    onClick={this.controlClick.bind(null, this.props.row.option)}
                    data-option={this.props.row.option}>{this.props.row.label}</button>
            </div>
        );
    }
});