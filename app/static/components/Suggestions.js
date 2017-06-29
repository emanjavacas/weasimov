import React from 'react';
import ReactDOM from 'react-dom';
import * as RB from 'react-bootstrap';
import Utils from './Utils';
import { CSSTransitionGroup } from 'react-transition-group';


function makeHypItems(hyps, models, onHypSelect, onHypDismiss) {
  let hypItems = [];
  for (var i=0; i<hyps.length; i++) {
    const hyp = hyps[i];
    const {r, g, b} = Utils.getModelData(models, hyp.model).color;
    const backgroundColor = `rgb(${r},${g},${b})`;
    // const backgroundColor = 'gray';
    hypItems.push(
      <RB.ListGroupItem
	 key={i}
	 className="list-group-hover"
	 onClick={() => onHypSelect(hyp)}
         style={{backgroundColor: backgroundColor}}
	>
        <RB.Table style={{marginBottom:"0"}} responsive>
	  <tbody>
	    <tr>
	      <td>
		<RB.Button
		   style={{border: "none", padding: "0", background: "none"}}
		   onClick={(e) => {e.stopPropagation(); onHypDismiss(hyp.generation_id);}}>
		  <i className="fa fa-close fa-fw" style={{color:"#666666"}}></i>
		</RB.Button>
	      </td>
	      <td style={{padding:"0px 10px 0px 20px"}}>
		{hyp.text}
	      </td>
	      <td>
		<RB.Label className="pull-right">{hyp.score}</RB.Label>
	      </td>
	    </tr>
	  </tbody>
	</RB.Table>
      </RB.ListGroupItem>
    );
  }
  return hypItems;
}


class Suggestions extends React.Component {

  render() {
    const hasHyps = (this.props.hyps.length > 0);
    const isCollapsed = this.props.isCollapsed || !hasHyps;
    if (this.props.loadingHyps) {
      return <Utils.Spinner/>;
    } else {
      return (
	<div className="panel panel-default suggestions-panel" style={{visibility: hasHyps ? "visible" : "hidden"}}>
	  <div className="panel-heading">
            <RB.Button bsSize="sm">
              <i className="fa fa-caret-down"></i>
            </RB.Button>
	    <span className="pull-right">
              <RB.Button
		 onClick={this.props.onRegenerate}
		 bsSize="sm">
		<i className="fa fa-refresh"/>
      	      </RB.Button>
	    </span>
	  </div>
	  <RB.ListGroup>
 	    {makeHypItems(this.props.hyps, this.props.models, this.props.onHypSelect, this.props.onHypDismiss)}
	  </RB.ListGroup>
	</div>
      );
    }
  }
}

export default Suggestions;
