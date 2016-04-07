'use strict';
var React = require('react');

/*
[props]
    nav
    currentNavKey
    onNavClick
*/   
module.exports = React.createClass({  

    render: function() {

        var that = this;
        var navList = $.map(this.props.nav, function(v, k){

            var active = (k == that.props.currentNavKey) ? 'active' : '';
            return (
                <li key={k} className={active}>
                    <NavLink
                        navKey={k}
                        navValue={v}
                        onNavClick={that.props.onNavClick} />
                </li>
            );
        });

        return (
            <ul className={that.props.classNames}>
                {navList}
            </ul>
        );
    }
});

var NavLink = React.createClass({
    handleClick: function(e) {
        e.preventDefault();
        this.props.onNavClick(this.props.navKey);
        return;
    },
    render: function() {
        return (
            <a href="javascript:;" onClick={this.handleClick}>
                {this.props.navValue.label}
            </a>
        );
    }
});
