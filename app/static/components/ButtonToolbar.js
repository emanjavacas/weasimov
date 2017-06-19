import React from 'react';
import ReactDom from 'react-dom';
import * as RB  from 'react-bootstrap';
import Slider, { createSliderWithTooltip } from 'rc-slider';


const SliderWithTooltip = createSliderWithTooltip(Slider);

const ModelItem = (props) => {
  return (
    <RB.MenuItem
       style={{"backgroundColor": props.loaded ? "darkseagreen" : "white"}}
       eventKey={props.idx}
       onClick={() => props.onClick(props.model, props.loaded)}>
      {props.model.path}
    </RB.MenuItem>
  );
};

class ButtonToolbar extends React.Component {
  constructor(props) {
    super(props);
    this.state = {
      temperature: 0.35,
      currentModel: null,
      models: []
    };
    this.loadModel = this.loadModel.bind(this);
    this.updateModels = this.updateModels.bind(this);
    this.updateTemperature = this.updateTemperature.bind(this);
  }

  componentDidMount() {
    $.ajax({
      contentType: 'application/json;charset=UTF-8',
      url: 'models',
      type: 'GET',
      dataType: 'json',
      success: (response) => this.setState({models: response.models}),
      error: (error) =>  console.log(error)
    });
  }

  updateModels(path, loaded) {
    if (!loaded) {
      return this.state.models;
    } else {
      return this.state.models.map(
	(model) => (model.path === path) ? {path: model.path, loaded: loaded} : model);
    }
  };

  loadModel(model, loaded) {
    const newModels = this.updateModels(model.path, !loaded);
    console.log(newModels);
    $.ajax({
      contentType: 'application/json;charset=UTF-8',
      url: 'load_model',
      type: 'POST',
      data: JSON.stringify({'model_name': model.path}),
      dataType: 'json',
      success: (response) => this.setState(
	{currentModel: model.path, models: newModels}),
      error: (error) =>  console.log(error)
    });
  }

  updateTemperature(value) {
    this.setState({temperature: value});
  }
  
  render() {
    const hasModels = (this.state.models.length > 0);
    let dropdownItems = null;
    if (hasModels) {
      dropdownItems = this.state.models.map((model, idx) => {
	return (<ModelItem key={idx} model={model} loaded={model.loaded} idx={idx} onClick={this.loadModel}/>);
      });
    } else {
      dropdownItems = <RB.MenuItem>No available models</RB.MenuItem>;
    }
    return (
      <div className="container-fluid">
        <div className="col-md-6">
	  <SliderWithTooltip
	     defaultValue={this.state.temperature} min={0.1} max={1.0} step={0.05}
	     style={{width: "100%"}}
	     onChange={this.updateTemperature}
	     tipProps={{ overlayClassName: 'foo' }}/>
	  <span style={{fontWeight: "bold"}} className="pull-right">
	    Creativity <RB.Label bsStyle="default">{this.state.temperature}</RB.Label>
	  </span>
	</div>
	<div className="col-md-6">
	  <RB.ButtonGroup className="pull-right">
	    <RB.DropdownButton
	       title={this.state.currentModel || "Model selection"}
	       id="dropdown">
	      {dropdownItems}
	    </RB.DropdownButton>
	    <RB.Button bsStyle="primary">Generate</RB.Button>
	  </RB.ButtonGroup>
	</div>
      </div>
    );
  }
};

export default ButtonToolbar;



