import React from 'react';
import ReactDOM from 'react-dom';
import * as RB from 'react-bootstrap';
import Utils from './Utils';
import { CSSTransitionGroup } from 'react-transition-group';


class HypItem extends React.Component {
  render() {
    const {hyp, backgroundColor, onHypSelect, onHypDismiss} = this.props;
    return (
      <RB.ListGroupItem
	 className="list-group-hover"
	 style={{backgroundColor: backgroundColor}}>
	<RB.Table style={{marginBottom: "0"}} responsive>
	  <tbody>
	    <tr>
	      <td>
		<RB.Button
		   style={{border: "none", padding: "0", background: "none"}}
		   onClick={(e) => onHypDismiss(hyp.generation_id)}>
                  <i className="fa fa-close fa-fw" style={{color:"#666666", fontSize: "20px"}}/>
		</RB.Button>
              </td>
              <td style={{padding:"0px 10px 0px 20px", width:"100%"}}>
		<p>{hyp.text}</p>
	      </td>
	      <td>
		<RB.Label className="pull-right">{hyp.score}</RB.Label>
	      </td>
	      <td>
		<RB.Button onClick={() => onHypSelect(hyp)} 
		  className="pull-right" 
		  style={{border: "none", padding: "0", background: "none"}}>
		  <i className="fa fa-check" style={{color:"#666666", fontSize: "20px"}}/>
		</RB.Button> 
	      </td>
            </tr>
          </tbody>
	</RB.Table>
      </RB.ListGroupItem>
    );
  }
};


function makeHypItems(hyps, models, onHypSelect, onHypDismiss) {
  let hypItems = [];
  for (var i=0; i<hyps.length; i++) {
    const hyp = hyps[i];
    const {r, g, b} = Utils.getModelData(models, hyp.model).color;
    hypItems.push(
      <HypItem
	 key={hyp.generation_id}
	 hyp={hyp}
	 backgroundColor={`rgba(${r},${g},${b}, 0.5)`}
	 onHypSelect={onHypSelect}
	 onHypDismiss={onHypDismiss}/>
    );
  }
  return hypItems;
}


class RegenerateButton extends React.Component {
  render() {
    let button;
    if (this.props.loadingHyps) {
      // show spinner
      button = (
	<RB.Button disabled style={{cursor: "default", padding:"4px 10px"}}>
	  <Utils.Spinner/>
	</RB.Button>
      );
    } else {
      // show refresh button
      button = (
	<RB.Button
	   onClick={this.props.onRegenerate}
	   bsSize="sm"
	   className="pull-right" >
	  <i className="fa fa-refresh"/>
      	</RB.Button>
      );
    }
    return button;
  }
}


class SuggestionList extends React.Component {
  componentDidUpdate() {
    ReactDOM.findDOMNode(this).scrollTop = 0;
  }

  render () {
    const {hyps, models, onHypSelect, onHypDismiss} = this.props;
    return (
      <RB.ListGroup>
	<CSSTransitionGroup
	   transitionName="dismiss"
	   transitionEnterTimeout={500}
	   transitionLeaveTimeout={150}>
 	  {makeHypItems(hyps, models, onHypSelect, onHypDismiss)}
	</CSSTransitionGroup>
      </RB.ListGroup>
    );
  }
}


class Suggestions extends React.Component {

  render() {
    const hasHyps = (this.props.hyps.length > 0) || this.props.loadingHyps || this.props.hasHadHyps;
    const collapsedClass = this.props.isCollapsed ? 'suggestions-panel-down' : 'suggestions-panel-up';
    const caretClass = this.props.isCollapsed ? 'fa fa-caret-up' : 'fa fa-caret-down';
    return (
      <div className={`panel panel-default suggestions-panel ${collapsedClass}`}
	   style={{visibility: hasHyps ? "visible" : "hidden"}}>
	<div className="panel-heading">
	  <RB.Row>
	    <RB.Col md={6} sm={4} xs={3}>
	      <RB.ButtonGroup>
		<RB.Button bsSize="sm" onClick={() => this.props.onCollapse()}>
		  <i className={caretClass}></i>
		</RB.Button>
		{(this.props.hyps.length > 0)
		  ?
		  <RB.Button disabled style={{cursor: "default", padding: "4px 10px"}}>
		      <span>{this.props.hyps.length}</span>
		    </RB.Button>
		    :
		    <span></span>
		    }
	      </RB.ButtonGroup>
	    </RB.Col>
	    <RB.Col md={6} sm={8} xs={9} className="pull-right">
	      <RB.ButtonGroup className="pull-right">
		<RB.Button
		   bsSize="sm"
		   style={{margin:"0 20px"}}
		   onClick={() => {this.props.resetHyps(); this.props.onCollapse();}}>
		  Clear All
		</RB.Button>
		<RegenerateButton
		   loadingHyps={this.props.loadingHyps}  
		   onRegenerate={this.props.onRegenerate}/> 
	      </RB.ButtonGroup>
	    </RB.Col>
	  </RB.Row>
	</div>
	<SuggestionList
	   hyps={this.props.hyps}
	   models={this.props.models}
	   onHypSelect={this.props.onHypSelect}
	   onHypDismiss={this.props.onHypDismiss}/>
      </div>
    );
  }
}

export default Suggestions;
