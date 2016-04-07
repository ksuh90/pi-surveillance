'use strict';
var React = require('react');

module.exports = React.createClass({
    statusClass: function() {
        if (this.props.status) {
            return 'alert alert-success status';
        } else {
            return 'alert alert-danger status';
        }
    },
    render: function() {
        return (
            <div className={this.statusClass} role="alert">
                <strong>{this.props.msg}</strong>
            </div>
        );
    }
});