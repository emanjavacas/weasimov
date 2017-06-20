import React from 'react';
import ReactDOM from 'react-dom';
import * as RB from 'react-bootstrap';
import Utils from './Utils';


class Suggestions extends React.Component {
  render() {
    const hasHyps = (this.props.hyps.length > 0);
    let hyps = [];
    for (var i=0; i<this.props.hyps.length; i++) {
      const hyp = this.props.hyps[i];
      hyps.push(
	<RB.ListGroupItem
	   key={i}
	   className="list-group-hover"
	   onClick={() => this.props.onHypSelect(hyp)}>
          {hyp.text}
	  <RB.Label className="pull-right">{hyp.score}</RB.Label>
        </RB.ListGroupItem>
      );
    }
    if (this.props.loadingHyps) {
      return <Utils.Spinner/>;
    } else {
      return (
	<div className="panel panel-info" style={{visibility: hasHyps ? "visible" : "hidden"}}>
	  <div className="panel-heading">
	    <p>Suggestions
	      <span className="pull-right">
		<RB.Button
		   onClick={this.props.onRegenerate}
		   bsSize="small">
		  <i className="fa fa-refresh"/>
		</RB.Button>
	      </span>
	    </p>
	  </div>
	  <RB.ListGroup>{hyps}</RB.ListGroup>
	</div>
      );
    }
  }
}

export default Suggestions;










