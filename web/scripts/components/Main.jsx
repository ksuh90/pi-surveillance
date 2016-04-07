'use strict';
var React = require('react');
var ReactDOM = require('react-dom');
var Nav = require('./Nav.jsx');
var Log = require('./Log.jsx');
var ControlPanel = require('./ControlPanel.jsx');


var Content = React.createClass({

    getInitialState: function() {
        return {
            app: this.props.app
        };
    },
    render: function() {
        var label = this.props.currentNav.label;
        return(
            <div className="col-sm-9 col-sm-offset-3 col-md-10 col-md-offset-2 main">
                <h1 className="page-header">{label}</h1>
                {this.props.currentNav.component}
            </div>
        );
    }
});

var Container = React.createClass({

    getInitialState: function() {
        return {
            app: this.props.app,
            currentNavKey: 'log'
        };
    },
    componentDidMount: function() {
              
    },
    handleNavClick: function(navKey) {
        this.setState({
            currentNavKey: navKey
        });
    },
    render: function() {
        var props = {
            app: this.state.app,
        };
        var nav = {
            log: {
                component: <Log {...props} />,
                label    : 'Log'
            },
            controlPanel: {
                component: <ControlPanel {...props} />,
                label    : 'Control Panel'
            }
        };
        return(
            <div>
                <nav className="navbar navbar-inverse navbar-fixed-top">
                    <div className="container-fluid">
                        <div className="navbar-header">
                            <button type="button" className="navbar-toggle collapsed" data-toggle="collapse" data-target="#navbar" aria-expanded="false" aria-controls="navbar">
                                <span className="sr-only">Toggle navigation</span>
                                <span className="icon-bar"></span>
                                <span className="icon-bar"></span>
                                <span className="icon-bar"></span>
                            </button>
                            <a className="navbar-brand" href="#">{"pi-surveillance"}</a>
                        </div>
                        <div id="navbar" className="navbar-collapse collapse">
                            <Nav
                                classNames={"nav navbar-nav navbar-right"}
                                nav={nav}
                                currentNavKey={this.state.currentNavKey}
                                onNavClick={this.handleNavClick} />
                        </div>
                    </div>
                </nav>

                <div className="container-fluid">
                    <div className="row">
                        <div className="col-sm-3 col-md-2 sidebar">
                            <Nav
                                classNames={"nav nav-sidebar"}
                                nav={nav}
                                currentNavKey={this.state.currentNavKey}
                                onNavClick={this.handleNavClick} />
                        </div>
                        <Content
                            currentNav={nav[this.state.currentNavKey]}
                            app={this.state.app} />                        
                    </div>
                </div>
            </div>
        );
    }
});


// Initialize APP object
var APP = window.APP || {};
APP.pubnub = PUBNUB.init({
    publish_key: APP.pubnub_pub_key,
    subscribe_key: APP.pubnub_sub_key,
    ssl : (('https:' == document.location.protocol) ? true : false),
    error: function (error) {
        console.log('Error:', error);
    }
});  

// Entry point
ReactDOM.render(
    <Container app={APP} />,
    document.getElementById('container')
);