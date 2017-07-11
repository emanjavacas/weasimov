
import React from 'react';
import ReactDOM from 'react-dom';
import * as RB from 'react-bootstrap';

import Utils from './Utils';


class Navbar extends React.Component {
  render() {
    return (
        <RB.Navbar>
	<RB.Navbar.Header>
	  <RB.Navbar.Brand>
            <a href="#">Ik, Asimov</a>
	    <span>
	      <Utils.NBSP size={10}/>
	      <small>{this.props.username || "loading"}</small>
	    </span>
	  </RB.Navbar.Brand>
	  <RB.Navbar.Toggle/>
	</RB.Navbar.Header>
	<RB.Navbar.Collapse>
	  <RB.Nav className="pull-right">
	    <RB.NavItem eventKey={1} href="logout">
	      <i className="fa fa-sign-out" style={{"fontSize": "25px"}}/>
	    </RB.NavItem>
	  </RB.Nav>
	</RB.Navbar.Collapse>
      </RB.Navbar>
    );
  }
}


export default Navbar;
