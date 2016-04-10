'use strict';
var React = require('react');

module.exports = React.createClass({
    statusClass: function() {
        var classes = '';
        if (this.props.status) {
            classes = 'alert-success';
        } else {
            classes = 'alert-danger';
        }
        return 'alert status ' + classes;
    },
    render: function() {
        return (
            <div className={this.statusClass()} role="alert">
                <strong>{this.props.msg}</strong>
            </div>
        );
    }
});