
import React from 'react';
import ReactDOM from 'react-dom';
import * as RB from 'react-bootstrap';

import Utils from './Utils';


function DocItem(props) {
  return (
    <RB.MenuItem
       eventKey={props.doc.id}
       active={props.doc.id === props.activeDoc}
       onClick={() => props.onClick(props.doc.id)}>
      {props.doc.screen_name}
    </RB.MenuItem>
  );
}


class ScreenNameInput extends React.Component {
  constructor(props) {
    super(props);
    this.state = {
      inputState: props.screenName,
      editing: false
    };
    this.onSaveScreenName = this.onSaveScreenName.bind(this);
    this.getInputValue = () => ReactDOM.findDOMNode(this.refs.input).value;
  }

  toggleEditing(newValue) {
    if (newValue === null) {
      this.setState({editing: !this.state.editing});
    } else {
      this.setState({editing: newValue});
    }
  }

  onSaveScreenName() {
    const newName = this.getInputValue();
    if (newName) {
      this.props.onSubmit(newName);
      this.toggleEditing(false);
    }
  }

  render() {
    return this.state.editing ?
      (
	<RB.Navbar.Form pullLeft>
	  <RB.FormGroup>
            <RB.FormControl
	       ref="input"
	       type="text"
	       placeholder="Enter a new name"
	       defaultValue={this.props.screenName}/>
          </RB.FormGroup>
	  <Utils.NBSP size={2}/>
          <RB.Button onClick={() => this.onSaveScreenName()}>Save</RB.Button>
	</RB.Navbar.Form>
      ) : (
	<RB.Nav>
	  <RB.NavItem>
	    <span onClick={() => this.toggleEditing(true)}>{this.props.screenName}</span>
	  </RB.NavItem>
	</RB.Nav>
      );
  }
}


class Navbar extends React.Component {
  render() {
    return (
        <RB.Navbar>
	  <RB.Navbar.Header>
	    <RB.Navbar.Brand>
              <a href="#">AsiBot</a>
	    </RB.Navbar.Brand>
	    <RB.Navbar.Toggle/>
	  </RB.Navbar.Header>
	  <RB.Navbar.Collapse>
	    <RB.Nav>
	      <RB.NavItem>
		{this.props.username || "loading"}
	      </RB.NavItem>
	    </RB.Nav>
	    <ScreenNameInput
	       screenName={this.props.docs[this.props.activeDoc].screen_name}
	       onSubmit={this.props.onSubmitScreenName}/>
	    <RB.Nav className="pull-right">
	      <RB.NavDropdown title="Documents" id="nav-dropdown" style={{zIndex: 10000}}>
		{Object.keys(this.props.docs).map((key) => {
		  return (
		    <DocItem
		       key={key}
		       doc={this.props.docs[key]}
		       activeDoc={this.props.activeDoc}
		       onClick={this.props.onSelectDoc}>
		    </DocItem>
		  );
		})}
              </RB.NavDropdown>
             <RB.NavItem eventKey={2} onClick={this.props.onNewDoc}>
               <i className="fa fa-plus-square" style={{fontSize: "20px"}}/>
             </RB.NavItem>
	     <RB.NavItem eventKey={3} href="logout">
	       <i className="fa fa-sign-out" style={{fontSize: "20px"}}/>
	     </RB.NavItem>
	   </RB.Nav>
	 </RB.Navbar.Collapse>
       </RB.Navbar>
    );
  }
}


export default Navbar;
