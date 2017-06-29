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
    hypItems.push(
      <RB.ListGroupItem
	 key={hyp.generation_id}
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


class ButtonRight extends React.Component {
  render() {
    let buttonRight;
    if (this.props.loadingHyps) {
      // show spinner
      buttonRight = <Utils.Spinner/>;
    } else {
      // show refresh button
      buttonRight = (
	<RB.Button
	   onClick={this.props.onRegenerate}
	   bsSize="sm">
	  <i className="fa fa-refresh"/>
      	</RB.Button>
      );
    }
    return buttonRight;
  }
}


class Suggestions extends React.Component {
  render() {
    const hasHyps = (this.props.hyps.length > 0) || this.props.loadingHyps;
    const collapsedClass = this.props.isCollapsed ? 'suggestion-panel-down' : 'suggestion-panel-up';
    return (
      <div className={`panel panel-default suggestions-panel ${collapsedClass}`}
	   style={{visibility: hasHyps ? "visible" : "hidden"}}>
	<div className="panel-heading">
          <RB.Button bsSize="sm" onClick={() => this.props.onCollapse()}>
            <i className="fa fa-caret-down"></i>
          </RB.Button>
	  <span className="pull-right">
	    <ButtonRight loadingHyps={this.props.loadingHyps} onRegenerate={this.props.onRegenerate}/>
	  </span>
	</div>
	<RB.ListGroup>
	  <CSSTransitionGroup
	     transitionName="dismiss"
	     transitionEnterTimeout={500}
	     transitionLeaveTimeout={300}>
 	    {makeHypItems(this.props.hyps, this.props.models, this.props.onHypSelect, this.props.onHypDismiss)}
	  </CSSTransitionGroup>
	</RB.ListGroup>
      </div>
    );
  }
}

export default Suggestions;
