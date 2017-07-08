
import React from 'react';
import * as RB from 'react-bootstrap';
import {Editor, EditorState, convertFromRaw, convertToRaw} from 'draft-js';
import Moment from 'react-moment';
import jsonpatch from 'fast-json-patch';

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
      <a
	 key={docId}
	 className="list-group-item"
	 style={{cursor: "pointer"}}
	 onClick={() => onJoinRoom(docId)}>
	<h4 className="list-group-item-heading">
	  {doc.screen_name}
	  <small>
	    <span className="text-muted pull-right">
	      <Moment fromNow ago>{doc.last_modified}</Moment>
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
  const color = props.user.active? "#17d517": "#777";
  return (
    <div className="panel panel-default">
      <div className="panel-heading">
	<span className="text-muted">
	  {props.user.username}
	  <i className="pull-right fa fa-user" style={{color: color}}/>
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
    this.onLoadDoc = this.onLoadDoc.bind(this);
    this.onLoadDocSuccess = this.onLoadDocSuccess.bind(this);
    this.onLoadDocError = this.onLoadDocError.bind(this);
  }

  componentDidMount() {
    /**
     * doc_id: int
     * edit: json
     * timestamp: int
     */
    this.props.socket.on('savechange', (data) => {
      console.log('savechange', data);
      const contentState = this.state.editorState.getCurrentContent();
      const rawContent = convertToRaw(contentState);
      const newRawContent = jsonpatch.applyPatch(rawContent, data.edit);
      const newContent = convertFromRaw(newRawContent);
      this.onChange(EditorState.push(this.state.editorState, newContent));
    });
  }

  onLoadDoc(docId) { // TODO: this could be cached checking last_modified timestamps for validation
    const {user_id} = this.props.docs[docId];
    Utils.fetchDoc(docId, this.onLoadDocSuccess, this.onLoadDocError, user_id);
  }

  onLoadDocSuccess(response) {
    this.setState({
      editorState: response.contentState ?
	EditorState.createWithContent(
	  convertFromRaw(response.contentState), EditorUtils.hypDecorator) :
	EditorState.createEmpty(EditorUtils.hypDecorator)
    });
  }

  onLoadDocError(error) {
    console.log(error);
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
	<MonitorDoc
	   activeRoom={this.props.activeRoom}
	   editorState={this.state.editorState}
	   onChange={this.props.onChange}
	   onLoadDoc={this.onLoadDoc}/>
      );
    }
  }
}

export default MonitorPanel;
