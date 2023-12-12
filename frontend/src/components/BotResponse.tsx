import * as React from 'react';
import Typography from '@mui/material/Typography';
import Title from './Title';

interface response{
    type: string
    content: string
}

export default function BotResponse(response:response) {
  return (
    <React.Fragment>
      <Title>{response.type} </Title>
      <Typography 
      component="p" variant="h6"
      style={{overflow: 'auto', fontSize: '12px' }}>
        {response.content}
      </Typography>
    </React.Fragment>
  );
}
