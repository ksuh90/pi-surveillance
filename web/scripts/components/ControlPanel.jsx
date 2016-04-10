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
                label: 'Take picture',
                desc: 'Manually take a picture.',
                buttons: [
                    {
                        option: 'take_pic',
                        label: 'Take picture'
                    }
                ]
            },
            {
                label: 'Pause/Resume',
                desc: 'Pause/Resume the system.',
                buttons: [
                    {
                        option: 'pause',
                        label: 'Pause'
                    },
                    {
                        option: 'resume',
                        label: 'Resume'
                    }
                ]
            },
            {
                label: 'Email Notifications',
                desc: 'Toggle email notifications',
                buttons: [
                    {
                        option: 'email_on',
                        label: 'On'
                    },
                    {
                        option: 'email_off',
                        label: 'Off'
                    }
                ]

            },
            {
                label: 'Ping',
                desc: 'Ping the pi-surveillance system',
                buttons: [
                    {
                        option: 'ping',
                        label: 'Ping'
                    }
                ]
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
    controlRequest: function(payload) {
        // publish control option via pubnub
        var that = this;
        that.props.app.pubnub.publish({
            channel: that.props.app.pubnub_channel,
            message: payload,
            callback : function(m){
                console.log('Control : pubnub : publish :');
                console.log(m);
            }
        });
    },
    controlClick: function(option) {
        var that = this;
        console.log('remote control option: '+option);
        this.setState({statusComponent: ''});
        $.blockUI.defaults.message = '';
        $.blockUI();

        this.controlRequest({
            type: 'control_request',
            option: option
        });
    },
    render: function() {
        var that = this;
        that.props.app.pubnub.subscribe({
            channel: that.props.app.pubnub_channel,
            message: function(r){
                console.log('ControlPanel: ');
                console.log(r);
                if (r.type == 'control_resp') {
                    var status = <StatusAlert status={true} msg={r.msg} />;
                    that.setState({statusComponent: status});
                }
                $.unblockUI();
            },
            error: function (error) {
                var status = <StatusAlert status={false} msg={JSON.stringify(error)} />;
                that.setState({statusComponent: status});
                $.unblockUI();
                //console.log(JSON.stringify(error));
            }
        });

        var buttons = $.map(this.props.row.buttons, function(button, key){
            return (
                <ControlButton key={key} btnData={button} controlClick={that.controlClick} />
            );
        });

        return(
            <div className="jumbotron control-slot">
                <h3>{this.props.row.label}</h3>
                <p>{this.props.row.desc}</p>
                <div className="status-container">{this.state.statusComponent}</div>
                {buttons}
            </div>
        );
    }
});

var ControlButton = React.createClass({
    render: function() {
        return(
            <button
                type="button"
                className="btn btn-lg btn-primary btn-control"
                onClick={this.props.controlClick.bind(null, this.props.btnData.option)}
                data-option={this.props.btnData.option}>{this.props.btnData.label}</button>
        );
    }
});