import React from 'react';
import ReactDom from 'react-dom';
import * as RB  from 'react-bootstrap';
import Slider from 'rc-slider';
import Utils from './Utils';


function makeButtons(models, onClick) {
  let buttons = [];
  for (var i=0; i<models.length; i++) {
    const model = models[i];
    const title = Utils.getInitials(model.modelName);
    const overlay = model.modelName ? model.modelName : model.path;

    const borderWidth = model.loaded ? "1.5px" : "0.5px";
    const {r, g, b} = model.color;
    const backgroundColor = `rgb(${r},${g},${b})`;

    buttons.push(
      <RB.OverlayTrigger
         key={i}
	 overlay={<RB.Tooltip id="tooltip">{overlay}</RB.Tooltip>}
	 placement="bottom">
        <RB.Button
	   bsStyle="primary"
	   style={{backgroundColor: backgroundColor,
		   borderColor: backgroundColor,
	           color: "black"}}
	   onClick={() => onClick(model.path)}>
	 {title}
        </RB.Button>
      </RB.OverlayTrigger>
    );
  }
  return buttons;
}


const noModelsButton = () => <RB.Button>No available models</RB.Button>;


class ButtonToolbar extends React.Component {
  render() {
    const {temperature, maxSeqLen, models} = this.props;
    return (
      <div className="generate-bar">
	<RB.Row>
	  <RB.Col md={7} sm={5}>
	    <RB.ButtonGroup style={{width: "200px", display: "inline-flex", margin: "7px 15px"}}>
	      <span>Creativiteit</span>
	      <Slider
		 defaultValue={temperature} min={0.05} max={1.0} step={0.05}
		 style={{width: "100%", margin: "3px 10px"}}
		 onChange={this.props.onTemperatureChange}
		 title="Creativiteit"/>
	      <RB.Label style={{padding:"4px 8px", width:"75px", margin: "0px 8px"}}>{temperature}</RB.Label>
	    </RB.ButtonGroup>
	    <RB.ButtonGroup style={{width: "200px", display: "inline-flex", margin: "7px 15px"}}>
	      <span>Lengte</span>
	      <Slider
		 defaultValue={maxSeqLen} min={10} max={200} step={5}
		 style={{width: "100%", margin: "3px 10px"}}
		 onChange={this.props.onSeqLenChange}
		 title="Lengte"/>
	      <RB.Label style={{padding:"4px 8px", width:"75px", margin: "0px 8px"}}>{maxSeqLen}</RB.Label>
	    </RB.ButtonGroup>
	  </RB.Col>
	  <RB.Col md={5} sm={7} className="pull-right">
	    <RB.ButtonGroup className="pull-right" style={{backgroundColor: "none"}}> 
              {(models.length > 0) ? makeButtons(models, this.props.onGenerate) : noModelsButton}
	    </RB.ButtonGroup>
	  </RB.Col>
	</RB.Row>
      </div>
    );
  }
};

export default ButtonToolbar;


