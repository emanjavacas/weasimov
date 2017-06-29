import React from 'react';
import ReactDOM from 'react-dom';
import * as RB from 'react-bootstrap';
import Utils from './Utils';
import { CSSTransitionGroup } from 'react-transition-group';


function makeHypItems(hyps, models, onHypSelect, onHypDismiss) {
  let hypItems = [];
  for (var i=0; i<hyps.length; i++) {
    const hyp = hyps[i];
    const key = i;
    const {r, g, b} = Utils.getModelData(models, hyp.model).color;
    const backgroundColor = `rgba(${r},${g},${b}, 0.5)`;
    hypItems.push(
      <RB.ListGroupItem
	 key={key}
	 className="list-group-hover"
         style={{backgroundColor: backgroundColor}}
	>
        <RB.Table style={{marginBottom:"0"}} responsive>
	  <tbody>
	    <tr>
	      <td>
		<RB.Button
		   style={{border: "none", padding: "0", background: "none"}}
		   onClick={(e) => {e.stopPropagation(); onHypDismiss(key);}}>
		  <i className="fa fa-close fa-fw" 
			style={{color:"#666666", fontSize: "20px"}}></i>
		</RB.Button>
	      </td>
	      <td style={{padding:"0px 10px 0px 20px"}}>
		{hyp.text}
	      </td>
	      <td>
		<RB.Label className="pull-right">{hyp.score}</RB.Label>
	      </td>
				<td>
					<RB.Button onClick={() => onHypSelect(hyp)} 
						className="pull-right" 
						style={{border: "none", padding: "0", background: "none"}}>
						<i className="fa fa-check" style={{fontSize: "20px"}}></i>
					</RB.Button> 
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
}

export default Suggestions;
