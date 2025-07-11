import React from 'react';
import * as jsx from '../javascript-extras.js';
import MathJax from 'react-mathjax';
import { DropTarget } from 'react-dnd';

import psv from './PSV';
import ModelBox, { DropHandler } from './ModelBox';
import KnowledgeElement from './KnowledgeElement';
import Tool from './Tool';
import Variable from './Variable';
import Function from './Function';

import { FontAwesomeIcon } from '@fortawesome/react-fontawesome';
import { faBookOpen } from '@fortawesome/free-solid-svg-icons';
import { faCircle } from '@fortawesome/free-regular-svg-icons';

import Popover from 'react-bootstrap/Popover';
import OverlayTrigger from 'react-bootstrap/OverlayTrigger';
import ListGroup from 'react-bootstrap/ListGroup';
import Button from 'react-bootstrap/Button';
  
export const readConstants = (knowledgeElements, stage) => {
  return knowledgeElements
    .filter((ke) => ke.props.stage <= stage && ke.props.content.type === <Function />.type) // Strenghten to arity 0
    .map((x) => <variable id={x.props.content.props.name} type="constant"></variable>);
}

export const readVariables = (knowledgeElements, stage) => {
  return knowledgeElements
    .filter((ke) => ke.props.stage <= stage && ke.props.content.type === <Variable />.type)
    .map((x) => <variable id={x.props.content.props.name}></variable>)
}

class Knowledge extends ModelBox {
  constructor(props) {
    super(props);
    this.state = {
        owner : props.owner ? props.owner : undefined
      , boxes : props.elements ? props.elements : []
      , stage : props.stage ? props.stage : 0
      , mumbleView : (props.mumbleView === true) ? true : false
      , readonly : (props.readonly === false) ? false : true
      , preprocess : encapsulate
    };
  }
  
  getKnowledge = () => {
    return (this.state.stage > -1)
      ? this.state.boxes.filter((k) =>
          k.props.stage <= this.state.stage
        )
      : this.state.boxes;
  }
  
  toPSV = () => {
    var knowledge = this.getKnowledge();
    var constants = readConstants(this.state.boxes, this.state.stage);
    var variables = readVariables(this.state.boxes, this.state.stage);
    if((constants && constants.length) || (variables && variables.length) )        
    {
        return (
        <knowledge entity={this.state.owner}>
            {constants}
            {variables}
        </knowledge>
        );
    }
    else{
        return("");
        
    }
  }
  render() {
    const { isOver, canDrop, connectDropTarget } = this.props;
    
    const emptyClass = (this.state.boxes.length === 0) ? "knowledge-empty" : "";
    
    const dragClass = (isOver && canDrop)
      ? "drag-over"
      : (canDrop && !this.state.readonly
        ? "drag-accepting"
        : ""
      );
      
    const className = emptyClass + (this.props.className ? this.props.className : "") + " " + dragClass;
    
    const mumbleBubbles = (this.state.mumbleView)
      ? <span className="knowledge-button-mumble"><FontAwesomeIcon icon={faCircle} /><FontAwesomeIcon icon={faCircle} /></span>
      : "";
    const mumbleClass = (this.state.mumbleView)
      ? "knowledge-btn-mumble"
      : "";
      
    const knowledge = this.getKnowledge();
    const emptyMessage = (knowledge.length >  0) ? "" : "you know nothing";
    
    const popover = (
      <Popover id="popover-basic" className="knowledge shadow-lg">
        <Popover.Title as="h3">Knowledge</Popover.Title>
        <Popover.Content>
          {emptyMessage}
          <ListGroup variant="flush">
          {knowledge.map((k) =>
            <ListGroup.Item>{k}</ListGroup.Item>
          )}
          </ListGroup>
        </Popover.Content>
      </Popover>
    );
    
    var result = (
      <div className=" knowledge-buttons">
        <OverlayTrigger
          trigger="click"
          placement="right"
          overlay={popover}
        >
          <Button className={className + " knowledge-button " + mumbleClass} variant="outline-info" size="sm"><FontAwesomeIcon icon={faBookOpen} /></Button>
        </OverlayTrigger>
        {mumbleBubbles}
      </div>
    );
    
    return (this.state.readonly)
      ? result
      : connectDropTarget(result);
  }
}

/**
 * Drop handling 
 */
const acceptCriteria = [
    (o) => (o.type === <Tool />.type && o.props.object.type === <Variable />.type)
  , (o) => (o.type === <Tool />.type && o.props.object.type === <Function />.type && o.props.object.props.arity === 0)
];

export const encapsulate = (parent, item) => {
  var state = parent.state ? parent.state : parent.props;
  return <KnowledgeElement content={item} stage={state.stage} />;
};

export default DropTarget('Tool', DropHandler.generateEvents(acceptCriteria), DropHandler.eventCollector)(psv(Knowledge))
