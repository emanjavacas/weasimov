
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
    this.togglecredits = () => {
      $("body").removeClass("menu");
      $("body").toggleClass("credits");
    }
    this.togglehelp = () => {
      $("body").removeClass("menu");
      $("body").toggleClass("help");
    }
    this.togglemenu = () => {
      $("body").toggleClass("menu");
    }
    this.toggleasibot = () => {
      $("body").toggleClass("asibotopen");
    }
    this.onSelectDoc = (docId) => {
      if (docId === this.props.activeDoc) { // don't do anything if selecting same doc
        this.toggleDropdown(false);
            } else {
        this.props.onSelectDoc(docId);
        this.toggleDropdown(false);
      }
    };
  }

  

  render() {
    return (
      <div id="navbar">
        <RB.Button className="menutoggle" onClick={this.togglemenu}>MENU</RB.Button>
        <RB.Button onClick={this.toggleasibot} className="asibotsuggesties right">
            AsiBot suggesties
            <i className="fa fa-caret-right" style={{fontSize: "16px"}}/>
          </RB.Button>
        <div id="burgerfold">
          <RB.Button className="mobilehide">Asibot</RB.Button>
          <RB.Button onClick={this.togglecredits}>credits</RB.Button>
          <RB.Button onClick={this.togglehelp}>help</RB.Button>
          <RB.Button className="mobilehide right" href={(this.props.isMonitor) ? "/monitor" : null}>
            {this.props.username || "loading"}
          </RB.Button>
          <RB.Button href="https://www.ad.nl/binnenland/schrijfwedstrijd-iedereen-maakt-kans-dankzij-robot~ae88229b/" target="_blank" className="right">schrijfwedstrijd</RB.Button>
          <RB.Button href="logout" className="right">uitloggen</RB.Button>
        </div>
      </div>
    );
  }
}


export default Navbar;
