
import React from 'react';
import ReactDOM from 'react-dom';
import * as RB from 'react-bootstrap';
import Moment from 'react-moment';

import Utils from './Utils';


function DocItem(props) {
  return (
    <RB.MenuItem
       active={props.doc.id === props.activeDoc}
       style={{marginBottom: "0px", width:"320px"}}
       onClick={() => props.onSelectDoc(props.doc.id)}>
      {props.doc.screen_name}
      <Moment className="pull-right" fromNow ago >{props.doc.last_modified}</Moment>
    </RB.MenuItem>
  );
}


function makeDocItems(docs, activeDoc, onSelectDoc) {
  const docItems = [];
  const docIds = Object.keys(docs);
  for (var i=0; i<docIds.length; i++) {
    const docId = docIds[i], doc = docs[docId];
    docItems.push(
      <DocItem
         key={docId}
	 eventKey={docId}
	 doc={doc}
	 activeDoc={activeDoc}
	 onSelectDoc={onSelectDoc}>
      </DocItem>
    );
  }
  return docItems;
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
	<RB.Form inline>
	  <RB.FormGroup>
            <RB.FormControl
	       ref="input"
	       type="text"
	       placeholder="Enter a new name"
	       defaultValue={this.props.screenName}
         onKeyPress={(e) => {(e.key === 'Enter' ? this.onSaveScreenName() : null)}}/>
	    <RB.Button
	      onClick={() => this.onSaveScreenName()}
	      style={{margin: "0 16px"}}>
	      Save
	    </RB.Button>
          </RB.FormGroup>
	</RB.Form>
      ) : (
	<RB.Button onClick={() => this.toggleEditing(true)}>
	  <span >{this.props.screenName}</span>
	</RB.Button>
      );
  }
}


class NewDocModal extends React.Component {
  constructor(props) {
    super(props);
    this.onNewDoc = this.onNewDoc.bind(this);
    this.getInputValue = () => ReactDOM.findDOMNode(this.refs.newDocInput).value;
  }

  onNewDoc() {
    const value = this.getInputValue();
    if (value) {
      this.props.onSubmit(value);
      this.props.close();
    }
  }

  render() {
    return (
      <RB.Modal className="document-form" show={this.props.show} onHide={this.props.close}>
        <RB.Modal.Body >
          <RB.Form inline> 
            <RB.FormGroup controlId="newDoc">
              <RB.FormControl
                 ref="newDocInput"
                 type="text"
                 placeholder="Enter a name"/>
            </RB.FormGroup>
            <RB.Button className="pull-right" onClick={this.onNewDoc}>Create</RB.Button>
          </RB.Form>
      	</RB.Modal.Body>
      </RB.Modal>
    );
  }
}


class RemoveDocModal extends React.Component {
  constructor(props) {
    super(props);
    this.onRemoveDoc = this.onRemoveDoc.bind(this);
  }

  onRemoveDoc() {
    this.props.onSubmit(this.props.doc.id);
    this.props.close();
  }

  render() {
    return (
      <RB.Modal show={this.props.show} onHide={this.props.close}>
	<RB.Modal.Header>
        <RB.Modal.Title>
	  <p>Weet je zeker dat je het document "{this.props.doc.screen_name}" wilt verwijderen?</p>
      	</RB.Modal.Title>
	</RB.Modal.Header>
	<RB.Modal.Footer>
	  <RB.Button bsStyle="danger" onClick={this.onRemoveDoc}>
	    Ja, gooi weg!
	  </RB.Button>
	  <RB.Button bsStyle="primary" onClick={this.props.close}>
	    Nee, ik heb me bedacht!
	  </RB.Button>
	</RB.Modal.Footer>
      </RB.Modal>
    );
  }
}


class Navbar extends React.Component {
  constructor(props) {
    super(props);
    this.state = {
      showNewDocModal: false,
      showRemoveDocModal: false,
      dropdownOpen: false
    };
    this.toggleNewDocModal = () => this.setState({showNewDocModal: !this.state.showNewDocModal});
    this.toggleRemoveDocModal = () => {
      if (Object.keys(this.props.docs).length === 1) {
	console.log("This is your last doc, you can't remove it");
	return;
      }
      this.setState({showRemoveDocModal: !this.state.showRemoveDocModal});
    };
    this.toggleDropdown = (newValue) => {
      this.setState({
	dropdownOpen: (newValue === null) ? !this.state.dropdownOpen : newValue
      });
    };
    this.onSelectDoc = (docId) => {
      if (docId === this.props.activeDoc) { // don't do anything if selecting same doc
	this.toggleDropdown(false);
      } else {
	this.props.onSelectDoc(docId);
      }
    };
  }

  render() {
    return (
      <RB.Navbar>
	<NewDocModal
	   show={this.state.showNewDocModal}
	   close={this.toggleNewDocModal}
	   onSubmit={this.props.onSubmitNewDoc}/>
	<RemoveDocModal
	   show={this.state.showRemoveDocModal}
	   close={this.toggleRemoveDocModal}
	   doc={this.props.docs[this.props.activeDoc]}
	   onSubmit={this.props.onSubmitRemoveDoc}/>
	<RB.Navbar.Header>
	  <RB.Navbar.Brand>
            <a href="./">AsiBot</a>
	  </RB.Navbar.Brand>
	  <RB.Navbar.Toggle/>
	</RB.Navbar.Header>
	<RB.Navbar.Collapse>
	  <RB.ButtonGroup style={{marginTop:"7px", display: "inline-flex"}}>
	    <ScreenNameInput
	       screenName={this.props.docs[this.props.activeDoc].screen_name}
	       onSubmit={this.props.onSubmitScreenName}/>
	    <RB.DropdownButton
	       title=" "
	       id="nav-dropdown"
	       open={this.state.dropdownOpen}
	       onToggle={this.toggleDropdown}
	       style={{zIndex: 9999999}}
	       pullRight>
	      {makeDocItems(this.props.docs, this.props.activeDoc, this.onSelectDoc)}
	    </RB.DropdownButton>
	    <RB.Button onClick={this.toggleNewDocModal}>
	      <i className="fa fa-file" style={{fontSize: "16px"}}/>
	    </RB.Button>
	    <RB.Button onClick={this.toggleRemoveDocModal}>
	      <i className="fa fa-trash-o" style={{fontSize: "16px"}}/>
	    </RB.Button>
	  </RB.ButtonGroup>
	  <RB.ButtonGroup className="pull-right" style={{marginTop:"7px"}}>
	    <RB.Button href={(this.props.isMonitor) ? "/monitor" : null}>
	      {this.props.username || "loading"}
            </RB.Button>
	    <RB.Button href="logout">
	      <i className="fa fa-sign-out" style={{fontSize: "16px"}}/>
            </RB.Button>
	  </RB.ButtonGroup>
	</RB.Navbar.Collapse>
      </RB.Navbar>
    );
  }
}


export default Navbar;
