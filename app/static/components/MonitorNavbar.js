
import React from 'react';
import ReactDOM from 'react-dom';
import * as RB from 'react-bootstrap';


class MonitorNavbar extends React.Component {
  render() {
    return (
      <RB.Navbar inverse>
	<RB.Navbar.Header>
	  <RB.Navbar.Brand>
            <a href="#">AsiBot</a>
	  </RB.Navbar.Brand>
	  <RB.Navbar.Toggle/>
	</RB.Navbar.Header>
	<RB.Navbar.Collapse>
	  <RB.Nav>
	    <RB.NavItem>
	      Monitor Panel
	    </RB.NavItem>
	  </RB.Nav>
	  <RB.Nav pullRight>
	    <RB.NavItem eventKey={1}>
	      {(this.props.activeRoom !== null) ?
		<i className="fa fa-home" style={{fontSize: "20px"}} onClick={this.props.onLeaveRoom}/> :
		<span/>}
	    </RB.NavItem>
	    <RB.NavItem eventKey={1} href="index">
	      <i className="fa fa-sign-out" style={{fontSize: "20px"}}/>
	    </RB.NavItem>
	  </RB.Nav>
	</RB.Navbar.Collapse>
      </RB.Navbar>
    );
  }
}

export default MonitorNavbar;
