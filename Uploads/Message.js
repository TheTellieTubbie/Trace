import React from 'react';

import Row from 'react-bootstrap/Row';
import Col from 'react-bootstrap/Col';

import psv from './PSV';
import ModelBox from './ModelBox';
import EventBox from './EventBox';
import PreBox from './PreBox';
import PostBox from './PostBox';
import Party from './Party';
import Variable from './Variable';
import Function from './Function';
import Knowledge, { encapsulate, readConstants, readVariables } from './Knowledge';

class Message extends React.Component {
  constructor(props) {
    super(props);
    this.preRef = React.createRef();
    this.eventRef = React.createRef();
    this.postRef = React.createRef();
    
    this.state = {
        left : props.fromParty ? props.fromParty : <Party />
      , right : props.toParty ? props.toParty : <Party />
      , stage : props.stage ? props.stage : 1
      , knowledgeLeft : (props.direction === "send")
          ? props.knowledgeFrom
          : props.knowledgeTo
      , knowledgeRight : (props.direction === "send")
          ? props.knowledgeTo
          : props.knowledgeFrom
      , pre : undefined
      , event : undefined
      , post : undefined
    };
    
    this.state.pre = <PreBox stage={props.stage} ref={this.preRef} preprocess={(a, b) => this.augmentKnowledge(this, this.state.knowledgeLeft, a, b)} />;
    this.state.event = <EventBox direction={props.direction === "receive" ? "receive" : "send"} ref={this.eventRef} preprocess={(a, b) => this.augmentKnowledge(this, this.state.knowledgeRight, a, b)} />;
    this.state.post = <PostBox stage={props.stage} ref={this.postRef} preprocess={(a, b) => this.augmentKnowledge(this, this.state.knowledgeRight, a, b)} />;
  }
  
  // TODO: does not render the knowledge properly (if you add something later, it eventually will)
  augmentKnowledge = (msg, k, a, item) => {
    
    // Assignments (pre/post boxes)
    if (item.props.lvalue) {
      // TODO: Change the variable state
      k.props.elements.push(encapsulate(k, item.props.lvalue));
    }
    
    // Variables (event boxes)
    console.log("vars", item);
    if (item.props.name) {
      k.props.elements.push(encapsulate(k, item));
    }
    return item;
  }
  
  toPSV = () => {
    var lknowledge = "";
    var rknowledge = "";
    var pre = "";
    var event = "";
    var post = "";
//     var lvar ="";
//     var lconst ="";
//     var rvar ="";
//     var rconst ="";
    
    if (this.preRef && this.preRef.current) {
      pre = this.preRef.current.toPSV();
    }
    
    if (this.eventRef && this.eventRef.current) {
      /*
       * Since event is a dnd, it is decorated with
       * the dnd object (which contains it into "decoratedRef.current").
       */
      event = this.eventRef.current.decoratedRef.current.toPSV();
    }
    
    if (this.postRef && this.postRef.current) {
      post = this.postRef.current.toPSV();
    }
    var lconstants = readConstants(this.state.knowledgeLeft.props.elements, this.state.stage - 1);
    var lvariables = readVariables(this.state.knowledgeLeft.props.elements, this.state.stage - 1);
    var rconstants = readConstants(this.state.knowledgeLeft.props.elements, this.state.stage - 1);
    var rvariables = readVariables(this.state.knowledgeLeft.props.elements, this.state.stage - 1);
    if((lconstants && lconstants.length) || (lvariables && lvariables.length) )        
    {
        lknowledge =
        <knowledge entity={this.state.left.props.name}>
            {lconstants}
            {lvariables}
        </knowledge>;
    }
    else{
        lknowledge = "";
        
    }
    if((rconstants && rconstants.length) || (rvariables && rvariables.length) )        
    {
        rknowledge =
        <knowledge entity={this.state.right.props.name}>
            {rconstants}
            {rvariables}
        </knowledge>;
    }
    else{
        rknowledge = "";
        
    }    
    // TODO: this code is a copy/paste from eventbox
    var ev = this.eventRef.current.decoratedRef.current;
    let mirroredEvent = (!event) ? "" :
      <event type="receive">
        {ev.state.boxes.map((e) => <variable id={e.props.name}></variable>)}
      </event>;

    return (
      <message id={"m-" + this.state.stage} from={this.state.left.props.name} to={this.state.right.props.name}>
        {lknowledge}
        {rknowledge}
          {pre}
          {event}
        <channel></channel>
          {mirroredEvent}
          {post}
      </message>
    );
  }
  
  render() {
    var topLeft, topRight, bottomLeft, bottomRight, raiseClassLeft, raiseClassRight;
    
    if (this.state.event.props.direction === "send") {
      topLeft = [this.state.pre, this.state.knowledgeLeft];
      topRight = "";
      bottomRight = [this.state.post, this.state.knowledgeRight];
      bottomLeft = "";
      raiseClassLeft = "";
      raiseClassRight = " message-raise";
    } else {
      topLeft = "";
      topRight = [this.state.pre, this.state.knowledgeLeft];
      bottomRight = "";
      bottomLeft = [this.state.post, this.state.knowledgeRight];
      raiseClassLeft = " message-raise";
      raiseClassRight = "";
    }
    
    return (
      <div className="message">
        <Row>
          <Col className={"message-pre" + raiseClassLeft}>{topLeft}</Col>
          <Col className="message-event"></Col>
          <Col className={"message-post" + raiseClassRight}>{topRight}</Col>
        </Row>
        <Row>
          <Col className="message-pre"></Col>
          <Col className="message-event">{this.state.event}</Col>
          <Col className="message-post"></Col>
        </Row>
        <Row>
          <Col className={"message-pre" + raiseClassLeft}>{bottomLeft}</Col>
          <Col className="message-event"></Col>
          <Col className={"message-post" + raiseClassRight}>{bottomRight}</Col>
        </Row>
      </div>
    );
  }
}

export default psv(Message);
