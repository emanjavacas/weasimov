
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
    // listen to login, logout, createdoc...
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
    // join room
    this.setState({activeRoom: docId});
  }

  leaveRoom() {
    // leave room
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
