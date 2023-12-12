import * as React from 'react';
import Grid from '@mui/material/Grid';
import Toolbar from '@mui/material/Toolbar';
import Container from '@mui/material/Container';
import Paper from '@mui/material/Paper';
import BotResponse from './BotResponse';
import Misinformation from './Misinformation';
import HumanResponse from './HumanResponse';
import { useSelector, useDispatch } from 'react-redux'
import { RootState } from "../app/store";

interface response{
  type: string
  content: string
}

export default function Board() {

  const misinformation = useSelector((state:RootState) => state.misinformation)

  return (
    <React.Fragment>
      <Toolbar />
      <Container sx={{ mt: '4vh' }}>
        <Grid container spacing={2} sx={{height: '80vh'}}>
          {/* Misinformation */}
          <Grid item xs={12} >
            <Paper 
              sx={{ 
                p: 2, 
                display: 'flex', 
                flexDirection: 'column',
                height: '15vh',
                }}>
              <Misinformation content={misinformation.content} />
            </Paper>
          </Grid>
          {/* Positive Response */}
          <Grid item xs={6}>
            <Paper
              sx={{
                p: 2,
                display: 'flex',
                flexDirection: 'column',
                height: '35vh',
              }}
            >
              <BotResponse type={'Response 1'} content={misinformation.res_1} />
            </Paper>
          </Grid>
          {/* Negative Response */}
          <Grid item xs={6}>
            <Paper
              sx={{
                p: 2,
                display: 'flex',
                flexDirection: 'column',
                height: '35vh'
              }}
            >
              <BotResponse type={'Response 2'} content={misinformation.res_2} />
            </Paper>
          </Grid>
          {/* Researcher Response */}
          <Grid item xs={12}>
            <Paper 
              sx={{ 
                p: 2, 
                display: 'flex', 
                flexDirection: 'column',
                height: '30vh',
                }}>
              <HumanResponse />
            </Paper>
          </Grid>
        </Grid>
      </Container>
    </React.Fragment>
  );
}
