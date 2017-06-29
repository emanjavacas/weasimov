import React from 'react';

const Spinner = (props) => (
  <div className="text-center" style={{"fontSize": "18px"}}>
    <span className="loading dots"></span>
  </div>);

const Spacer = (props) => <div className="row" style={{height: props.height}}></div>;

const Utils = {
  Spinner: Spinner,
  Spacer: Spacer
};

export default Utils;
