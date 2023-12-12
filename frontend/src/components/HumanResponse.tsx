import * as React from 'react';
import { Divider, Grid, Button, TextField } from '@mui/material';
import { useSelector, useDispatch } from 'react-redux'
import { RootState } from "../app/store";
import { edit, quickEdit, clear, initialState } from '../app/slices/misInformation';
import { useSendResponseMutation } from '../app/slices/bot' 
import { reduce } from '../app/slices/messagesID'
import { useEffect } from 'react';

export default function HumanResponse() {

  const misinformation = useSelector((state:RootState) => state.misinformation)
  const dispatch = useDispatch()
  const [sendResponse, { isLoading, isError, isSuccess }] = useSendResponseMutation();

  useEffect(() => {
    if (isSuccess) {
      dispatch(reduce(misinformation.id))
      dispatch(clear())
    }
  }, [isSuccess]);

  const handleSend = () => {
    console.log("clicked")
    sendResponse(misinformation)
  }

  const handleEdit = (e: React.ChangeEvent<HTMLInputElement>) => {
    dispatch(edit(e.target.value));
  };

  const handleQuickEdit = (type:string) => {
    dispatch(quickEdit(type))
  }

  return (
    <React.Fragment>
      <Grid container spacing={2}>
        <Grid item xs={1.5} sx={{ display: 'flex', justifyContent: 'center' }}>
          <Button variant='outlined' onClick={() => handleQuickEdit('res_1')}>Response 1</Button>
        </Grid>
        <Grid item xs={1.5} sx={{ display: 'flex', justifyContent: 'center' }}>
          <Button variant='outlined' onClick={() => handleQuickEdit('res_2')}>Response 2</Button>
        </Grid>
        <Grid item xs={1} sx={{ display: 'flex', justifyContent: 'center' }}>
          <Button variant="outlined" onClick={() => handleQuickEdit('clear')}>Clear</Button>
        </Grid>
        <Grid item xs={7}>
        </Grid>
        <Grid item xs={1} sx={{ display: 'flex', justifyContent: 'center', right: '0' }}>
          <Button variant="outlined" onClick={handleSend} disabled={misinformation.id === initialState.id}>Send</Button>
        </Grid>
      </Grid>

      <Divider sx={{mt: '2vh', mb: '2vh'}}></Divider>
      
      <TextField
          id="response"
          label="Response"
          multiline
          rows={5}
          value={misinformation.final}
          onChange={handleEdit}
      >
        
      </TextField>
    </React.Fragment>
  );
}

