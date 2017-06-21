
import React from 'react';
import ReactDOM from 'react-dom';
import * as RB from 'react-bootstrap';


class Navbar extends React.Component {
  render() {
    return (
        <RB.Navbar>
	<RB.Navbar.Header>
	  <RB.Navbar.Brand>
            <a href="#">Ik, Asimov</a>
	  </RB.Navbar.Brand>
	</RB.Navbar.Header>
	<RB.Nav className="pull-right">
	  <RB.NavItem eventKey={1} href="#">
	    <i className="fa fa-sign-out" style={{"fontSize": "25px"}}/>
	  </RB.NavItem>
	</RB.Nav>
      </RB.Navbar>
    );
  }
}


export default Navbar;
