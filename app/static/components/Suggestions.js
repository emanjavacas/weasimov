import React from 'react';
import ReactDOM from 'react-dom';
import * as RB from 'react-bootstrap';


class Suggestions extends React.Component {
  render() {
    return (
      <RB.Panel header="Suggestion">
	<RB.ListGroup>
	  <RB.ListGroupItem>Hello</RB.ListGroupItem>
	</RB.ListGroup>
      </RB.Panel>
    );
  }	
};


export default Suggestions;

	// <div id="hyps-toolbar" class="panel panel-default" style="visibility: hidden">
	//   <div class="panel-heading">Suggestions</div>
	//   <ul id="hyps-panel" class="list-group list-group-hover">
	//   </ul>
	// </div>
