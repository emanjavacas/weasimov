
import React from 'react';
import * as RB from 'react-bootstrap';
import {Editor, EditorState, RichUtils} from 'draft-js';

import Utils from './Utils';
import EditorUtils from './EditorUtils';
import MonitorUtils from './MonitorUtils';
import MonitorDoc from './MonitorDoc';


function makeUserDocs(docs, onJoinRoom) {
  const userDocs = [];
  const docIds = Object.keys(docs);
  for (var i=0; i<docIds.length; i++) {
    const docId = docIds[i], doc = docs[docId];
    userDocs.push(
      <a key={docId} className="list-group-item" onClick={() => onJoinRoom(docId)}>
	<h4 className="list-group-item-heading">
	  {doc.screen_name}
	  <small>
	    <span className="pull-right text-muted">
	      {Utils.timestampToHuman(doc.last_modified)}
	    </span>
	  </small>
	</h4>
	<p className="list-group-item-text">{doc.snippet}...</p>
      </a>
    );
  }
  return userDocs;
}


function UserPanel(props) {
  return (
    <div className="panel panel-default">
      <div className="panel-heading">
	<span className="text-muted">
	  {props.user.username}
	  <i className="pull-right fa fa-user" style={{color: props.user.active? "green": "auto"}}/>
	</span>
      </div>
      <div className="panel-body">
	<div className="list-group">
	  {makeUserDocs(props.docs, props.onJoinRoom)}
         </div>
      </div>
    </div>
  );
}


function OverviewPanel(props) {
  return (
    <RB.PanelGroup>
      {Object.keys(props.users).map((userId) => {
	const user = props.users[userId];
	return (
	  <UserPanel
	     key={userId}
	     onJoinRoom={props.onJoinRoom}
	     user={user}
	     docs={MonitorUtils.filterDocs(props.docs, user.id)}/>
	);
      })}
    </RB.PanelGroup>
  );
}


class MonitorPanel extends React.Component {
  constructor(props) {
    super(props);
    this.state = {
      editorState: EditorState.createEmpty(EditorUtils.hypDecorator)
    };
    this.onChange = this.onChange.bind(this);
  }

  componentDidMount() {
    // listen to savechanges on active room
  }

  onChange(editorState) {
    this.setState({editorState});
  }
  
  render() {
    if (this.props.activeRoom === null) {
      return (
	<OverviewPanel
	   users={this.props.users}
	   docs={this.props.docs}
	   onJoinRoom={this.props.onJoinRoom}/>
      );
    } else {
      return (
	<MonitorDoc editorState={this.state.editorState} onChange={this.props.onChange}/>
      );
    }
  }
}

export default MonitorPanel;
