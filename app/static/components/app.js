import React from 'react';
import ReactDOM from 'react-dom';

import ButtonToolbar from './ButtonToolbar';
import TextEditor from './TextEditor';
import Suggestions from './Suggestions';
import Spacer from './utils';


const Header = () => <h1>Ik, Asimov</h1>;

const App = function(props) {
    return (
      <div className="container-fluid">
	<div className="row">
          <div className="col-md-2"></div>
          <div className="col-md-8">
	    <div className="row"><Header/></div>
            <Spacer height="15px"/>
            <div className="row"><ButtonToolbar/></div>
	    <Spacer height="15px"/>
	    <div className="row"><TextEditor/></div>
	    <div className="row"><Suggestions/></div>
	  </div>
	  <div className="col-md-2"></div>
	</div>
      </div>
    );
};

ReactDOM.render(<App/>, document.getElementById('app'));

