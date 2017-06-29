import React from 'react';
import ReactDOM from 'react-dom';
import * as RB from 'react-bootstrap';
import Utils from './Utils';
import ReactCSSTransitionGroup from 'react-addons-css-transition-group'; // ES6

class Suggestions extends React.Component {
  render() {
    const hasHyps = (this.props.hyps.length > 0);
    let hyps = [];
    for (var i=0; i<this.props.hyps.length; i++) {
      const hyp = this.props.hyps[i];
      // const {r, g, b} = Utils.getModelData(this.props.models, hyp.model).color;
      // const backgroundColor = `rgb(${r},${g},${b})`;
      // FOR TESTING
      const backgroundColor = "#FDCDAC";
      hyps.push(
	<RB.ListGroupItem
	   key={i}
	   className="list-group-hover"
	   onClick={() => this.props.onHypSelect(hyp)}
     style={{backgroundColor: backgroundColor}}
     >
    <RB.Table style={{marginBottom:"0"}} responsive>
      <tbody>
        <tr>
          <td>
            <RB.Button style={{border: "none", padding: "0", background: "none"}}>
              <i className="fa fa-close fa-fw" style={{fontSize:"large", color:"#666666"}} >
                </i></RB.Button>
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
    if (this.props.loadingHyps) {
      return <Utils.Spinner/>;
    } else {
      return (
	<div className="panel panel-default suggestions-panel" style={{visibility: hasHyps ? "visible" : "hidden"}}>
	  <div className="panel-heading">
          <RB.Button
          bsSize="medium"
// TODO ADD SLIDING ANIMATION
//          onClick={this.props.onRegenerate}
          >
            <i className="fa fa-caret-down"></i>
          </RB.Button>
	      <span className="pull-right">
          <RB.Button
            onClick={this.props.onRegenerate}
            bsSize="medium">
            <i className="fa fa-refresh"/>
      		</RB.Button>
	      </span>
	  </div>
	  <RB.ListGroup>
 					{hyps}
			</RB.ListGroup>
	</div>
      );
    }
  }
}

export default Suggestions;
