import React from 'react';
import ReactDOM from 'react-dom';
import * as RB from 'react-bootstrap';

import io from 'socket.io-client';
let socket = io(window.location.host);


class Monitor extends React.Component {
  constructor(props) {
    super(props);
    this.state = {init: false};
  }

  componentDidMount() {
    
  }

  render() {
    return (
      <RB.Grid fluid>
	<RB.Row>
	  <RB.Col lg={2} md={2} sm={1}></RB.Col>
	  <RB.Col lg={8} md={8} sm={10}>
	    Stuff
	  </RB.Col>
	  <RB.Col lg={2} md={2} sm={1}></RB.Col>
	</RB.Row>	
      </RB.Grid>
    );
  }
}

ReactDOM.render(<Monitor/>, document.getElementById('app'));
