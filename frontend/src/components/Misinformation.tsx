import * as React from 'react';
import Typography from '@mui/material/Typography';
import Title from './Title';

interface misinformationCotent{
  content: string
}

export default function Misinformation(misinformation:misinformationCotent) {
  return (
    <React.Fragment>
      <Title>Detected Misinformation</Title>
      <Typography component="p" variant="h5"
        style={{overflow: 'auto', fontSize: '12px' }}> 
        {misinformation.content}
      </Typography>


    </React.Fragment>
  );
}

