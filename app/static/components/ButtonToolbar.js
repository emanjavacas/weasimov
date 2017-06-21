import React from 'react';
import ReactDom from 'react-dom';
import * as RB  from 'react-bootstrap';
import Slider, { createSliderWithTooltip } from 'rc-slider';


const SliderWithTooltip = createSliderWithTooltip(Slider);

class ButtonToolbar extends React.Component {
  constructor(props) {
    super(props);
    this.state = {
      models: []
    };
    this.updateModels = this.updateModels.bind(this);
    this.loadModel = this.loadModel.bind(this);
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

  loadModel(model) {
    if (model.loaded) {
      this.props.onModelSelect(model.path);
    } else {
      $.ajax({
	contentType: 'application/json;charset=UTF-8',
	url: 'load_model',
	type: 'POST',
	data: JSON.stringify({'model_name': model.path}),
	dataType: 'json',
	success: (response) => {
	  this.props.onModelSelect(response.model.path);
	  this.setState(
	    {models: this.updateModels(response.model.path, response.model.loaded)});
	},
	error: (error) =>  console.log(error)
      });
    }
  }
  
  render() {
    const {models} = this.state;
    const {temperature, currentModel} = this.props;
    // create dropdown items for models
    const hasModels = (models.length > 0);
    let dropdownModels = null;
    if (hasModels) {
      dropdownModels = [];
      for (var i=0; i<models.length; i++) {
	const model = models[i];
	dropdownModels.push(
	  <RB.MenuItem
	     style={{"backgroundColor": model.loaded ? "darkseagreen" : "white"}}
	     eventKey={i}
	     key={i}
	     onSelect={(key, obj) => this.loadModel(models[key])}>
	    {model.path}
	  </RB.MenuItem>
	);
      }
    } else {
      dropdownModels = <RB.MenuItem>No available models</RB.MenuItem>;
    }
    // create dropdown items for size
    const dropdownSizes = [];
    for (var i=0; i<this.props.sizes.length; i++) {
      const size = this.props.sizes[i];
      dropdownSizes.push(
	<RB.MenuItem
	   style={{"backgroundColor": (size === this.props.maxSeqLen) ? "darkseagreen" : "white"}}
	   eventKey={i}
	   key={i}
	   onSelect={(key, obj) => this.props.onSeqLenChange(this.props.sizes[key])}>
            {size}
	</RB.MenuItem>
      );
    }
    const tempStr = (temperature.toString().length === 3) ?
	    temperature.toString() + '0' :
	    temperature;
    return (
      <RB.Form horizontal>
	<RB.FormGroup>
	  <RB.Col componentClass={RB.ControlLabel} md={3} sm={4}>
	    Creativity <RB.Label bsStyle="default">{tempStr}</RB.Label>
	  </RB.Col>
	  <RB.Col md={9} sm={8}>
	    <SliderWithTooltip
      	       defaultValue={temperature} min={0.1} max={1.0} step={0.05}
      	       style={{width: "100%", marginTop: "10px"}}
      	       onChange={this.props.onSliderChange}
      	       tipProps={{ overlayClassName: 'foo' }}/>
	  </RB.Col>
	</RB.FormGroup>
	<RB.FormGroup>
	  <RB.Col componentClass={RB.ControlLabel} md={3} sm={4}>
	    Model
	  </RB.Col>
	  <RB.Col md={9} sm={8}>
      	    <RB.DropdownButton
      	       title={currentModel || "Model selection"}
      	       id="dropdown-model">
      	      {dropdownModels}
      	    </RB.DropdownButton>
	  </RB.Col>
	</RB.FormGroup>
	<RB.FormGroup>
	  <RB.Col componentClass={RB.ControlLabel} md={3} sm={4}>
	    Size
	  </RB.Col>
	  <RB.Col md={9} sm={8}>
      	    <RB.DropdownButton
      	       title={this.props.maxSeqLen + " characters"}
      	       id="dropdown-size">
      	      {dropdownSizes}
      	    </RB.DropdownButton>
	  </RB.Col>
	</RB.FormGroup>
	<RB.FormGroup>
	  <RB.Col smOffset={3} sm={9}>
	    <RB.Button
      	       bsStyle="primary"
      	       onClick={this.props.onGenerate}>
      	      Generate
      	    </RB.Button>
	  </RB.Col>
	</RB.FormGroup>
      </RB.Form>
    );
  }
};

export default ButtonToolbar;
