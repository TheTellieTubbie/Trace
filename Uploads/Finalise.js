import React from 'react';

import Container from 'react-bootstrap/Container';
import Row from 'react-bootstrap/Row';
import Col from 'react-bootstrap/Col';

import psv from './PSV';
import Function from './Function';

class Finalise extends React.Component {
  constructor(props) {
    super(props);
    // Finals are expected to be an array of triplets (array of party, algorithms, knowledge)
    this.state = {
        finals : props.finals ? props.finals : []
      , messages : props.messages ? props.messages : []
    };
  }
  
  getFunctions = (statements) => {
    if (statements) {
      return statements
        .filter((e) => e.props.deterministic && e.props.rvalue.type === <Function />.type)
        .map((s) => 
          <assignment variable={s.props.lvalue.props.name}> 
            <application function={s.props.rvalue.props.name}>
              {s.props.rvalue.props.arguments.map((a) =>
                <argument
                  id={a.props.name}
//                   type=QUALCOSA
                >
                </argument> 
              )}
            </application> 
          </assignment>
        );
    } else {
      return "";
    }
  }
  getCorrectness = (statements) => {
      console.log(statements)
    if (typeof statements[0] !== 'undefined') {
      return(<argument id={statements[0].props.lvalue.props.name}></argument>);
    } else {
      return "";
    }
  }
  toPSV = () => {
    /*WARNING Type of variable within argument doesn't work 
        - Some variables do not have typesets?
            
      TODO -> Make type work on func
           -> Make Set work
           -> Make rvar work
    */
    var finalise = this.state.finals.map((pak) => {
      let party = pak[0];
      let algorithmBox = pak[1];
      
      return (
          <>
        <finalise
          entity={party.props.name}
          lastmessage={"m-" + (this.state.messages.length > 0
            ? this.state.messages[this.state.messages.length - 1].props.stage
            : "no-msg")}
        >
          {this.getFunctions(algorithmBox.props.statements)}
        </finalise>
        </>
      );
    });
    if(this.state.finals.length > 1 && typeof this.state.finals[0][1].props.statements[0] !== 'undefined' && typeof this.state.finals[1][1].props.statements[0] !== 'undefined'){ 
        var correctness = 
            <correctness>
                <application function="eq">
                    {this.getCorrectness(this.state.finals[0][1].props.statements)}
                    {this.getCorrectness(this.state.finals[1][1].props.statements)}
                </application>
            </correctness> }
    else{correctness = ""}
    return (
      <>{finalise}
      {<properties>
          {correctness}       
        </properties> 
    }</>
    );
  }
  
  render() {
    return (
      <Container className="finalise">
        <Row>
          {this.state.finals.map((e, i) => 
            <Col key={i}>{e[1]}</Col>
          )}
        </Row>
        <Row>
          {this.state.finals.map((e, i) => 
            <Col key={i}>{e[2]}</Col>
          )}
        </Row>
      </Container>
    );
  }
}

export default psv(Finalise);
