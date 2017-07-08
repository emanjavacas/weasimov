
import React from 'react';
import ReactDOM from 'react-dom';
import * as RB from 'react-bootstrap';
import io from 'socket.io-client';

import MonitorPanel from './MonitorPanel';
import MonitorUtils from './MonitorUtils';
import MonitorNavbar from './MonitorNavbar';
import Utils from './Utils';


const socket = io(window.location.host + "/monitor");


class Monitor extends React.Component {
  constructor(props) {
    super(props);
    this.state = {init: false};
    // functions
    this.onInitSuccess = this.onInitSuccess.bind(this);
    this.onInitError = (error) => console.log(error);
    this.joinRoom = this.joinRoom.bind(this);
    this.leaveRoom = this.leaveRoom.bind(this);
  }

  componentDidMount() {
    MonitorUtils.monitorInit(this.onInitSuccess, this.onInitError);
    /**
     * user_id: int
     */
    socket.on('login', (data) => {
      console.log('login');
      this.setState({
	users: {
	  ...this.state.users,
	  [data.user_id]: {
	    ...this.state.users[data.user_id],
	    active: true
	  }
	}
      });
    });
    /**
     * user_id: int
     */
    socket.on('logout', (data) => {
      console.log('logout');
      this.setState({
	users: {
	  ...this.state.users,
	  [data.user_id]: {
	    ...this.state.users[data.user_id],
	    active: false
	  }
	}
      });
    });
    /**
     * id: int
     * user_id: int
     * screen_name: str
     * last_modified: int
     * timestamp: int
     * snippet: str
     */
    socket.on('createdoc', (data) => {
      console.log('createdoc', data);
      const {docs} = this.state;
      docs[data.id] = data;
      this.setState({docs: docs});
    });
    /**
     * doc_id: int
     */
    socket.on('removedoc', (data) => {
      console.log('removedoc', data);
      const {docs} = this.state;
      delete docs[data.doc_id];
      this.setState({docs: docs});
    });
    /**
     * doc_id: id
     * screen_name: str
     * timestamp: int
     */
    socket.on('editdocname', (data) => {
      console.log('editdocname', data);
      this.setState({
	docs: {
	  ...this.state.docs,
	  [data.doc_id]: {
	    ...this.state.docs[data.doc_id],
	    screen_name: data.screen_name
	  }
	}
      });
    });
  }

  onInitSuccess(response) {
    this.setState({
      init: true,
      activeRoom: null,
      users: MonitorUtils.normalizeUsers(response.users),
      docs: MonitorUtils.normalizeDocs(response.docs)
    });
  }

  joinRoom(docId) {
    socket.emit('join', {'room': docId});
    this.setState({activeRoom: docId});
  }

  leaveRoom() {
    socket.emit('leave', {'room': this.state.activeRoom});
    this.setState({activeRoom: null});
  }

  render() {
    if (!this.state.init) {
      return <Utils.LoadingApp/>;
    } else {
      return (
	<div>
	  <MonitorNavbar
	     activeRoom={this.state.activeRoom}
	     activeDoc={this.state.docs[this.state.activeRoom]}
	     onLeaveRoom={this.leaveRoom}/>
	  <RB.Grid fluid>
	    <RB.Row>
	      <RB.Col lg={2} md={2} sm={1}></RB.Col>
	      <RB.Col lg={8} md={8} sm={10}>
		<MonitorPanel
                   users={this.state.users}
                   docs={this.state.docs}
                   socket={socket}
                   activeRoom={this.state.activeRoom}
                   onJoinRoom={this.joinRoom}
                   onLeaveRoom={this.leaveRoom}/>
	      </RB.Col>
	      <RB.Col lg={2} md={2} sm={1}></RB.Col>
	    </RB.Row>	
	  </RB.Grid>
	</div>
      );
    }
  }
}

ReactDOM.render(<Monitor/>, document.getElementById('app'));
